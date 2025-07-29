//! Create pipelines from a scope view analysis graph
//! dtt analysis graphs are created in a different function
use num_traits::{Float};
use petgraph::data::DataMap;
use petgraph::visit::Topo;
use pipelines::complex::c128;
use user_messages::UserMsgProvider;
use crate::analysis::fourier_tools::csd;
use crate::analysis::graph::analysis::{AnalysisGraph, OutputSource};
use crate::analysis::graph::scheme::SchemePipelineType;
use crate::analysis::scope::splice::{SpliceMode, SplicePipeline};
use crate::analysis::result::ResultsReceiver;
use crate::data_source::data_distributor::add_distributor_to_graph;
use crate::data_source::{DataBlockReceiver};
use crate::errors::DTTError;
use crate::params::channel_params::TrendType;
use crate::run_context::RunContext;
use crate::scope_view::ScopeView;

use crate::analysis::graph::graph_to_pipeline::{create_average, get_incoming_edges, get_only_incoming_edge, populate_output_source, wrap_results, create_timeshift};
use crate::analysis::scope::{downsample, inline_fft::InlineFFTParams, };
use crate::analysis::arithmetic::{real, sqrt};
use crate::params::test_params::AverageType;

pub async fn view_graph_to_pipeline(rc: &Box<RunContext>, view: &mut ScopeView,
                                    graph: &mut AnalysisGraph<'_>, block_rx: DataBlockReceiver)
                                    -> Result<ResultsReceiver, DTTError>
{
    let mut topo = Topo::new(&*graph);

    let mut final_out = Err(DTTError::AnalysisPipelineError("scope view pipeline creation terminated without processing the results node".to_string()));
    
    let mut opt_block_rx = Some(block_rx);
    
    loop {
        let node_idx = match topo.next(&*graph) {
            None => break,
            Some(n) => n,
        };
        let node = graph.node_weight(node_idx).unwrap();

        match node.pipeline_type {
            
            SchemePipelineType::DataSource => {
                if let Some(b_rx) = opt_block_rx {
                    add_distributor_to_graph(rc,
                                             graph, node_idx, b_rx)?
                } else {
                    return Err(DTTError::AnalysisPipelineError("Two data source nodes are not allowed".to_string()));
                };
                opt_block_rx = None;
            },
            SchemePipelineType::Results => {
                let out = wrap_results(rc, graph, node_idx).await;
                final_out = out;
            },
            SchemePipelineType::Identity => {
                return Err(DTTError::UnimplementedOption("Identity type".to_string(), "scope view".to_string()));
            }
            SchemePipelineType::Average => {
                create_average(rc, AverageType::Fixed, graph, node_idx).await?
            },
            SchemePipelineType::Conditioning => {
                create_conditioning(rc, graph, node_idx).await?
            },
            SchemePipelineType::Splice => {
                create_splice(rc, graph, node_idx, view).await?
            },
            SchemePipelineType::Downsample => {
                create_downsample(rc, graph, node_idx).await?
            }
            SchemePipelineType::InlineFFT => {
                create_inline_fft(rc, view.fft_config_tx.subscribe(), graph, node_idx).await?
            }
            SchemePipelineType::CSD => {
                create_csd(rc, graph, node_idx).await?
            }
            SchemePipelineType::Real => {
                create_real(rc, graph, node_idx).await?
            }
            SchemePipelineType::Sqrt => {
                create_sqrt(rc, graph, node_idx).await?
            }
            SchemePipelineType::TimeShift { shift} => {
                create_timeshift(rc, graph, node_idx, shift).await?
            }
            SchemePipelineType::FFT => {
                return Err(DTTError::UnimplementedOption("FFT type".to_string(), "scope view".to_string()));
            },
            SchemePipelineType::ASD => {
                return Err(DTTError::UnimplementedOption("ASD type".to_string(), "scope view".to_string()));
            },
            SchemePipelineType::PerChannelBSource(_) | SchemePipelineType::PerChannelASource(_) => {
                let node_name = graph.node_weight(node_idx).unwrap().name.clone();
                let msg = format!("PerChannel node {} should have been elided before creating pipelines.", node_name);
                return Err(DTTError::AnalysisPipelineError(msg));
            },
            #[cfg(feature = "python-pipe")]
            SchemePipelineType::Custom(_) => {
                return Err(DTTError::UnimplementedOption("Average type".to_string(), "scope view".to_string()));
            }
            SchemePipelineType::Dummy(_create_timeshift) => {
                let msg = format!("{} is a Dummy pipeline. Dummy pipeline can't be used.", node.name);
                return Err(DTTError::AnalysisPipelineError(msg));
            }
        }
    }

    rc.user_messages.clear_message("BadInput");

    final_out.map(|r| r)
}

async fn create_conditioning(rc: &Box<RunContext>, graph: &mut AnalysisGraph<'_>,
                             node_idx: petgraph::graph::NodeIndex) -> Result<(), DTTError> {

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

    let ds = channel.create_data_source_pipeline(rc, buffer_rx).await.into();
    
    populate_output_source(graph, node_idx, &ds);
    
    Ok(())
    
}

async fn create_splice(rc: &Box<RunContext>, graph: &mut AnalysisGraph<'_>,
                             node_idx: petgraph::graph::NodeIndex,
                             view: &ScopeView) -> Result<(), DTTError> {

    let edge_idx = get_only_incoming_edge(graph, node_idx);

    let node = graph.node_weight(node_idx).unwrap();
    let channel = &node.channels[0];
    let pipe_name = channel.name().clone() + ".splice";
    
    let edge = graph.edge_weight_mut(edge_idx).unwrap();
    

    let out_source = match  &edge.output_source {
        OutputSource::NotSet |
        OutputSource::BufferRx(_) |
        OutputSource::PipelineFreqArrayFloat64(_) |
        //OutputSource::PipelineTDArrayString(_) |
        OutputSource::PipelineResultValue(_) |
        OutputSource::PipelineTDPairArrayFloat64(_) |
        OutputSource::PipelineTDPairArrayInt64(_) |
        OutputSource::PipelineTDPairArrayInt32(_) |
        OutputSource::PipelineTDPairArrayInt16(_) |
        OutputSource::PipelineTDPairArrayInt8(_) |
        OutputSource::PipelineTDPairArrayUInt64(_) |
        OutputSource::PipelineTDPairArrayUInt32(_) |
        OutputSource::PipelineTDPairArrayUInt16(_) |
        OutputSource::PipelineTDPairArrayUInt8(_) |
        OutputSource::PipelineFreqArrayComplex128(_) => {
            let msg = format!("{} not a valid input type for a splice pipeline: Must be a time-domain array.", edge.output_source );
            rc.user_messages.set_error("BadInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        }
        OutputSource::PipelineTDArrayFloat64(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip,  view.span.span_pip,
                //SpliceMode::FillGaps(f64::nan()), view.span.online,  t).await.into(),
                SpliceMode::ContiguousLatest, view.span.online,  t).await.into()
        }
        OutputSource::PipelineTDArrayComplex128(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip,  view.span.span_pip,
                                   SpliceMode::FillGaps(c128::new(f64::nan(), f64::nan())), view.span.online,  t).await.into()
        }
        OutputSource::PipelineTDArrayInt64(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip, view.span.span_pip,
                                   SpliceMode::FillGaps(0i64), view.span.online, t).await.into()
        }
        OutputSource::PipelineTDArrayInt32(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip, view.span.span_pip,
                                   SpliceMode::FillGaps(0i32), view.span.online, t).await.into()
        }
        OutputSource::PipelineTDArrayInt16(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip, view.span.span_pip,
                                   SpliceMode::FillGaps(0i16), view.span.online, t).await.into()
        }
        OutputSource::PipelineTDArrayInt8(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip, view.span.span_pip,
                                   SpliceMode::FillGaps(0i8), view.span.online, t).await.into()
        }
        OutputSource::PipelineTDArrayUInt64(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip, view.span.span_pip,
                                   SpliceMode::FillGaps(0u64), view.span.online, t).await.into()
        }
        OutputSource::PipelineTDArrayUInt32(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip, view.span.span_pip,
                                   SpliceMode::FillGaps(0u32), view.span.online, t).await.into()
        }
        OutputSource::PipelineTDArrayUInt16(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip, view.span.span_pip,
                                   SpliceMode::FillGaps(0u16), view.span.online, t).await.into()
        }
        OutputSource::PipelineTDArrayUInt8(t) => {
            SplicePipeline::create(rc.ump_clone(), pipe_name, view.span.start_pip, view.span.span_pip,
                                   SpliceMode::FillGaps(0u8), view.span.online, t).await.into()
        }
    };


    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}


async fn create_downsample(rc: &Box<RunContext>, graph: &mut AnalysisGraph<'_>,
                       node_idx: petgraph::graph::NodeIndex) -> Result<(), DTTError> {

    let edge_idx = get_only_incoming_edge(graph, node_idx);

    let node = graph.node_weight(node_idx).unwrap();
    let channel = &node.channels[0];
    let pipe_name = channel.name().clone() + ".downsample";

    let edge = graph.edge_weight_mut(edge_idx).unwrap();


    let out_source = match  &edge.output_source {
        OutputSource::NotSet |
        OutputSource::BufferRx(_) |
        OutputSource::PipelineTDArrayComplex128(_) |
        OutputSource::PipelineFreqArrayFloat64(_) |
        //OutputSource::PipelineTDArrayString(_) |
        OutputSource::PipelineResultValue(_) |
        OutputSource::PipelineTDPairArrayFloat64(_) |
        OutputSource::PipelineTDPairArrayInt8(_) |
        OutputSource::PipelineTDPairArrayInt16(_) |
        OutputSource::PipelineTDPairArrayInt32(_) |
        OutputSource::PipelineTDPairArrayInt64(_) |
        OutputSource::PipelineTDPairArrayUInt8(_) |
        OutputSource::PipelineTDPairArrayUInt16(_) |
        OutputSource::PipelineTDPairArrayUInt32(_) |
        OutputSource::PipelineTDPairArrayUInt64(_) |
        OutputSource::PipelineFreqArrayComplex128(_) => {
            let msg = format!("{} not a valid input type for a downsample pipeline: Must be an f64 or c128 time domain array.", edge.output_source );
            rc.user_messages.set_error("BadInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        }
        OutputSource::PipelineTDArrayFloat64(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        }

        OutputSource::PipelineTDArrayInt8(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        } 
        OutputSource::PipelineTDArrayInt16(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        }
        OutputSource::PipelineTDArrayInt32(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        }
        OutputSource::PipelineTDArrayInt64(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        }
        OutputSource::PipelineTDArrayUInt8(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        }
        OutputSource::PipelineTDArrayUInt16(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        }
        OutputSource::PipelineTDArrayUInt32(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        }
        OutputSource::PipelineTDArrayUInt64(t) => {
            downsample::DownsampleCache::create(rc.ump_clone(), pipe_name, t).await.into()
        }
    };


    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}

async fn create_inline_fft(rc: &Box<RunContext>, fft_config_rx: tokio::sync::watch::Receiver<InlineFFTParams>,
                           graph: &mut AnalysisGraph<'_>,
                           node_idx: petgraph::graph::NodeIndex) -> Result<(), DTTError> {

    let edge_idx = get_only_incoming_edge(graph, node_idx);

    let node = graph.node_weight(node_idx).unwrap();
    let channel = &node.channels[0];
    let pipe_name = channel.name().clone() + ".inline_fft";

    let edge = graph.edge_weight_mut(edge_idx).unwrap();


    let out_source = match  &edge.output_source {
        OutputSource::NotSet |
        OutputSource::BufferRx(_) |
        OutputSource::PipelineFreqArrayComplex128(_) |
        OutputSource::PipelineFreqArrayFloat64(_) |
        //OutputSource::PipelineTDArrayString(_) |
        OutputSource::PipelineResultValue(_) |
        OutputSource::PipelineTDPairArrayFloat64(_) |
        OutputSource::PipelineTDPairArrayInt8(_) |
        OutputSource::PipelineTDPairArrayInt16(_) |
        OutputSource::PipelineTDPairArrayInt32(_) |
        OutputSource::PipelineTDPairArrayInt64(_) |
        OutputSource::PipelineTDPairArrayUInt8(_) |
        OutputSource::PipelineTDPairArrayUInt16(_) |
        OutputSource::PipelineTDPairArrayUInt32(_) |
        OutputSource::PipelineTDPairArrayUInt64(_) |
        OutputSource::PipelineTDArrayInt8(_) |
        OutputSource::PipelineTDArrayInt16(_) |
        OutputSource::PipelineTDArrayInt32(_) |
        OutputSource::PipelineTDArrayInt64(_) |
        OutputSource::PipelineTDArrayUInt8(_) |
        OutputSource::PipelineTDArrayUInt16(_) |
        OutputSource::PipelineTDArrayUInt32(_) |
        OutputSource::PipelineTDArrayUInt64(_)  => {
            let msg = format!("{} not a valid input type for a inline fft pipeline: Must be an f64 or c128 time domain array.", edge.output_source );
            rc.user_messages.set_error("BadInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        },
        OutputSource::PipelineTDArrayFloat64(t) => {
            InlineFFTParams::create(rc.ump_clone(), pipe_name, fft_config_rx, t).await.into()
        },

        OutputSource::PipelineTDArrayComplex128(t) => {
            InlineFFTParams::create(rc.ump_clone(), pipe_name, fft_config_rx, t).await.into()
        },


    };


    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}


async fn create_csd(rc: &Box<RunContext>,
                           graph: &mut AnalysisGraph<'_>,
                           node_idx: petgraph::graph::NodeIndex) -> Result<(), DTTError> {

    let edges_idx = get_incoming_edges(graph, node_idx);

    if edges_idx.len() != 2 {
        let msg = format!("{} must have exactly 2 incoming edges.", node_idx.index());
        rc.user_messages.set_error("BadInput", msg.clone());
        return Err(DTTError::AnalysisPipelineError(msg));
    }

    let node = graph.node_weight(node_idx).unwrap();
    let channel = &node.channels[0];
    let pipe_name = channel.name().clone() + ".csd";

    let edge1 = graph.edge_weight(edges_idx[0]).unwrap();
    let edge2 = graph.edge_weight(edges_idx[1]).unwrap();

    let out_source = match  (&edge1.output_source, &edge2.output_source) {
        (OutputSource::PipelineFreqArrayComplex128(t1),
            OutputSource::PipelineFreqArrayComplex128(t2)) => {
            csd::create(rc.ump_clone(), pipe_name, t1, t2).await.into()
        },
        (a,b)  => {
            let msg = format!("{} x {} are not valid input types for a csd pipeline. must be  c128 freq. domain arrays.", a, b );
            rc.user_messages.set_error("BadInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        },

    };


    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}


async fn create_real(rc: &Box<RunContext>,
                    graph: &mut AnalysisGraph<'_>,
                    node_idx: petgraph::graph::NodeIndex) -> Result<(), DTTError> {

    let edge_idx = get_only_incoming_edge(graph, node_idx);

    let node = graph.node_weight(node_idx).unwrap();
    let channel = &node.channels[0];
    let pipe_name = channel.name().clone() + ".real";

    let edge = graph.edge_weight_mut(edge_idx).unwrap();

    let out_source = match  &edge.output_source {
        OutputSource::PipelineFreqArrayComplex128(t) => {
            real::create(rc.ump_clone(), pipe_name, t).await.into()
        },
        a  => {
            let msg = format!("{} is not valid input type for a real pipeline. must be  complex 128 freq. domain array.", a );
            rc.user_messages.set_error("BadInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        },

    };

    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}

async fn create_sqrt(rc: &Box<RunContext>,
                     graph: &mut AnalysisGraph<'_>,
                     node_idx: petgraph::graph::NodeIndex) -> Result<(), DTTError> {

    let edge_idx = get_only_incoming_edge(graph, node_idx);

    let node = graph.node_weight(node_idx).unwrap();
    let channel = &node.channels[0];
    let pipe_name = channel.name().clone() + ".sqrt";

    let edge = graph.edge_weight_mut(edge_idx).unwrap();

    let out_source = match  &edge.output_source {
        OutputSource::PipelineFreqArrayComplex128(t) => {
            sqrt::create(rc.ump_clone(), pipe_name, t).await.into()
        },
        OutputSource::PipelineFreqArrayFloat64(t) => {
            sqrt::create(rc.ump_clone(), pipe_name, t).await.into()
        },
        OutputSource::PipelineTDArrayComplex128(t) => {
            sqrt::create(rc.ump_clone(), pipe_name, t).await.into()
        },
        OutputSource::PipelineTDArrayFloat64(t) => {
            sqrt::create(rc.ump_clone(), pipe_name, t).await.into()
        },
        a  => {
            let msg = format!("{} is not valid input type for a sqrt pipeline. must be a floating point array.", a );
            rc.user_messages.set_error("BadInput", msg.clone());
            return Err(DTTError::AnalysisPipelineError(msg));
        },

    };

    populate_output_source(graph, node_idx, &out_source);

    Ok(())
}