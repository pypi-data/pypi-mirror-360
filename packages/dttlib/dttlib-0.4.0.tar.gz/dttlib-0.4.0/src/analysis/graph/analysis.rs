

//! the actual analysis graph, built up from scheme graphs and a test timeline

use std::cmp::Ordering;
use std::collections::{HashMap, HashSet};
use std::fmt::{Display, Formatter};
use std::hash::{Hash, Hasher};
use crate::data_source::buffer::Buffer;
use petgraph::{Directed, Direction, Graph};
use petgraph::algo::{connected_components, toposort};
use petgraph::data::DataMap;
use petgraph::graph::{NodeIndex};
use petgraph::visit::{EdgeRef, Topo};
use tokio::sync::mpsc;
use pipelines::complex::c128;
use pipelines::PipelineSubscriber;
use pipelines::stateless::pure::PureStatelessPipeline1;
use user_messages::UserMsgProvider;
use crate::analysis::conditioning::StandardPipeOutput;
use crate::analysis::general;
use crate::analysis::graph::analysis::OutputSource::{NotSet, PipelineFreqArrayComplex128, PipelineFreqArrayFloat64, PipelineResultValue, PipelineTDArrayFloat64, PipelineTDArrayInt32, PipelineTDArrayInt64, PipelineTDPairArrayFloat64, PipelineTDPairArrayInt64};
use crate::analysis::graph::scheme::{SchemeEdge, SchemeGraph, SchemeNode, SchemePipelineType};
use crate::analysis::result::{EdgeDataType, EdgeResultsWrapper};
use crate::analysis::types::frequency_domain_array::{FreqDomainArray, FreqDomainArrayComplex, FreqDomainArrayReal};
use crate::analysis::types::time_domain_array::{TimeDomainArray, TimeDomainArrayComplex, TimeDomainArrayReal};
use crate::errors::DTTError;
use crate::params::channel_params::ChannelSettings;
use crate::params::channel_params::nds_data_type::NDSDataType::Float32;
use crate::analysis::result::result_value::ResultValue;
use crate::params::channel_params::channel::Channel;
use crate::run_context::RunContext;

#[derive(Debug, Clone)]
pub (crate) struct AnalysisNode<'a> {
    pub pipeline_type: SchemePipelineType<'a>,
    pub name: String,
    pub channels: Vec<ChannelSettings>,
}

impl<'a> PartialEq for AnalysisNode<'a> {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name && self.channels == other.channels
    }
}

impl<'a> Eq for AnalysisNode<'a> {

}

impl<'a> Hash for AnalysisNode<'a> {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.name.hash(state);
        self.channels.hash(state);
    }
}

impl<'a> PartialOrd for AnalysisNode<'a> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl<'a> Ord for AnalysisNode<'a> {
    fn cmp(&self, other: &Self) -> Ordering {
        if self.channels < other.channels {
            Ordering::Less
        }
        else if self.channels > other.channels {
            Ordering::Greater
        }
        else if self.name < other.name {
            Ordering::Less
        }
        else if self.name > other.name {
            Ordering::Greater
        }
        else {
            Ordering::Equal
        }
    }
}

impl<'a> AnalysisNode<'a> {
    pub (crate)  fn from_scheme_node(other: &SchemeNode<'a>, channels: Vec<ChannelSettings>) -> Self {
        Self {
            pipeline_type: other.pipeline_type.clone(),
            name: other.name.clone(),
            channels,
        }
    }

    pub (crate)  fn get_result_value_name(&self) -> Result<String, DTTError> {
        match &self.pipeline_type {
            #[cfg(feature = "python-pipe")]
            SchemePipelineType::Custom(c) => Ok(c.name.clone()),
            p => {
                let msg = format!("Cannot get a ResultValue name for {} pipelines.", p);
                Err(DTTError::AnalysisPipelineError(msg))
            }
        }
    }
}

/// owns the output structure for an edge
/// so that target nodes know what to link to
#[derive(Default, Debug)]
pub (crate) enum OutputSource {
    #[default]
    NotSet,
    // receiver for NDS buffer
    BufferRx(mpsc::Receiver<Buffer>),

    // pipeline subscribers
    PipelineTDArrayFloat64(PipelineSubscriber<TimeDomainArray<f64>>),
    PipelineTDArrayComplex128(PipelineSubscriber<TimeDomainArray<c128>>),
    PipelineFreqArrayFloat64(PipelineSubscriber<FreqDomainArray<f64>>),
    PipelineFreqArrayComplex128(PipelineSubscriber<FreqDomainArray<c128>>),

    PipelineTDArrayInt64(PipelineSubscriber<TimeDomainArray<i64>>),
    PipelineTDArrayInt32(PipelineSubscriber<TimeDomainArray<i32>>),
    PipelineTDArrayInt16(PipelineSubscriber<TimeDomainArray<i16>>),
    PipelineTDArrayInt8(PipelineSubscriber<TimeDomainArray<i8>>),

    PipelineTDArrayUInt64(PipelineSubscriber<TimeDomainArray<u64>>),
    PipelineTDArrayUInt32(PipelineSubscriber<TimeDomainArray<u32>>),
    PipelineTDArrayUInt16(PipelineSubscriber<TimeDomainArray<u16>>),
    PipelineTDArrayUInt8(PipelineSubscriber<TimeDomainArray<u8>>),

    PipelineTDPairArrayFloat64(PipelineSubscriber<(TimeDomainArray<f64>, TimeDomainArray<f64>)>),
    PipelineTDPairArrayInt64(PipelineSubscriber<(TimeDomainArray<i64>, TimeDomainArray<i64>)>),
    PipelineTDPairArrayInt32(PipelineSubscriber<(TimeDomainArray<i32>, TimeDomainArray<i32>)>),
    PipelineTDPairArrayInt16(PipelineSubscriber<(TimeDomainArray<i16>, TimeDomainArray<i16>)>),
    PipelineTDPairArrayInt8(PipelineSubscriber<(TimeDomainArray<i8>, TimeDomainArray<i8>)>),
    PipelineTDPairArrayUInt64(PipelineSubscriber<(TimeDomainArray<u64>, TimeDomainArray<u64>)>),
    PipelineTDPairArrayUInt32(PipelineSubscriber<(TimeDomainArray<u32>, TimeDomainArray<u32>)>),
    PipelineTDPairArrayUInt16(PipelineSubscriber<(TimeDomainArray<u16>, TimeDomainArray<u16>)>),
    PipelineTDPairArrayUInt8(PipelineSubscriber<(TimeDomainArray<u8>, TimeDomainArray<u8>)>),




    //PipelineTDArrayString(PipelineSubscriber<TimeDomainArray<String>>),

    // here we've given up on trying to match types on compile time
    // and are just using an enum
    // a PipelineResultValue must also have a string name to use as an identifier
    PipelineResultValue(PipelineSubscriber<ResultValue>),
}

impl Display for  OutputSource {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            OutputSource::NotSet => write!(f, "Not Set"),
            OutputSource::BufferRx(_) => write!(f, "NDS Buffer Receiver"),
            OutputSource::PipelineFreqArrayFloat64(_) => write!(f, "Real-valued frequency array"),
            OutputSource::PipelineFreqArrayComplex128(_) => write!(f, "Complex-valued frequency array"),
            OutputSource::PipelineTDArrayFloat64(_) => write!(f, "Real-valued time-domain array"),
            OutputSource::PipelineTDArrayComplex128(_) => write!(f, "Complex-valued time-domain array"),

            OutputSource::PipelineTDArrayInt64(_) => write!(f, "int 64 Time domain array"),
            OutputSource::PipelineTDArrayInt32(_) => write!(f, "int 32 Time domain array"),
            OutputSource::PipelineTDArrayInt16(_) => write!(f, "int 16 Time domain array"),
            OutputSource::PipelineTDArrayInt8(_) => write!(f, "int 8 Time domain array"),
            OutputSource::PipelineTDArrayUInt64(_) => write!(f, "unsigned int 64 Time domain array"),
            OutputSource::PipelineTDArrayUInt32(_) => write!(f, "unsigned int 32 Time domain array"),
            OutputSource::PipelineTDArrayUInt16(_) => write!(f, "unsigned int 16 Time domain array"),
            OutputSource::PipelineTDArrayUInt8(_) => write!(f, "unsigned int 8 Time domain array"),

            OutputSource::PipelineTDPairArrayFloat64(_) => write!(f, "Real-valued time-domain pair of arrays"),
            OutputSource::PipelineTDPairArrayInt64(_) => write!(f, "int 64 Time domain pair of arrays"),
            OutputSource::PipelineTDPairArrayInt32(_) => write!(f, "int 32 Time domain pair of arrays"),
            OutputSource::PipelineTDPairArrayInt16(_) => write!(f, "int 16 Time domain pair of arrays"),
            OutputSource::PipelineTDPairArrayInt8(_) => write!(f, "int 8 Time domain pair of arrays"),

            OutputSource::PipelineTDPairArrayUInt64(_) => write!(f, "uint 64 Time domain pair of arrays"),
            OutputSource::PipelineTDPairArrayUInt32(_) => write!(f, "uint 32 Time domain pair of arrays"),
            OutputSource::PipelineTDPairArrayUInt16(_) => write!(f, "uint 16 Time domain pair of arrays"),
            OutputSource::PipelineTDPairArrayUInt8(_) => write!(f, "uint 8 Time domain pair of arrays"),

            //OutputSource::PipelineTDArrayString(_) => write!(f, "String Time domain array"),

            OutputSource::PipelineResultValue(_) => write!(f, "Result"),
        }
    }
}

impl From<StandardPipeOutput> for OutputSource {
    fn from(standard_pipe: StandardPipeOutput) -> Self {
        match standard_pipe {
            StandardPipeOutput::Float64(subscriber ) => OutputSource::PipelineTDArrayFloat64(subscriber),
            StandardPipeOutput::Complex128(subscriber) => OutputSource::PipelineTDArrayComplex128(subscriber),

            StandardPipeOutput::Int64(subscriber ) => OutputSource::PipelineTDArrayInt64(subscriber),
            StandardPipeOutput::Int32(subscriber ) => OutputSource::PipelineTDArrayInt32(subscriber),
            StandardPipeOutput::Int16(subscriber ) => OutputSource::PipelineTDArrayInt16(subscriber),
            StandardPipeOutput::Int8(subscriber ) => OutputSource::PipelineTDArrayInt8(subscriber),

            StandardPipeOutput::UInt64(subscriber ) => OutputSource::PipelineTDArrayUInt64(subscriber),
            StandardPipeOutput::UInt32(subscriber ) => OutputSource::PipelineTDArrayUInt32(subscriber),
            StandardPipeOutput::UInt16(subscriber ) => OutputSource::PipelineTDArrayUInt16(subscriber),
            StandardPipeOutput::UInt8(subscriber ) => OutputSource::PipelineTDArrayUInt8(subscriber),

            //StandardPipeOutput::String(subscriber ) => OutputSource::PipelineTDArrayString(subscriber),
        }
    }
}

impl From<PipelineSubscriber<TimeDomainArrayReal>> for OutputSource {
    fn from(value: PipelineSubscriber<TimeDomainArrayReal>) -> Self {
        PipelineTDArrayFloat64(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArrayComplex>> for OutputSource {
    fn from(value: PipelineSubscriber<TimeDomainArrayComplex>) -> Self {
        OutputSource::PipelineTDArrayComplex128(value)
    }
}

impl From<PipelineSubscriber<FreqDomainArrayReal>> for OutputSource {
    fn from(value: PipelineSubscriber<FreqDomainArrayReal>) -> Self {
        PipelineFreqArrayFloat64(value)
    }
}

impl From<PipelineSubscriber<FreqDomainArrayComplex>> for OutputSource {
    fn from(value: PipelineSubscriber<FreqDomainArrayComplex>) -> Self {
        PipelineFreqArrayComplex128(value)
    }
}

impl From<PipelineSubscriber<ResultValue>> for OutputSource {
    fn from(value: PipelineSubscriber<ResultValue>) -> Self {
        PipelineResultValue(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArray<i64>>> for OutputSource{
    fn from(value: PipelineSubscriber<TimeDomainArray<i64>>) -> Self {
        PipelineTDArrayInt64(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArray<i32>>> for OutputSource{
    fn from(value: PipelineSubscriber<TimeDomainArray<i32>>) -> Self {
        PipelineTDArrayInt32(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArray<i16>>> for OutputSource {
    fn from(value: PipelineSubscriber<TimeDomainArray<i16>>) -> Self {
        OutputSource::PipelineTDArrayInt16(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArray<i8>>> for OutputSource {
    fn from(value: PipelineSubscriber<TimeDomainArray<i8>>) -> Self {
        OutputSource::PipelineTDArrayInt8(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArray<u64>>> for OutputSource {
    fn from(value: PipelineSubscriber<TimeDomainArray<u64>>) -> Self {
        OutputSource::PipelineTDArrayUInt64(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArray<u32>>> for OutputSource {
    fn from(value: PipelineSubscriber<TimeDomainArray<u32>>) -> Self {
        OutputSource::PipelineTDArrayUInt32(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArray<u16>>> for OutputSource {
    fn from(value: PipelineSubscriber<TimeDomainArray<u16>>) -> Self {
        OutputSource::PipelineTDArrayUInt16(value)
    }
}

impl From<PipelineSubscriber<TimeDomainArray<u8>>> for OutputSource {
    fn from(value: PipelineSubscriber<TimeDomainArray<u8>>) -> Self {
        OutputSource::PipelineTDArrayUInt8(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArrayReal, TimeDomainArrayReal)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArrayReal, TimeDomainArrayReal)>) -> Self {
        PipelineTDPairArrayFloat64(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArray<i64>, TimeDomainArray<i64>)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArray<i64>, TimeDomainArray<i64>)>) -> Self {
        PipelineTDPairArrayInt64(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArray<i32>, TimeDomainArray<i32>)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArray<i32>, TimeDomainArray<i32>)>) -> Self {
        OutputSource::PipelineTDPairArrayInt32(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArray<i16>, TimeDomainArray<i16>)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArray<i16>, TimeDomainArray<i16>)>) -> Self {
        OutputSource::PipelineTDPairArrayInt16(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArray<i8>, TimeDomainArray<i8>)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArray<i8>, TimeDomainArray<i8>)>) -> Self {
        OutputSource::PipelineTDPairArrayInt8(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArray<u64>, TimeDomainArray<u64>)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArray<u64>, TimeDomainArray<u64>)>) -> Self {
        OutputSource::PipelineTDPairArrayUInt64(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArray<u32>, TimeDomainArray<u32>)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArray<u32>, TimeDomainArray<u32>)>) -> Self {
        OutputSource::PipelineTDPairArrayUInt32(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArray<u16>, TimeDomainArray<u16>)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArray<u16>, TimeDomainArray<u16>)>) -> Self {
        OutputSource::PipelineTDPairArrayUInt16(value)
    }
}

impl From<PipelineSubscriber<(TimeDomainArray<u8>, TimeDomainArray<u8>)>> for OutputSource {
    fn from(value: PipelineSubscriber<(TimeDomainArray<u8>, TimeDomainArray<u8>)>) -> Self {
        OutputSource::PipelineTDPairArrayUInt8(value)
    }
}




impl OutputSource {

    /// copy any value except NDSBufferRX, which isn't cloneable.
    /// NDSBufferRX is changed to NotSet
    pub (crate) fn almost_copy(&self) -> Self {
        match self {
            NotSet => NotSet,
            OutputSource::BufferRx(_) => NotSet,
            PipelineTDArrayFloat64(x) => PipelineTDArrayFloat64(x.clone()),
            OutputSource::PipelineTDArrayComplex128(x) => OutputSource::PipelineTDArrayComplex128(x.clone()),
            PipelineFreqArrayFloat64(x) => PipelineFreqArrayFloat64(x.clone()),
            PipelineFreqArrayComplex128(x) => OutputSource::PipelineFreqArrayComplex128(x.clone()),
            PipelineResultValue(x) => PipelineResultValue(x.clone()),

            OutputSource::PipelineTDArrayInt64(x) => OutputSource::PipelineTDArrayInt64(x.clone()),
            OutputSource::PipelineTDArrayInt32(x) => OutputSource::PipelineTDArrayInt32(x.clone()),
            OutputSource::PipelineTDArrayInt16(x) => OutputSource::PipelineTDArrayInt16(x.clone()),
            OutputSource::PipelineTDArrayInt8(x) => OutputSource::PipelineTDArrayInt8(x.clone()),

            OutputSource::PipelineTDArrayUInt64(x) => OutputSource::PipelineTDArrayUInt64(x.clone()),
            OutputSource::PipelineTDArrayUInt32(x) => OutputSource::PipelineTDArrayUInt32(x.clone()),
            OutputSource::PipelineTDArrayUInt16(x) => OutputSource::PipelineTDArrayUInt16(x.clone()),
            OutputSource::PipelineTDArrayUInt8(x) => OutputSource::PipelineTDArrayUInt8(x.clone()),

            OutputSource::PipelineTDPairArrayFloat64(x) => OutputSource::PipelineTDPairArrayFloat64(x.clone()),
            OutputSource::PipelineTDPairArrayInt64(x) => OutputSource::PipelineTDPairArrayInt64(x.clone()),
            OutputSource::PipelineTDPairArrayInt32(x) => OutputSource::PipelineTDPairArrayInt32(x.clone()),
            OutputSource::PipelineTDPairArrayInt16(x) => OutputSource::PipelineTDPairArrayInt16(x.clone()),
            OutputSource::PipelineTDPairArrayInt8(x) => OutputSource::PipelineTDPairArrayInt8(x.clone()),
            OutputSource::PipelineTDPairArrayUInt64(x) => OutputSource::PipelineTDPairArrayUInt64(x.clone()),
            OutputSource::PipelineTDPairArrayUInt32(x) => OutputSource::PipelineTDPairArrayUInt32(x.clone()),
            OutputSource::PipelineTDPairArrayUInt16(x) => OutputSource::PipelineTDPairArrayUInt16(x.clone()),
            OutputSource::PipelineTDPairArrayUInt8(x) => OutputSource::PipelineTDPairArrayUInt8(x.clone()),

            //OutputSource::PipelineTDArrayString(x) => OutputSource::PipelineTDArrayString(x.clone()),
        }
    }

    #[allow(dead_code)]
    /// Creates a results pipeline subscriber
    pub (crate) async fn to_value_pipeline(&self, rc: &Box<RunContext>, name: impl Into<String>) -> Result<PipelineSubscriber<ResultValue>, DTTError>{
        match self {
            NotSet | OutputSource::BufferRx(_) =>
                Err(DTTError::AnalysisPipelineError("value_pipeline can only be created from another pipeline".to_string())),
            PipelineFreqArrayComplex128(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            PipelineFreqArrayFloat64(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            PipelineTDArrayFloat64(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDArrayComplex128(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },

            OutputSource::PipelineTDArrayInt64(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDArrayInt32(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDArrayInt16(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDArrayInt8(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },

            OutputSource::PipelineTDArrayUInt64(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDArrayUInt32(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDArrayUInt16(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDArrayUInt8(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDPairArrayFloat64(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            },
            OutputSource::PipelineTDPairArrayInt64(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            }
            OutputSource::PipelineTDPairArrayInt32(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            }
            OutputSource::PipelineTDPairArrayInt16(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            }
            OutputSource::PipelineTDPairArrayInt8(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            }
            OutputSource::PipelineTDPairArrayUInt64(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            }
            OutputSource::PipelineTDPairArrayUInt32(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            }
            OutputSource::PipelineTDPairArrayUInt16(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            }
            OutputSource::PipelineTDPairArrayUInt8(a) => {
                Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            }
            
            // OutputSource::PipelineTDArrayString(a) => {
            //     Ok( PureStatelessPipeline1::start(rc.ump_clone(), name, a, general::into::generate).await )
            // },
            
            OutputSource::PipelineResultValue(a) => Ok(a.clone()),
        }
    }
}

#[derive(Debug)]
pub (crate) struct AnalysisEdge {
    pub (crate) port: usize,
    pub (crate) result_type: EdgeDataType,
    pub (crate) output_source: OutputSource,
    pub (crate) results_wrapper: Option<EdgeResultsWrapper>,
}

impl AnalysisEdge {
    fn new(value: SchemeEdge, result_type: EdgeDataType) -> Self {
        Self {
            port: value.port,
            result_type,
            output_source: Default::default(),
            results_wrapper: value.result_wrapper,
        }
    }

    /// copy another edge, but fail if that edge has output_source == NDSBufferRX, which isn't
    /// cloneable
    fn almost_copy(&self) -> Self {
        Self {
            port: self.port,
            result_type: self.result_type.clone(),
            results_wrapper: self.results_wrapper.clone(),
            output_source: self.output_source.almost_copy(),


        }
    }

    /// If the output_source is NDSBufferRx, return the Receiver and set output_source to NotSet, otherwise return a copy
    /// of the output_source as an error so it can be printed out
    /// needed because the Receiver isn't cloneable.
    pub (crate) fn take_nds_buffer_rx(&mut self) -> Result<mpsc::Receiver<Buffer>, OutputSource> {
        let orig_out_source = std::mem::replace(&mut self.output_source, OutputSource::NotSet);
        let (new_source, result) = match orig_out_source {
            OutputSource::BufferRx(rx) => {
                (NotSet, Ok(rx))
            },
            s => (s.almost_copy(), Err(s))
        };

        self.output_source = new_source;

        result
    }
}

pub (crate) type AnalysisGraph<'a> = Graph<AnalysisNode<'a>, AnalysisEdge, Directed>;

pub (crate) fn extend_graph<'a>(base_graph: &'_ mut AnalysisGraph<'a>, base_map: &'_ mut HashMap<AnalysisNode<'a>, NodeIndex>,
                                     other_graph: &'_ AnalysisGraph<'a>) {

    // A mapping from node ids in other_graph to corresponding node ids in the base graph
    let mut idx_map = HashMap::new();

    for node_idx in other_graph.node_indices() {

        let node = other_graph.node_weight(node_idx).unwrap().clone();

        let base_idx = if base_map.contains_key(&node) {
            base_map.get(&node).unwrap().clone()
        }
        else {
            base_graph.add_node(node.clone())
        };

        base_map.insert(node, base_idx);

        idx_map.insert(node_idx, base_idx);
    }

    for edge_idx in other_graph.edge_indices() {
        let edge = other_graph.edge_weight(edge_idx).unwrap();
        let (source, target) = other_graph.edge_endpoints(edge_idx).unwrap();

        base_graph.add_edge(
            idx_map.get(&source).unwrap().clone(),
            idx_map.get(&target).unwrap().clone(),
            edge.almost_copy(),
        );
    };
}

pub (crate) fn set_result_types(graph: &mut AnalysisGraph) -> Result<(), DTTError> {
    let mut topo = Topo::new(&*graph);

    loop {
        let next = match topo.next(&*graph) {
            None => break,
            Some(n) => n,
        };
        determine_result_type(graph, next)?;
    }
    Ok(())
}

pub (crate) fn from_per_channel_scheme<'a>(channel: &'_ ChannelSettings, scheme_graph: &'_ SchemeGraph<'a>) -> Result<AnalysisGraph<'a>, DTTError>
{
    let mut new_graph = AnalysisGraph::new();
    let (nodes, edges) = scheme_graph.clone().into_nodes_edges();
    for node in nodes {
        let channels = match node.weight.pipeline_type {
            SchemePipelineType::Results | SchemePipelineType::DataSource => Vec::new(),
            _ => vec![channel.clone()],
        };

        new_graph.add_node(AnalysisNode::from_scheme_node(&node.weight, channels,
                                                          ));
    }
    for edge in edges {
        // set every edge to the same result type,
        // but we only really care about the DataSource -> Conditioning edge.
        // Every other edge will be set by determine_result_type()
        new_graph.add_edge(edge.source(), edge.target(),
                           AnalysisEdge::new(edge.weight,
                                             channel.data_type().into()));
    }

    // fix all types
    let mut topo = Topo::new(&new_graph);

    loop {
        let next = match topo.next(&new_graph) {
            None => break,
            Some(n) => n,
        };
        determine_result_type(&mut new_graph, next)?;
    }

    Ok(new_graph)
}

pub (crate) fn from_cross_channel_scheme<'a>(a_channel: &'_ ChannelSettings, b_channel: &'_ ChannelSettings,
                                             scheme_graph: &'_ SchemeGraph<'a>) -> Result<AnalysisGraph<'a>, DTTError> {
    let mut new_graph = AnalysisGraph::new();
    let (nodes, edges) = scheme_graph.clone().into_nodes_edges();
    for node in nodes {
        let channels = match node.weight.pipeline_type {
            SchemePipelineType::Results | SchemePipelineType::DataSource => Vec::new(),
            SchemePipelineType::PerChannelASource(_) => vec![a_channel.clone()],
            SchemePipelineType::PerChannelBSource(_) => vec![b_channel.clone()],
            _ => vec![a_channel.clone(), b_channel.clone()],
        };

        new_graph.add_node(AnalysisNode::from_scheme_node(&node.weight, channels,
        ));
    }

    for edge in edges {
        // for cross channel graphs, the initial edge types don't matter, since they will all be
        // set by determine_result_type()
        new_graph.add_edge(edge.source(), edge.target(),
                           AnalysisEdge::new(edge.weight,
                                             EdgeDataType::TimeDomainValueReal));
    }

    // fix all types
    let mut topo = Topo::new(&new_graph);

    loop {
        let next = match topo.next(&new_graph) {
            None => break,
            Some(n) => n,
        };
        determine_result_type(&mut new_graph, next)?;
    }

    Ok(new_graph)
}

/// produce a hashmap by node weight to node index
fn _node_map<'a,'b>(graph: &'a AnalysisGraph<'b>) -> HashMap<AnalysisNode<'b>, NodeIndex>
{
    let mut map = HashMap::new();

    for idx in graph.node_indices() {
        let node = graph.node_weight(idx).unwrap().clone();
        map.insert(node, idx);
    }
    map
}

/// Get the result types for the sources of a node,
/// Returning an error if the count of sources doesn't match the
/// given value
fn get_sources(graph: &AnalysisGraph, n: NodeIndex, num_sources: usize) -> Result<Vec<EdgeDataType>, DTTError> {
    let source_types: Vec<_> = graph.edges_directed(n, Direction::Incoming).map(|x|{
        x.weight().result_type.clone()
    }).collect();
    let pipe_type = graph.node_weight(n).unwrap().pipeline_type.clone();
    if source_types.len() != num_sources {
        let msg = format!("{} pipeline must have exactly {} input, but got {}", pipe_type, num_sources, source_types.len());
        return Err(DTTError::AnalysisPipelineError(msg));
    }
    Ok(source_types)
}

/// iterate through all output edges
/// and set the result type to the corresponding type
fn set_node_result_type(graph: &mut AnalysisGraph, n: NodeIndex, result_type: &EdgeDataType) {
    let out_edges: Vec<_> = graph.edges_directed(n, Direction::Outgoing)
        .map(|x|{x.id()}).collect();

    for edge in out_edges {
        graph[edge].result_type = result_type.clone();
    }
}

/// Set the result types correctly for a pipeline
/// Assumes source node types are already set
/// Also checks some constraints and will return a failure if they aren't met
fn determine_result_type(graph: & mut AnalysisGraph, n: NodeIndex) -> Result<(), DTTError> {
    let pipe_type = graph.node_weight(n).unwrap().pipeline_type.clone();
    let node_result_type = match pipe_type {
        SchemePipelineType::Results | SchemePipelineType::DataSource
        | SchemePipelineType::PerChannelBSource(_) | SchemePipelineType::PerChannelASource(_)
        => return Ok(()), // nothing to be done here
        SchemePipelineType::Conditioning => {
            let mut source_types = get_sources(graph, n, 1)?;
            let source_type = source_types.remove(0);
            if ! source_type.is_time_domain() {
                return Err(DTTError::AnalysisPipelineError(
                    "Channel conditioning pipelines only take time domain input".to_string()));
            }
            if graph.node_weight(n).unwrap().channels[0].do_heterodyne || source_type.is_complex() {
                EdgeDataType::TimeDomainValueComplex
            }
            else {
                EdgeDataType::TimeDomainValueReal
            }
        },
        SchemePipelineType::FFT => {
            let mut source_types = get_sources(graph, n, 1)?;
            let source_type = source_types.remove(0);
            if ! source_type.is_time_domain() {
                return Err(DTTError::AnalysisPipelineError(
                    "FFT pipeline only takes time domain input".to_string()));
            }
            EdgeDataType::FreqDomainValueComplex
        },
        SchemePipelineType::InlineFFT => {
            let mut source_types = get_sources(graph, n, 1)?;
            let source_type = source_types.remove(0);
            if ! source_type.is_time_domain() {
                return Err(DTTError::AnalysisPipelineError(
                    "InlineFFT pipeline only takes time domain input".to_string()));
            }
            EdgeDataType::FreqDomainValueComplex
        },
        SchemePipelineType::CSD => {
            let mut sources_types = get_sources(graph, n, 2)?;
            if sources_types[0] != sources_types[1] {
                return Err(DTTError::AnalysisPipelineError(
                    "CSD pipeline inputs must be the same type".to_string()
                ))
            }
            let source_type = sources_types.remove(0);
            match source_type {
                EdgeDataType::FreqDomainValueComplex => (),
                _ => {
                    return Err(DTTError::AnalysisPipelineError(
                        "CSD pipeline only takes complex frequency domain input".to_string()));
                }
            }
            EdgeDataType::FreqDomainValueComplex
        },
        SchemePipelineType::Real => {
            let mut sources_types = get_sources(graph, n, 1)?;
            let source_type = sources_types.remove(0);
            match source_type {
                EdgeDataType::FreqDomainValueComplex => (),
                _ => {
                    return Err(DTTError::AnalysisPipelineError(
                        "Real pipeline only takes complex frequency domain input".to_string()));
                }
            }
            EdgeDataType::FreqDomainValueReal
        },
        SchemePipelineType::Sqrt => {
            let mut sources_types = get_sources(graph, n, 1)?;
            let source_type = sources_types.remove(0);
            match source_type {
                EdgeDataType::FreqDomainValueComplex
                | EdgeDataType::FreqDomainValueReal
                | EdgeDataType::TimeDomainValueReal
                | EdgeDataType::TimeDomainValueComplex
                    => (),
                _ => {
                    return Err(DTTError::AnalysisPipelineError(
                        "Sqrt pipeline only takes real or complex floating point input".to_string()));
                }
            }
            source_type
        },
        SchemePipelineType::ASD => {
            let mut sources_types = get_sources(graph, n, 1)?;
            let source_type = sources_types.remove(0);
            match source_type {
                EdgeDataType::FreqDomainValueComplex => (),
                _ => {
                    return Err(DTTError::AnalysisPipelineError(
                        "ASD pipeline only takes complex frequency domain input".to_string()));
                }
            }
            EdgeDataType::FreqDomainValueReal
        },
        SchemePipelineType::TimeShift{shift: _} |
        SchemePipelineType::Average | 
        SchemePipelineType::Identity => {
            let mut source_types = get_sources(graph, n, 1)?;
            let source_type = source_types.remove(0);
            source_type
        },
        SchemePipelineType::Downsample => {
            let mut source_types = get_sources(graph, n, 1)?;
            let source_type = source_types.remove(0);
            match source_type {
                EdgeDataType::TimeDomainValueReal => EdgeDataType::TimeDomainMinMaxReal,
                EdgeDataType::TimeDomainValueInt64 => EdgeDataType::TimeDomainMinMaxInt64,
                EdgeDataType::TimeDomainValueInt32 => EdgeDataType::TimeDomainMinMaxInt32,
                EdgeDataType::TimeDomainValueInt16 => EdgeDataType::TimeDomainMinMaxInt16,
                EdgeDataType::TimeDomainValueInt8 => EdgeDataType::TimeDomainMinMaxInt8,
                EdgeDataType::TimeDomainValueUInt64 => EdgeDataType::TimeDomainMinMaxUInt64,
                EdgeDataType::TimeDomainValueUInt32 => EdgeDataType::TimeDomainMinMaxUInt32,
                EdgeDataType::TimeDomainValueUInt16 => EdgeDataType::TimeDomainMinMaxUInt16,
                EdgeDataType::TimeDomainValueUInt8 => EdgeDataType::TimeDomainMinMaxUInt8,
                _ => {
                    return Err(DTTError::AnalysisPipelineError(
                        "Downsample pipeline only takes real time-domain input".to_string()));
                }
            }
        }
        #[cfg(feature = "python-pipe")]
        SchemePipelineType::Custom(c) => {
            let source_types = get_sources(graph, n, c.inputs.len())?;
            c.determine_result_type(&source_types)
        },
        SchemePipelineType::Dummy(_) => {
            return Err(DTTError::AnalysisPipelineError("Dummy pipeline cannot produce a result".to_string()));
        }
        SchemePipelineType::Splice => {
            let mut source_types = get_sources(graph, n, 1)?;
            let source_type = source_types.remove(0);
            source_type.clone()
        }
    };
    set_node_result_type(graph, n, &node_result_type);
    Ok(())
}

/// graph name is for error reporting
fn check_duplicate_names(graph_name: &str, graph: &'_ SchemeGraph) -> Result<(), DTTError> {
    let mut names = HashSet::new();
    for node in graph.raw_nodes() {
        if names.contains(&node.weight.name) {
            return Err(DTTError::AnalysisPipelineError(format!("Duplicate node name '{}' in {} graph", node.weight.name, graph_name)));
        }
        names.insert(node.weight.name.clone());
    }
    Ok(())
}

/// test a per-channel scheme and a cross-channel scheme together
/// by creating two fake channels, then an analysis graph consisting of
/// two per-channel and one cross-channel in a single graph.
///
/// This would also be a great graph to send to the user
pub (crate) fn test_schemes<'a>(rc: Box<RunContext>, per_channel_scheme: &'_ SchemeGraph<'a>,
                    cross_channel_scheme: &'_ SchemeGraph<'a>) -> Result<AnalysisGraph<'a>, DTTError> {

    check_duplicate_names("per-channel scheme", per_channel_scheme)?;
    check_duplicate_names("cross-channel scheme", cross_channel_scheme)?;

    let a_chan = Channel::new("a_channel".to_string(), Float32, 0.0).into();


    let b_chan = Channel::new("b_channel".to_string(), Float32, 0.0).into();


    let channels = vec![a_chan, b_chan];

    let analysis_graph = create_analysis_graph(channels.as_slice(),
                                                   &per_channel_scheme, &cross_channel_scheme)?;

    check_graph_errors(rc, &analysis_graph)?;

    Ok(analysis_graph)
}

/// this function creates an analysis graph from
/// it's assumed that every pair of channels in channel get a set of cross pipelines
/// in both orderings!
///
/// We don't do a channel crossed with itself.
///
/// This is different from old DTT, where only some channels were A channels and other channels B channels
pub (crate) fn create_analysis_graph<'a>(channels: &'_ [ChannelSettings],
                                         per_channel: &'_ SchemeGraph<'a>, cross_channel: &'_ SchemeGraph<'a>)
                                         -> Result<AnalysisGraph<'a>, DTTError> {

    let  mut analysis_graph = AnalysisGraph::new();

    let mut node_map = HashMap::new();

    // create per-channel nodes
    for chan in channels {        
        let per_chan_graph = from_per_channel_scheme(chan, per_channel)?;
        extend_graph(&mut analysis_graph, &mut node_map, &per_chan_graph);
    }

    // create cross-channel nodes
    for a_chan in channels {
        for b_chan in channels {
            if a_chan != b_chan {
                let cross_chan_graph =
                    from_cross_channel_scheme(a_chan, b_chan, &cross_channel)?;
                extend_graph(&mut analysis_graph, &mut node_map, &cross_chan_graph);
            }
        }
    }
    
    set_result_types(&mut analysis_graph)?;

    Ok(analysis_graph)
}

fn check_graph_errors(rc: Box<RunContext>, graph: &AnalysisGraph) -> Result<(), DTTError> {
    // Check for errors
    // 1. A disconnected part of the graph.
    if connected_components(graph) > 1 {
        return Err(DTTError::AnalysisPipelineError("Disconnection found in analysis graph".to_string()))
    }

    // 2. A cycle in the graph.
    if let Err(c) = toposort(graph, None) {
        let cyc_node = graph.node_weight(c.node_id()).unwrap().clone();
        let msg = format!("The analysis pipelines contain a cycle.  Node {} depends on itself.", cyc_node.name);
        return Err(DTTError::AnalysisPipelineError(msg));
    }


    let mut no_output_warning = false;

    for node_idx in graph.node_indices() {

        let node = graph.node_weight(node_idx).unwrap();

        // 3. A source that's not a data source.
        let in_edges: Vec<_> = graph.edges_directed(node_idx,
                                            Direction::Incoming)
            .map(|x|{x.id ()}).collect();

        if in_edges.len() == 0 {
            match node.pipeline_type {
                SchemePipelineType::DataSource => (),
                _ => {
                    let msg = format!("Node {} needs inputs, but has none.", node.name);
                    return Err(DTTError::AnalysisPipelineError(msg));
                }
            }
        }

        // 5. Input ports that don't have exactly 1 input.
        let mut port_map = HashSet::new();
        match node.pipeline_type {
            SchemePipelineType::Results => (), // don't care about port numbers on the results node
            _ =>{
                for edge_idx in in_edges {
                    let edge = graph.edge_weight(edge_idx).unwrap();
                    let port_num = edge.port;
                    if port_map.contains(&port_num) {
                        let msg = format!("Node {} has more than one input to port {}", node.name, port_num);
                        return Err(DTTError::AnalysisPipelineError(msg));
                    } else {
                        port_map.insert(port_num);
                    }
                }
            }
        }

        if let Some(num_ports) = node.pipeline_type.port_count() {
            for p in 1..=num_ports {
                if !port_map.contains(&p) {
                    let msg = format!("Node {} is missing an input on port {}", node.name, p);
                    return Err(DTTError::AnalysisPipelineError(msg));
                }
            }
        }

        // 4. A sink that's not the result node
        let out_edges: Vec<_> = graph.edges_directed(node_idx, Direction::Outgoing)
            .map(|x|{x.id ()}).collect();

        if out_edges.len() == 0 {
            match node.pipeline_type {
                SchemePipelineType::Results => (),
                _ => {
                    let msg = format!("Node {} doesn't output to anything.", node.name);
                    no_output_warning = true;
                    rc.user_messages.set_warning("NoPipelineOutput", msg);
                },
            }
        }
    }

    if !no_output_warning {
        rc.user_messages.clear_message("NoPipelineOutput");
    }

    Ok(())
}