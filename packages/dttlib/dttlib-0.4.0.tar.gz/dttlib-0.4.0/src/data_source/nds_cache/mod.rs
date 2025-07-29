mod gap_handler;

use std::collections::{HashMap, HashSet};
use std::ops::Range;
use tokio::sync::mpsc;
use std::fmt::Display;
use std::sync::{OnceLock};
use crate::data_source::{ChannelQuery, DataBlock, DataBlockReceiver, DataBlockSender, DataSource, DataSourceFeatures, DataSourceRef};
use crate::errors::DTTError;
use crate::params::channel_params::channel::Channel;
use crate::run_context::RunContext;
use ligo_hires_gps_time::{PipDuration, PipInstant};
use nds_cache_rs::{
    init,
    CacheHandle,    
};
use super::buffer::Buffer;
#[cfg(feature = "python")]
use pyo3::{
    pyclass,
    pymethods,
};
#[cfg(feature = "python")]
use pyo3_stub_gen::{
  derive::{
      gen_stub_pyclass, gen_stub_pymethods, gen_stub_pyclass_enum,
  }
};
use tokio_util::sync::CancellationToken;
#[cfg(not(feature = "python"))]
use dtt_macros::new;
use crate::scope_view::ScopeView;
use crate::user::ResponseToUser;

#[derive(Clone, Copy, PartialEq)]
#[cfg_attr(feature = "python", gen_stub_pyclass_enum)]
#[cfg_attr(feature = "python",pyclass(frozen, eq))]
pub enum DataFlow {
    /// Data is sent repeatedly as
    /// more of the request is filled in.
    ///
    /// Each response gives all the data available.
    ///
    /// This is how NDScope expects data.
    Unordered,

    /// Data is returned from the earliest time stamp to the latest.
    /// Data is returned only once.
    /// This is how DTT expects data.
    Ordered,
}

impl Display for DataFlow {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            DataFlow::Unordered => write!(f, "Unordered"),
            DataFlow::Ordered => write!(f, "Ordered"),
        }
    }
}

/// The global cache handle used by all cache datasource objects
static cache_handle:OnceLock<CacheHandle> = OnceLock::new();

/// Data source that gets all its data directly from an NDS2 server (no local caching).
#[derive(Clone)]
#[cfg_attr(feature = "python",gen_stub_pyclass)]
#[cfg_attr(feature = "python",pyclass(frozen))]
pub struct NDS2Cache {
    /// default path to store cache when saving
    _default_file_path: String,

    size_bytes: usize,
}

/// How far ahead is "run forever"
const INDEFINITE_FUTURE_SEC: i64 = 366 * 24 * 60 * 60;

impl DataSource for NDS2Cache {
    fn stream_data(&self, rc: Box<RunContext>, channels: &[Channel], start_pip: PipInstant,
                   end_pip: Option<PipInstant>) -> Result<DataBlockReceiver, DTTError> {

        let online = end_pip.is_none();

        let calc_end_pip = match end_pip {
            Some(t) => t,
            None => start_pip + PipDuration::from_sec(INDEFINITE_FUTURE_SEC)
        };

        let interval: Range<PipInstant> = Range {
            start: start_pip,
            end: calc_end_pip,
        };

        let (db_tx, db_rx) = mpsc::channel(4);

        let new_chan_names = channels.iter().map(|c| c.name.clone()).collect();

        let handle = tokio::runtime::Handle::current();
        let _guard = handle.enter();
        futures::executor::block_on(
                self.clone().ordered_stream_loop(rc, new_chan_names, interval, db_tx, online)
        )?;

        Ok(db_rx)
    }

    fn start_scope_data(&self, rc: Box<RunContext>, view: & mut ScopeView) -> Result<DataBlockReceiver, DTTError> {

        let (db_tx, db_rx) = mpsc::channel(1);

        view.block_tx = Some(db_tx.clone());

        view.data_task_cancel_token = Some(CancellationToken::new());

        // the following two lines and the future::executor::block_on
        // on the third line are needed to call an async function
        // from within an async context from a non-async function.
        let handle = tokio::runtime::Handle::current();
        let _guard = handle.enter();
        futures::executor::block_on(self.clone().scope_view_stream_loop(rc, view))?;

        Ok(db_rx)
    }

    fn update_scope_data(&self, rc: Box<RunContext>, view: &mut ScopeView) -> Result<(), DTTError> {

        if let Some(tx) = &view.span_update_tx {
            if view.span.online {
                return tx.send(view.span.span_pip).map_err(|e| e.into());
            }
        }

        view.reset_count += 1;

        if let Some(c) = &view.data_task_cancel_token {
            c.cancel();
        }
        view.data_task_cancel_token = Some(CancellationToken::new());

        // the following two lines and the future::executor::block_on
        // on the third line are needed to call an async function
        // from within an async context from a non-async function.
        let handle = tokio::runtime::Handle::current();
        let _guard = handle.enter();
        futures::executor::block_on(self.clone().scope_view_stream_loop(rc, view))?;

        Ok(())
    }

    fn capabilities(&self) -> HashSet<DataSourceFeatures> {
        HashSet::from([DataSourceFeatures::LiveStream, DataSourceFeatures::Stream, DataSourceFeatures::QueryChannels])
    }

    fn as_ref(&self) -> DataSourceRef {
        self.clone().into()
    }

    fn find_channels(&self, rc: Box<RunContext>, query: &ChannelQuery) -> Result<(), DTTError> {
        let handle = tokio::runtime::Handle::current();
        let new_self = self.clone();
        let cloned_query = query.clone();
        handle.spawn(new_self.find_channels_blocking(rc, cloned_query));
        Ok(())
    }
}

async fn wrap_buffers(mut rx: tokio::sync::mpsc::Receiver<Vec<nds_cache_rs::buffer::Buffer>>) -> tokio::sync::mpsc::Receiver<Vec<Buffer>> {
    let (buf_tx, buf_rx) = tokio::sync::mpsc::channel(1);

    tokio::spawn(async move {
        loop {
            let buffers = match rx.recv().await {
                Some(b) => b.into_iter().map(|x|x.into()).collect(),
                None => break,
            };
            if let Err(_) = buf_tx.send(buffers).await {
                break;
            }
        }
    });

    buf_rx
}

impl NDS2Cache {

    /// For DTT stream.  All data must be consumed one-time only, and in order.
    /// The stream cannot drop any data from the cache.
    async fn ordered_stream_loop(self, rc: Box<RunContext>, channel_names: Vec<String>, interval: Range<PipInstant>,
                   data_block_tx: DataBlockSender, online: bool)
        -> Result<(), DTTError>
    {

        let cache = self.initialize_cache().await?;

        let mut data_rx = if online {
            cache.get_live(channel_names).await
        } else {
            cache.get_past_ordered(interval,  channel_names, ).await
        };

        let found_all = true;

        //let mut count: u64 = 0;

        tokio::spawn(
        async move {
            'main: loop {

//                println!("Ordered: {}: cache data len = {}", count, data_rx.len());

                let rx = data_rx.recv().await;

                let buffs = match rx {
                    None => {
                        break 'main
                    },
                    Some(b) => {
                        match b {
                            Ok(x) => x.into_iter().map(|b|b.into()).collect(),
                            Err(e) => {
                                rc.user_messages.error(format!("Error reading data from cache: {}", e));
                                continue 'main;
                            }
                        }
                    },
                };

                //count += 1;

                if let Err(e) = send_block(buffs, &data_block_tx).await {
                    match e {
                        DTTError::TokioMPSCSend(_) => {break 'main}
                        e => {
                            rc.user_messages.error(format!("Error sending data to analysis: {}", e));
                        }
                    }
                }

            }

            if found_all {
                rc.user_messages.clear_message("MissingCacheChannel");
            }
        });

        Ok(())
    }


    /// initialize cache if need be
    async fn initialize_cache(&self) -> Result<&CacheHandle, DTTError> {
        if cache_handle.get().is_none() {
            let size = self.size_bytes;

            let cache = init(size).await?;

            cache_handle.get_or_init(
                move || {
                    cache
                }
            );
        }
        Ok(cache_handle.get().unwrap())
    }

    /// transform from nds_cache_rs buffers to dttlib buffers


    /// Produce a watch channel that always has the latest
    /// result from the cache
    async fn start_scope_view_get_latest(self, rc: Box<RunContext>, view: &mut ScopeView)
            -> Result<mpsc::Receiver<Vec<Buffer>>, DTTError>
    {
        let cache = self.initialize_cache().await?;

        let start_pip = view.span.start_pip;
        let end_pip = view.span.end_pip();

        let interval: Range<PipInstant> = start_pip..end_pip;
            // PipInstant::from_gpst_sec(start_pip.to_gpst_sec())
            //     ..
            // PipInstant::from_gpst_sec(end_pip.to_gpst_sec()+1);

        let channel_names = view.set.to_resolved_channel_names();

        let (result_watch_tx, result_watch_rx_cache) = mpsc::channel(1);

        // transform output into wrapped buffer
        let result_watch_rx_orig = wrap_buffers(result_watch_rx_cache).await;

        let (span_update_tx, mut data_rx, result_watch_rx) = if view.span.online {
                let (d_tx, d_rx) =
                    cache.get_live_with_window_unordered(end_pip - start_pip, channel_names ).await;
                (Some(d_tx), d_rx, result_watch_rx_orig)
        } else {
            println!("{}.{}: Getting past scope data in {} - {} for {}",
                     view.id, view.reset_count,
                     interval.start.to_gpst_seconds(),
                     interval.end.to_gpst_seconds(), channel_names.join(", "));
                     
             (None, 
                cache.get_past_unordered(interval, channel_names).await,
                gap_handler::setup_gap_handler(rc.clone(), result_watch_rx_orig).await,
            )
        };

        view.span_update_tx = span_update_tx;

        

        let id = view.id;
        let reset_count = view.reset_count;
        let cancel_token = match &view.data_task_cancel_token {
            Some(s) => s.clone(),
            None => return Err(DTTError::MissingDataStreamError("Cancel token missing for scope view data stream".into())),
        };


        tokio::spawn(async move {
            let mut count: u64 = 0;
            let mut results = Vec::with_capacity(100);

            'main: loop {
                // println!("{}.{}: {}: cache data len = {}", id, reset_count, count, data_rx.len());

                let buffs = tokio::select! {
                    _ = cancel_token.cancelled() => {
                        println!("{}.{}: cancelled", id, reset_count);
                        break 'main;
                    },
                    x = data_rx.recv_many(&mut results, 100) =>  {
                        if 0 == x {
                            //println!("{}.{}: got 0 results from cache", id, reset_count);
                            break 'main
                        }
                        else {
                            //println!("{}.{}: got {} results from cache", id, reset_count, x);
                            let mut last_good = x;
                            for (i,r) in results[0..x].iter().enumerate() {
                                match r {
                                    Ok(_) => {
                                        last_good = i;
                                    }
                                    Err(e) => {
                                        rc.user_messages.error(format!("Error reading data from cache: {}", e));
                                    }
                                }
                            }
                            if last_good < x {
                                results.remove(last_good).unwrap()
                            } else {
                                continue 'main;
                            }
                        }
                    }
                };

                count += 1;

                if result_watch_tx.send(buffs).await.is_err() {
                    break 'main;
                }
            }
        });

        Ok(result_watch_rx)

    }

    /// Unordered stream loop only sends the latest data
    /// It keeps a weak reference to the data block tx and will close if the reference disappears
    async fn scope_view_stream_loop(self, rc: Box<RunContext>, view: &mut ScopeView) -> Result<(), DTTError>
    {
        let mut weak_block_tx = match &view.block_tx {
            Some(s) => s.downgrade(),
            None => return Err(DTTError::MissingDataStreamError("A block channel is missing from scope view.  Cannot create a data stream.".into())),
        };

        let found_all = true;

        let mut results_watch_rx = self.start_scope_view_get_latest(rc.clone(), view).await?;

        let span_update_rx = view.span_update_tx.as_ref().map(|s| s.subscribe());

        tokio::spawn(
            async move {
                // track end points per-channel, only sending blocks with end points >= the latest end points
                let mut latest_ends: HashMap<String, PipInstant> = HashMap::new();
                'main: loop {

                    //println!("waiting next buffer");
                    let buffs = match results_watch_rx.recv().await {
                        Some(b) => b,
                        None => {
                            break 'main
                        },
                    };

                    let dblock_tx = match weak_block_tx.upgrade() {
                        Some(x) => x,
                        None => {
                            // External ownership of block_tx has been dropped
                            // and the channel is closed
                            break 'main;
                        }
                    };

                    // // re-set the latest record if the span changes
                    // if let Some(srx) = span_update_rx.as_mut() {
                    //     if srx.has_changed().unwrap_or(false) {
                    //         println!("Span changed");
                    //         srx.borrow_and_update();
                    //         latest_ends.clear();
                    //     }
                    // }

                    if let Err(e) = send_latest_block(buffs, &dblock_tx, &mut latest_ends).await {
                        match e {
                            DTTError::TokioMPSCSend(_) => {break 'main}
                            e => {
                                rc.user_messages.error(format!("Error sending data to analysis: {}", e));
                            }
                        }
                    }

                    weak_block_tx = dblock_tx.downgrade();
                }

                if found_all {
                    rc.user_messages.clear_message("MissingCacheChannel");
                }
            });

        drop(span_update_rx);

        Ok(())
    }

    /// block on find channels, sending results to the user app
    /// when received
    async fn find_channels_blocking(self, rc: Box<RunContext>, query: ChannelQuery) {
        let handle = match self.initialize_cache().await {
            Ok(h) => h,
            Err(_) => {
                rc.user_messages.error("Failed to open the interface to the local cache to request channels.");
                return;
            }
        };
        let c = match handle.find_channels(&(query.into())) {
            Ok(c) => c,
            Err(e) => {
                rc.user_messages.error(format!("Error finding channels: {}", e));
                return;
            }
        };
        let channels = c.into_iter().filter_map(
            |c| {
                match c.try_into() {
                    Ok(c) => Some(c),
                    Err(e) => {
                        rc.user_messages.error(format!("Error converting channel: {}", e));
                        None
                    }
                }
            }
        ).collect();
        let rc2 = rc.clone();
        rc.output_handle.send(rc2, ResponseToUser::ChannelQueryResult {channels,}).unwrap();
    }
}

async fn send_latest_block(buffs: Vec<Buffer>, data_block_tx: &mpsc::Sender<DataBlock>, latest_ends: &mut HashMap<String, PipInstant>)
                    -> Result<(), DTTError>
{
    //println!("sending blocks");
    let mut block: HashMap<Channel, Vec<Buffer>> = HashMap::new();
    for buff in buffs {
        //println!("sending block @ {} for {}", buff.start().to_gpst_seconds(), buff.channel().name());
        let cname = buff.channel().name();

        if let Some(e) = latest_ends.get(cname) {
            if buff.end() < *e {
                continue;
            }
        }
        
        latest_ends.insert(cname.clone(), buff.end());

        let c1 = (&buff).try_into()?;

        match block.get_mut(&c1) {
            Some(v) => v.push(buff),
            None => { block.insert(c1, vec![buff, ]); },
        }
    }

    Ok(data_block_tx.send(block).await?)
}

async fn send_block(buffs: Vec<Buffer>, data_block_tx: &mpsc::Sender<DataBlock>)
                           -> Result<(), DTTError>
{
    let mut block: HashMap<Channel, Vec<Buffer>> = HashMap::new();
    for buff in buffs {
        let c1 = (&buff).try_into()?;

        match block.get_mut(&c1) {
            Some(v) => v.push(buff),
            None => { block.insert(c1, vec![buff, ]); },
        }
    }

    Ok(data_block_tx.send(block).await?)
}

#[cfg_attr(feature = "python", gen_stub_pymethods)]
#[cfg_attr(feature = "python", pymethods)]
impl NDS2Cache
{
    #[new]
    pub fn new(
        size_bytes: usize,
        default_file_path: String, ) -> Self
    {

        Self {
            _default_file_path: default_file_path,
            size_bytes,
        }
    }

    pub fn as_ref(&self) -> DataSourceRef {
        self.clone().into()
    }
}

