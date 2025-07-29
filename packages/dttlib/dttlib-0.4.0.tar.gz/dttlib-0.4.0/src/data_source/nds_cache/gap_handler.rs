//! Fill in gaps in nds_cache data streams
use crate::data_source::{
    buffer::{Buffer, },
};
use pipelines::complex::c64;
use core::f32;
use std::{collections::HashMap, i16, iter};

use crate::run_context::RunContext;

/// take a channel 
pub (super) async fn setup_gap_handler(rc: Box<RunContext>, mut input: tokio::sync::mpsc::Receiver<Vec<Buffer>>) -> tokio::sync::mpsc::Receiver<Vec<Buffer>> {
    let (output_tx, output_rx) = tokio::sync::mpsc::channel(1);

    tokio::spawn(async move {
        loop {
            tokio::select!{
                x = input.recv() => {
                    match x {
                        Some(bufs) => {
                            let mut by_channel: HashMap<String, Vec<Buffer>> = HashMap::new();

                            // collect buffers by channel name
                            for buf in bufs.into_iter() {
                                let key = buf.channel().name().clone();
                                if let Some(v) = by_channel.get_mut(&key) {
                                    v.push(buf);
                                } else {
                                    by_channel.insert(key, vec![buf]);
                                }                                
                            }

                            let mut out_buffers = Vec::with_capacity(by_channel.len());
                            // process any channels that have more than one buffer.
                            for mut buffs in by_channel.into_values() {
                                if buffs.len() == 1 {
                                    out_buffers.push(buffs.remove(0));
                                } else {
                                    out_buffers.push(handle_gaps(&rc, buffs));
                                }
                            }
                            if let Err(_) = output_tx.send(out_buffers).await {
                                break;
                            }
                        },
                        None => break,
                    }
                }
            }
        }
    });

    output_rx
}


/// buffers are all assumed to be of the same channel and non-overlapping
/// return a single buffer with gaps between buffers filled in with an appropriate value
fn handle_gaps(_rc: &Box<RunContext>, mut buffers: Vec<Buffer>) -> Buffer {
    buffers.sort();
    let mut first = buffers.remove(0);
    let period = first.period();
    let mut total_gap_size = 0;
    for buffer in buffers {
        let end_0 = first.end();
        let start_1 = buffer.start();
        let gap_size = ((start_1 - end_0) / period) as usize;
        total_gap_size += gap_size;
        match (&mut first.cache_buffer, buffer.cache_buffer) {
            (nds_cache_rs::buffer::Buffer::Int16(ts1), nds_cache_rs::buffer::Buffer::Int16(ts2))  => {
                ts1.data_mut().extend(iter::repeat(i16::MAX).take(gap_size));
                ts1.data_mut().extend(ts2.data().iter());
            },
            (nds_cache_rs::buffer::Buffer::Int32(ts1), nds_cache_rs::buffer::Buffer::Int32(ts2))  => {
                ts1.data_mut().extend(iter::repeat(i32::MAX).take(gap_size));
                ts1.data_mut().extend(ts2.data().iter());
            },
            (nds_cache_rs::buffer::Buffer::Int64(ts1), nds_cache_rs::buffer::Buffer::Int64(ts2))  => {
                ts1.data_mut().extend(iter::repeat(i64::MAX).take(gap_size));
                ts1.data_mut().extend(ts2.data().iter());
            },
            (nds_cache_rs::buffer::Buffer::Float32(ts1), nds_cache_rs::buffer::Buffer::Float32(ts2))  => {
                ts1.data_mut().extend(iter::repeat(f32::NAN).take(gap_size));
                ts1.data_mut().extend(ts2.data().iter());
            },
            (nds_cache_rs::buffer::Buffer::Float64(ts1), nds_cache_rs::buffer::Buffer::Float64(ts2))  => {
                ts1.data_mut().extend(iter::repeat(f64::NAN).take(gap_size));
                ts1.data_mut().extend(ts2.data().iter());
            },
            (nds_cache_rs::buffer::Buffer::Complex32(ts1), nds_cache_rs::buffer::Buffer::Complex32(ts2))  => {
                ts1.data_mut().extend(iter::repeat(c64::new(f32::NAN, f32::NAN)).take(gap_size));
                ts1.data_mut().extend(ts2.data().iter());
            },
            (nds_cache_rs::buffer::Buffer::Unknown(ts1), nds_cache_rs::buffer::Buffer::Unknown(ts2))  => {
                ts1.data_mut().extend(iter::repeat(vec![0; 16]).take(gap_size));
                ts1.data_mut().extend(ts2.take_data().into_iter());
            },
            // by exepectation that types of all buffers are the same, this can't be reached.
            _ => { 
                println!("buffers from the same channel were of a different type!");
                continue;
            }
        }
    
    }
    first.fields.total_gap_size = total_gap_size;
    first
}
