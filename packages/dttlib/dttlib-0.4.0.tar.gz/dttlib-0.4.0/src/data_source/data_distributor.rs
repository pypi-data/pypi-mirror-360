//! Take data from a data source and
//! send to analysis pipelines

use std::collections::HashMap;
use tokio::sync::mpsc;
use super::buffer::Buffer;
use petgraph::graph::NodeIndex;
use petgraph::Outgoing;
use petgraph::visit::EdgeRef;
use user_messages::UserMsgProvider;
use crate::analysis::graph::analysis::{AnalysisGraph, OutputSource};
use crate::data_source::{DataBlock, DataBlockReceiver};
use crate::errors::DTTError;
use crate::params::channel_params::channel::Channel;
use crate::run_context::RunContext;

async fn distribute(rc: Box<dyn UserMsgProvider>, mut receiver: mpsc::Receiver<DataBlock>, senders: HashMap<Channel, mpsc::Sender<Buffer>>) {

    let umh = rc.user_message_handle();
    'outer: loop {
        let block = match receiver.recv().await {
            Some(b) => b,
            None => break 'outer, // test over, no more data
        };
        for (channel, buffers) in block {
            if let Some(s) = senders.get(&channel) {
                for buffer in buffers {
                    //println!("distributing buffer for {}", buffer.channel().name());
                    if s.send(buffer).await.is_err() {
                        // nothing down stream to receive the buffer.
                        // test must be closing up.
                        break 'outer;
                    }
                }
            }
            else {
                let msg = format!("DataDistributor: Data for channel {}:{} received but no Sender was found for it.", channel.name, channel.trend_stat);
                umh.warning(msg)
            }
        }
    }
}

/// add the buffer receivers for a distributor to an analysis graph and start the distributor task
/// node_idx must be the node index for the one and only DataSource node.
/// This function adds the buffer receiver appropriate to each outgoing edge.
pub (crate) fn add_distributor_to_graph(rc: &Box<RunContext>, 
                                graph: &mut AnalysisGraph, node_idx: NodeIndex, 
                                block_rx: DataBlockReceiver) -> Result<(), DTTError> {

    // create channel channels
    let mut buf_tx_hash = HashMap::new();

    // populate the  edges
    let edges: Vec<_> = graph.edges_directed(node_idx, Outgoing)
        .map(|e|{e.id()}).collect();

    for edge_idx in edges {
        let (_, target_idx) = graph.edge_endpoints(edge_idx).unwrap();
        let channel: Channel = {
            let target = graph.node_weight(target_idx).unwrap();
            match target.channels.get(0) {
                Some(c) => c.clone().into(),
                None => {
                    let msg = format!("DataSource edge leads to a node {} with no associated channel.", target.name);
                    rc.user_messages.set_error("NoAssociatedChannel", msg.clone());
                    return Err(DTTError::AnalysisPipelineError(msg));
                },
            }
        };
        let edge = graph.edge_weight_mut(edge_idx).unwrap();

        let (tx, rx) = mpsc::channel(16);
        buf_tx_hash.insert(channel.clone(), tx);
        edge.output_source = OutputSource::BufferRx(rx);
    }

    rc.user_messages.clear_message("NoAssociatedChannel");

    // create distributor task
    tokio::spawn(
        distribute(rc.clone(), block_rx, buf_tx_hash)
    );

    Ok(())
}