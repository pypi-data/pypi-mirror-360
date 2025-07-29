use ligo_hires_gps_time::PipDuration;
use petgraph::graph::EdgeIndex;
use petgraph::data::DataMap;
use petgraph::graph::NodeIndex;
use petgraph::{Incoming, Outgoing};
use petgraph::visit::{EdgeRef, Topo};

#[cfg(feature = "python-pipe")]
use pipelines::python;

#[cfg(feature = "python-pipe")]
use pipelines::PipelineSubscriber;

use user_messages::UserMsgProvider;
use crate::analysis;

#[cfg(feature = "python-pipe")]
use crate::analysis::result::result_value::ResultValue;

use crate::analysis::conditioning::time_shift::start_timeshift;
use crate::analysis::fourier_tools::asd::ASD;
use crate::analysis::fourier_tools::fft::FFT;
use crate::analysis::graph::analysis::{AnalysisGraph, OutputSource};
use crate::analysis::graph::scheme::SchemePipelineType;
use crate::analysis::result::{EdgeResultsWrapper, ResultsReceiver};
use crate::AnalysisResult;
use crate::data_source::data_distributor::add_distributor_to_graph;
use crate::data_source::DataSourceRef;
use crate::errors::DTTError;
use crate::params::channel_params::channel::Channel;
#[cfg(feature = "python-pipe")]
use crate::params::custom_pipeline::CustomPipeline;
use crate::params::test_params::AverageType;
use crate::run_context::RunContext;
use crate::timeline::Timeline;

/// create the entire set of analysis pipelines from a graph and data source
/// This is specifically DTT analysis graph from a DTT pipeline.
/// Scope windows have a separate function for converting graphs to pipelines
pub (crate) async fn graph_to_pipeline(rc: &Box<RunContext>, timeline: &Timeline, graph: &mut AnalysisGraph<'_>,
                         data_source: &DataSourceRef) -> Result<ResultsReceiver, DTTError> {

    let mut topo = Topo::new(&*graph);
    
    let mut final_out = Err(DTTError::AnalysisPipelineError("pipeline creation terminated without processing the results node".to_string()));

    loop {
        let node_idx = match topo.next(&*graph) {
            None => break,
            Some(n) => n,
        };
        let node = graph.node_weight(node_idx).unwrap();

        match node.pipeline_type {
            SchemePipelineType::DataSource => {

                let chan_records: Vec<Channel> = timeline.all_channels().into_iter().map(|x| x.channel.clone()).collect();
                
                let block_rx = data_source.stream_data(rc.clone(),
                    chan_records.as_slice(),
                    timeline.extended_start_time_pip()?,
                        timeline.extended_end_time_pip()?)?;
                
                add_distributor_to_graph(rc, graph, node_idx, block_rx)?
            },
            SchemePipelineType::Results => {
                let out = wrap_results(rc, graph, node_idx).await;
                final_out = out;
            },
            SchemePipelineType::Average => {
                create_average(rc, timeline.test_params.average_type.clone(), graph, node_idx).await?
            },
            SchemePipelineType::Identity => {
                create_identity(rc, timeline, graph, node_idx).await?
            },
            SchemePipelineType::Conditioning => {
                create_conditioning(rc, timeline, graph, node_idx).await?
            },
            SchemePipelineType::FFT => {
                create_fft(rc, timeline, graph, node_idx).await?
            },
            SchemePipelineType::ASD => {
                create_asd(rc, timeline, graph, node_idx).await?
            },
            SchemePipelineType::PerChannelBSource(_) | SchemePipelineType::PerChannelASource(_) => {
                let node_name = graph.node_weight(node_idx).unwrap().name.clone();
                let msg = format!("PerChannel node {} should have been elided before creating pipelines.", node_name);
                return Err(DTTError::AnalysisPipelineError(msg));
            },
            #[cfg(feature = "python-pipe")]
            SchemePipelineType::Custom(c) => {
                create_custom_1_input(rc, timeline, graph, node_idx, c).await?
            }
            SchemePipelineType::Dummy(_) => {
                let msg = format!("{} is a Dummy pipeline. Dummy pipeline can't be used.", node.name);
                return Err(DTTError::AnalysisPipelineError(msg));
            }
            SchemePipelineType::Splice => {
                let msg = format!("Splice pipeline {} is not supported for DTT type analysis", node.name);
                return Err(DTTError::AnalysisPipelineError(msg));
            }
            SchemePipelineType::Downsample => {
                let msg = format!("Downsample pipeline {} is not supported for DTT type analysis", node.name);
                return Err(DTTError::AnalysisPipelineError(msg));
            }
            SchemePipelineType::InlineFFT => {
                let msg = format!("InlineFFT pipeline {} is not supported for DTT type analysis", node.name);
                return Err(DTTError::AnalysisPipelineError(msg));
            }
            SchemePipelineType::Real => {
                let msg = format!("Real pipeline {} is not supported for DTT type analysis", node.name);
                return Err(DTTError::AnalysisPipelineError(msg));
            }
            SchemePipelineType::CSD => {
                let msg = format!("CSD pipeline {} is not supported for DTT type analysis", node.name);
                return Err(DTTError::AnalysisPipelineError(msg));
            }
            SchemePipelineType::Sqrt => {
                let msg = format!("Sqrt pipeline {} is not supported for DTT type analysis", node.name);
                return Err(DTTError::AnalysisPipelineError(msg));
            }
            SchemePipelineType::TimeShift{shift} => {
                create_timeshift(rc, graph, node_idx, shift).await?
            }
        }
    }
    final_out
}



pub ( super ) async fn wrap_results(rc: &'_ Box<RunContext>, graph: &'_ AnalysisGraph<'_>, node_idx: NodeIndex) -> Result<ResultsReceiver, DTTError> {

    let (results_tx, results_rx) = tokio::sync::mpsc::channel(128);

    let edges: Vec<_> = graph.edges_directed(node_idx, Incoming)
        .map(|e| e.id()).collect();
    for edge_idx in edges {
        let (source_idx, _) = graph.edge_endpoints(edge_idx).unwrap();
        let source = graph.node_weight(source_idx).unwrap();
        let edge = graph.edge_weight(edge_idx).unwrap();
        match &edge.results_wrapper {
            Some(EdgeResultsWrapper::ASD) => {
                match &edge.output_source {
                    OutputSource::PipelineFreqArrayFloat64(x) =>
                        AnalysisResult::asd_wrapper(rc, source.channels[0].clone().into(), &x, results_tx.clone()).await,
                    s => {
                        let msg = format!("An ASD result requires a real-valued frequency array as output, but was {}", s);
                        rc.user_messages.set_error("WrongResultType", msg.clone());
                        return Err(DTTError::AnalysisPipelineError(msg));
                    }
                }
            }
            Some(EdgeResultsWrapper::ResultValue) => {
                match &edge.output_source {
                    OutputSource::PipelineResultValue(x) => {
                        let result_name = source.get_result_value_name()?;
                        let chans: Vec<_> = source.channels.iter().map(|x|{x.clone().into()}).collect();
                        AnalysisResult::result_value_wrapper(rc, chans.as_slice(), result_name, &x, results_tx.clone()).await;
                    },
                    s => {
                        let msg = format!("An general result requires a Result-value as output, but was {}", s);
                        rc.user_messages.set_error("WrongResultType", msg.clone());
                        return Err(DTTError::AnalysisPipelineError(msg));
                    }
                }
            }
            Some(EdgeResultsWrapper::TimeDomainReal) => {
                match &edge.output_source {
                    OutputSource::PipelineTDArrayFloat64(x)
                        => AnalysisResult::time_domain_real_wrapper(rc, source.channels[0].clone().into(), x, results_tx.clone()).await,
                    OutputSource::PipelineTDPairArrayFloat64(x)
                        => AnalysisResult::time_domain_real_wrapper(rc, source.channels[0].clone().into(), x, results_tx.clone()).await,
                    s => {
                        let msg = format!("A real time-domain result requires a real-valued time domain array as output, but was {}", s);
                        rc.user_messages.set_error("WrongResultType", msg.clone());
                        return Err(DTTError::AnalysisPipelineError(msg));
                    }
                }
            },
            // Some(r) => {
            //     let msg = format!("analysis pipeline result wrapper {} is not implemented.", r);
            //     rc.user_messages.set_error("WrongResultType", msg);
            // },
            None => {
                let msg = "No result wrapper was specified.".to_string();
                rc.user_messages.set_error("WrongResultType", msg.clone());
                return Err(DTTError::AnalysisPipelineError(msg));
            }
        }
    }

    rc.user_messages.clear_message("WrongResultType");

    Ok(results_rx)
}

pub (super) fn get_only_incoming_edge(graph: &AnalysisGraph, node_idx: NodeIndex) -> EdgeIndex {
    graph.edges_directed(node_idx, Incoming).next().unwrap().id()
}

pub (super) fn get_incoming_edges(graph: &AnalysisGraph, node_idx: NodeIndex) -> Vec<EdgeIndex> {
    graph.edges_directed(node_idx, Incoming).map(|e| e.id()).collect()
}

/// write the output source to every outgoing edge of a node
pub (super) fn populate_output_source(graph: &mut AnalysisGraph,
                          node_idx: NodeIndex, output_source: &OutputSource) {
    let edges: Vec<_> = graph.edges_directed(node_idx, Outgoing)
        .map(|e|{e.id()}).collect();
    for edge_idx in edges {
        let edge_weight = graph.edge_weight_mut(edge_idx).unwrap();
        edge_weight.output_source = output_source.almost_copy();
    }
}

/// simply pass the input into the output
async fn create_identity(_rc: &Box<RunContext>, _timeline: &Timeline,
                         graph: & mut AnalysisGraph<'_>, node_idx: NodeIndex) -> Result<(), DTTError> {
    let edge_idx = get_only_incoming_edge(graph, node_idx);


    let edge = graph.edge_weight(edge_idx).unwrap();

    let out_source = edge.output_source.almost_copy();

    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}

// time shift the input to the output
pub (super) async fn create_timeshift(rc: &Box<RunContext>,
                         graph: & mut AnalysisGraph<'_>, node_idx: NodeIndex, shift: PipDuration) -> Result<(), DTTError> {
    let node = graph.node_weight(node_idx).unwrap();
    let node_name = node.name.clone();
    let channel = &node.channels[0];
    let edge_idx = get_only_incoming_edge(graph, node_idx);
    let edge = graph.edge_weight(edge_idx).unwrap();

    // shift trends later in time by 1/2 step to make their time stamps centered in the time
    // region they summarize
    //
    // this is just period/2, but a more correct formula would be period *  (n-1)/2*n)
    // where n is the number of points per region.

    let out_source = match &edge.output_source {
        OutputSource::PipelineTDArrayInt8(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayInt8(p)
        },
        OutputSource::PipelineTDArrayInt16(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayInt16(p)
        },
        OutputSource::PipelineTDArrayInt32(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayInt32(p)
        },
        OutputSource::PipelineTDArrayInt64(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayInt64(p)
        },
        OutputSource::PipelineTDArrayUInt8(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayUInt8(p)
        },
        OutputSource::PipelineTDArrayUInt16(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayUInt16(p)
        },
        OutputSource::PipelineTDArrayUInt32(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayUInt32(p)
        },
        OutputSource::PipelineTDArrayUInt64(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayUInt64(p)
        },        
        OutputSource::PipelineTDArrayFloat64(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayFloat64(p)
        },
        OutputSource::PipelineTDArrayComplex128(f) => {
            let p = start_timeshift(rc.ump_clone(), channel.name().clone() + &node_name, shift, f).await;
            OutputSource::PipelineTDArrayComplex128(p)
        },
        s => {
            let msg = format!("Time-shfit on node {} must be a time domain value.  Got {}", node_name, s);
            rc.user_messages.set_error("TimeShiftWrongInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        }
    }.into();

    rc.user_messages.clear_message("TimeShiftWrongInput");

    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}

pub (super) async fn create_average(rc: &Box<RunContext>, average_type: AverageType,
                        graph: & mut AnalysisGraph<'_>, node_idx: NodeIndex) -> Result<(), DTTError> {

    let edge_idx = get_only_incoming_edge(graph, node_idx);

    let (source_idx, _) = graph.edge_endpoints(edge_idx).unwrap();

    let avg_name = graph.node_weight(source_idx).unwrap().name.clone() + ".avg";

    let node = graph.node_weight(node_idx).unwrap();

    let node_name = node.name.clone();
    
    let edge = graph.edge_weight(edge_idx).unwrap();

    let out_source= match average_type {
        
        AverageType::Fixed => {
            match &edge.output_source {
                OutputSource::NotSet | OutputSource::BufferRx(_)
                | OutputSource::PipelineTDArrayComplex128(_)
                | OutputSource::PipelineTDArrayFloat64(_)
                | OutputSource::PipelineTDArrayInt64(_)
                | OutputSource::PipelineTDArrayInt32(_)
                | OutputSource::PipelineTDArrayInt16(_)
                | OutputSource::PipelineTDArrayInt8(_)
                | OutputSource::PipelineTDArrayUInt64(_)
                | OutputSource::PipelineTDArrayUInt32(_)
                | OutputSource::PipelineTDArrayUInt16(_)
                | OutputSource::PipelineTDArrayUInt8(_)
                | OutputSource::PipelineTDPairArrayFloat64(_)
                | OutputSource::PipelineTDPairArrayInt64(_)
                | OutputSource::PipelineTDPairArrayInt32(_)
                | OutputSource::PipelineTDPairArrayInt16(_)
                | OutputSource::PipelineTDPairArrayInt8(_)
                | OutputSource::PipelineTDPairArrayUInt64(_)
                | OutputSource::PipelineTDPairArrayUInt32(_)
                | OutputSource::PipelineTDPairArrayUInt16(_)
                | OutputSource::PipelineTDPairArrayUInt8(_)
                //| OutputSource::PipelineTDArrayString(_)
                | OutputSource::PipelineResultValue(_)
                => {
                    let msg = format!("Average node {} requires an addable pipeline input", node_name);
                    rc.user_messages.set_error("MissingInput", msg.clone());
                    return Err(DTTError::AnalysisPipelineError(msg));
                },
                OutputSource::PipelineFreqArrayFloat64(p) => {
                    rc.user_messages.clear_message("MissingInput");
                    let avg_pipe = analysis::arithmetic::average::create(rc.clone(), avg_name, &p).await;
                    OutputSource::PipelineFreqArrayFloat64(avg_pipe)
                },
                OutputSource::PipelineFreqArrayComplex128(p) => {
                    rc.user_messages.clear_message("MissingInput");
                    let avg_pipe = analysis::arithmetic::average::create(rc.clone(), avg_name, &p).await;
                    OutputSource::PipelineFreqArrayComplex128(avg_pipe)
                },
                // OutputSource::PipelineResultValue(p) => {
                //     rc.user_messages.clear_message("MissingInput");
                //     let avg_pipe: PipelineSubscriber<ResultValue> = analysis::general::average
                //     ::create(rc.clone(), avg_name, p).await;
                //     OutputSource::PipelineResultValue(avg_pipe)
                // },
            }
        },
        a => return Err(DTTError::UnimplementedOption("Average type".to_string(), a.to_string())),
    };
    
    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}

async fn create_conditioning(rc: &Box<RunContext>, timeline: &Timeline, graph: &mut AnalysisGraph<'_>, 
                             node_idx: NodeIndex) -> Result<(), DTTError> {

    let edge_idx = get_only_incoming_edge(graph, node_idx);
    let edge = graph.edge_weight_mut(edge_idx).unwrap();
    let in_source_result = edge.take_nds_buffer_rx();
    let node = graph.node_weight(node_idx).unwrap();
    let channel = &node.channels[0];

    let node_name = node.name.clone();

    let buffer_rx = match in_source_result {
        Ok(r) =>  r,
        Err(s) => {
            let msg = format!("Conditioning pipeline {} only accepts NDS buffer pipes as input but got {}", node_name, s);
            rc.user_messages.set_error("BadInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        },
    };

    let out_source = channel.create_conditioning_pipeline(rc, timeline, buffer_rx).await?.into();

    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}

async fn create_fft(rc: &Box<RunContext>, timeline: &Timeline, graph: &mut AnalysisGraph<'_>,
                    node_idx: NodeIndex) -> Result<(), DTTError> {
    let node = graph.node_weight(node_idx).unwrap();
    let node_name = node.name.clone();
    let channel = &node.channels[0];
    let edge_idx = get_only_incoming_edge(graph, node_idx);
    let edge = graph.edge_weight(edge_idx).unwrap();

    let out_source = match &edge.output_source {
        OutputSource::PipelineTDArrayFloat64(t) => {
            FFT::create(rc.ump_clone(), channel.name().clone() + ":fft(real)", timeline, t).await?
        },
        OutputSource::PipelineTDArrayComplex128(t) => {
            FFT::create(rc.ump_clone(), channel.name().clone() + ":fft(complex)", timeline, t).await?
        },
        s => {
            let msg = format!("FFT input on node {} must be time domain.  Got {}", node_name, s);
            rc.user_messages.set_error("FFTWrongInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        }
    }.into();

    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}

async fn create_asd(rc: &Box<RunContext>, timeline: &Timeline, graph: &mut AnalysisGraph<'_>,
                    node_idx: NodeIndex) -> Result<(), DTTError> {
    let node = graph.node_weight(node_idx).unwrap();
    let node_name = node.name.clone();
    let channel = &node.channels[0];
    let edge_idx = get_only_incoming_edge(graph, node_idx);
    let edge = graph.edge_weight(edge_idx).unwrap();

    let out_source = match &edge.output_source {
        OutputSource::PipelineFreqArrayComplex128(f) => {
            ASD::create(rc.ump_clone(), channel.name().clone() + ":asd", timeline.heterodyned, f).await
        },
        s => {
            let msg = format!("FFT input on node {} must be a complex frequency domain value.  Got {}", node_name, s);
            rc.user_messages.set_error("FFTWrongInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        }
    }.into();

    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}

#[cfg(feature = "python-pipe")]
async fn create_custom_1_input(rc: &Box<RunContext>, _timeline: &Timeline, graph: &mut AnalysisGraph<'_>,
                       node_idx: NodeIndex, custom_pipeline: &CustomPipeline) -> Result<(), DTTError> {

    let node = graph.node_weight(node_idx).unwrap();
    let node_name = node.name.clone();
    let edge_idx = get_only_incoming_edge(graph, node_idx);
    let edge = graph.edge_weight(edge_idx).unwrap();
    
    let wrapped_in_source = edge.output_source
        .to_value_pipeline(rc, node_name.clone() + ".input_wrapper").await?;

    let out_pipe: PipelineSubscriber<ResultValue> = python::PythonPipeState::create(rc.ump_clone(), node_name, 
                                                   custom_pipeline.py_module.as_ref(), 
                                                   &wrapped_in_source).await;

    let out_source = out_pipe.into();
    populate_output_source(graph, node_idx, &out_source);
    
    Ok(())
}
