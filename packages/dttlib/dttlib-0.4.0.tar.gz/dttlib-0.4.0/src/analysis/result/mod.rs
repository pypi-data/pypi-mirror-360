pub mod record;
pub (crate) mod time_domain_value;
pub (crate) mod freq_domain_value;
pub (crate) mod result_value;

use std::fmt::{Display, Formatter};
use std::hash::{Hash};
use std::sync::Arc;
use pipelines::complex::c128;
use pipelines::{PipeData, PipelineSubscriber};
use user_messages::UserMsgProvider;
use crate::analysis::types::frequency_domain_array::FreqDomainArray;
use crate::params::channel_params::{nds_data_type::NDSDataType};
use crate::run_context::RunContext;
use time_domain_value::TimeDomainValue::FixedStepArray;

#[cfg(feature = "python")]
use pyo3::pyclass;
#[cfg(feature = "python")]
use pyo3_stub_gen::{
    derive::gen_stub_pyclass_rich_enum,
};
use freq_domain_value::FreqDomainValue;
use result_value::ResultValue;
use time_domain_value::TimeDomainValue;
use crate::params::channel_params::channel::Channel;

/// Give the result that should be used if a particular edge is sending a result to the app
#[derive(Clone, Debug)]
#[allow(dead_code)]
pub (crate) enum EdgeResultsWrapper {
    TimeDomainReal,
    ASD,
    ResultValue,
}


impl Display for EdgeResultsWrapper {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::TimeDomainReal => f.write_str("TimeDomainReal"),
            Self::ASD => f.write_str("ASD"),
            Self::ResultValue => f.write_str("ResultValue"),
        }
    }
}


/// All analysis outputs are contained in the result type.
#[derive(Clone, Hash, Debug, PartialEq, Eq)]
#[cfg_attr(feature = "python", gen_stub_pyclass_rich_enum)]
#[cfg_attr(feature = "python", pyclass(str))]
pub enum AnalysisResult{
    Coherence{channel_a: Channel, channel_b: Channel, value: FreqDomainValue<f64>},
    TransferFunction{channel_a: Channel, channel_b: Channel, value: FreqDomainValue<c128>},
    ASD{channel: Channel, value: FreqDomainValue<f64>},
    TimeHistoryReal{channel: Channel, value: TimeDomainValue<f64>},
    TimeHistoryComplex{channel: Channel, value: TimeDomainValue<c128>},

    /// (source channels, custom pipeline name, value)
    Custom{channels: Vec<Channel>, pipeline_name: String, value: ResultValue},
}

impl AnalysisResult {

    pub (crate) async fn time_domain_real_wrapper<T>(rc: &Box<RunContext>, channel: Channel, input: &PipelineSubscriber<T>,
                                                     output: ResultsSender)
     where
         T: PipeData,
         Arc<T>: Into<TimeDomainValue<f64>>,
    {
        let mut inp_rx = input.subscribe_or_die(rc.ump_clone()).await;
        tokio::spawn(
            async move {
                'main: loop {
        
                    let result = match inp_rx.recv().await {
                        Some(r) => r,
                        None => break 'main,
                    };
        
                    let wrapped_result = AnalysisResult::TimeHistoryReal{channel: channel.clone(), value: result.value.into()};
        
                    if let Err(_) = output.send(wrapped_result).await {
                        break 'main;
                    }
                }
            }
        );
    }

    pub (crate) async fn asd_wrapper(rc: &Box<RunContext>, channel: Channel, input: &PipelineSubscriber<FreqDomainArray<f64>>,
                                     output: ResultsSender) {
        let mut inp_rx = input.subscribe_or_die(rc.ump_clone()).await;
        tokio::spawn(
            async move {
                'main: loop {
                    let result = match inp_rx.recv().await {
                        Some(r) => r,
                        None => break 'main,
                    };

                    let wrapped_result = AnalysisResult::ASD{
                        channel: channel.clone(),
                        value: FreqDomainValue::FixedStepArray(result.value)
                    };

                    if let Err(_) = output.send(wrapped_result).await {
                        break 'main;
                    }
                }
            }
        );
    }


    pub (crate) async fn result_value_wrapper(rc: &Box<RunContext>, channels: &[Channel], name: impl Into<String>, input: &PipelineSubscriber<ResultValue>,
                                              output: ResultsSender) {
        let mut inp_rx = input.subscribe_or_die(rc.ump_clone()).await;
        let name_string = name.into();
        let chans = Vec::from(channels);
        tokio::spawn(
            async move {
                'main: loop {
                    let result = match inp_rx.recv().await {
                        Some(r) => r,
                        None => break 'main,
                    };

                    let wrapped_result = AnalysisResult::Custom{channels: chans.clone(),
                                                                pipeline_name: name_string.clone(),
                                                                value: result.value.as_ref().clone()};

                    if let Err(_) = output.send(wrapped_result).await {
                        break 'main;
                    }
                }
            }
        );
    }
}

impl Display for AnalysisResult {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            AnalysisResult::TimeHistoryReal{channel, value} => {
                write!(f, "TimeHistoryReal({}, ... [{}]))", channel.name, value.len())
            },
            AnalysisResult::TimeHistoryComplex{channel, value} => {
                write!(f, "TimeHistoryComplex({}, ... [{}])", channel.name, value.len())
            },
            AnalysisResult::ASD{channel, value} => {
                write!(f, "ASD({}, ... [{}]))", channel.name, value.len())
            },
            AnalysisResult::Coherence{channel_a: c1, channel_b: c2, value} => {
                write!(f, "Coherence({}, {}, ... [{}]))", c1.name, c2.name, value.len())
            },
            AnalysisResult::Custom{channels, pipeline_name: name, value} => {
                let chans = channels.iter().map(|c|c.name.clone()).reduce(|a, b| format!("{}, {}", a, b)).unwrap_or("".to_string());
                write!(f, "Custom({}, {}, ... [{}]))", chans, name, value.len())
            },
            AnalysisResult::TransferFunction{channel_a: c1, channel_b: c2, value} => {
                write!(f, "TransferFunction({}, {}, ... [{}]))", c1.name, c2.name, value.len())
            }
        }
    }
}

// impl Mul<f64> for ResultValue {
//     type Output = ResultValue;
//
//     fn mul(self, rhs: f64) -> Self::Output {
//         match self {
//             TimeDomainValueReal(a) => TimeDomainValueReal(a * rhs),
//             TimeDomainValueComplex(a) => TimeDomainValueComplex(a * rhs),
//             TimeDomainValueInt64(a) => TimeDomainValueReal(a*rhs);
//
//
//
//             FreqDomainValueReal(a) => FreqDomainValueReal(a * rhs),
//             FreqDomainValueComplex(a) => FreqDomainValueComplex(a * rhs),
//         }
//     }
// }


/// an unencumbered simple enum of result type to help with
/// graphs of the analysis
#[allow(dead_code)]
#[derive(Clone, PartialEq, Eq, Debug)]
pub enum EdgeDataType {
    FreqDomainValueComplex,
    FreqDomainValueReal,
    TimeDomainValueReal,
    TimeDomainValueComplex,
    CustomFreqDomainReal,
    CustomFreqDomainComplex,

    TimeDomainValueInt64,
    TimeDomainValueInt32,
    TimeDomainValueInt16,
    TimeDomainValueInt8,

    TimeDomainValueUInt64,
    TimeDomainValueUInt32,
    TimeDomainValueUInt16,
    TimeDomainValueUInt8,

    TimeDomainValueString,

    TimeDomainMinMaxReal,
    TimeDomainMinMaxInt64,
    TimeDomainMinMaxInt32,
    TimeDomainMinMaxInt16,
    TimeDomainMinMaxInt8,
    TimeDomainMinMaxUInt64,
    TimeDomainMinMaxUInt32,
    TimeDomainMinMaxUInt16,
    TimeDomainMinMaxUInt8,
}

impl Display for EdgeDataType {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::FreqDomainValueComplex => write!(f, "FFT"),
            Self::FreqDomainValueReal => write!(f, "ASD"),
            Self::TimeDomainValueReal => write!(f, "Real-valued time-domain array"),
            Self::TimeDomainValueComplex => write!(f, "Complex-valued time-domain array"),
            Self::CustomFreqDomainComplex => write!(f, "Custom complex-valued frequency-domain array"),
            Self::CustomFreqDomainReal => write!(f, "Custom real-valued frequency-domain array"),
            Self::TimeDomainValueInt64 => write!(f, "64-bit integer time-domain array"),
            Self::TimeDomainValueInt32 => write!(f, "32-bit integer time-domain array"),
            Self::TimeDomainValueInt16 => write!(f, "16-bit integer time-domain array"),
            Self::TimeDomainValueInt8 => write!(f, "8-bit integer time-domain array"),
            Self::TimeDomainValueUInt64 => write!(f, "64-bit unsigned integer time-domain array"),
            Self::TimeDomainValueUInt32 => write!(f, "32-bit unsigned integer time-domain array"),
            Self::TimeDomainValueUInt16 => write!(f, "16-bit unsigned integer time-domain array"),
            Self::TimeDomainValueUInt8 => write!(f, "8-bit unsigned integer time-domain array"),
            Self::TimeDomainValueString => write!(f, "String time-domain array"),
            Self::TimeDomainMinMaxReal => write!(f, "Pair of real-valued time-domain arrays representing min and max"),
            Self::TimeDomainMinMaxInt64 => write!(f, "Pair of 64-bit integer time-domain arrays representing min and max"),
            Self::TimeDomainMinMaxInt32 => write!(f, "Pair of 32-bit integer time-domain arrays representing min and max"),
            Self::TimeDomainMinMaxInt16 => write!(f, "Pair of 16-bit integer time-domain arrays representing min and max"),
            Self::TimeDomainMinMaxInt8 => write!(f, "Pair of 8-bit integer time-domain arrays representing min and max"),
            Self::TimeDomainMinMaxUInt64 => write!(f, "Pair of 64-bit unsigned integer time-domain arrays representing min and max"),
            Self::TimeDomainMinMaxUInt32 => write!(f, "Pair of 32-bit unsigned integer time-domain arrays representing min and max"),
            Self::TimeDomainMinMaxUInt16 => write!(f, "Pair of 16-bit unsigned integer time-domain arrays representing min and max"),
            Self::TimeDomainMinMaxUInt8 => write!(f, "Pair of 8-bit unsigned integer time-domain arrays representing min and max"),
        }
    }
}

/// convert NDSDataType to a ResultType for a DataSource pipeline source
impl From<NDSDataType> for EdgeDataType {
    fn from(value: NDSDataType) -> Self {
        match value {
            NDSDataType::Complex64 | NDSDataType::Complex128 => Self::TimeDomainValueComplex,
            NDSDataType::Float64 | NDSDataType::Float32 => Self::TimeDomainValueReal,
            NDSDataType::Int64 => Self::TimeDomainValueInt64,
            NDSDataType::Int32 => Self::TimeDomainValueInt32,
            NDSDataType::Int16 => Self::TimeDomainValueInt16,
            NDSDataType::Int8 => Self::TimeDomainValueInt8,
            NDSDataType::UInt64 => Self::TimeDomainValueUInt64,
            NDSDataType::UInt32 => Self::TimeDomainValueUInt32,
            NDSDataType::UInt16 => Self::TimeDomainValueUInt16,
            NDSDataType::UInt8 => Self::TimeDomainValueUInt8,
            //NDSDataType::String => Self::TimeDomainValueString,
        }
    }
}

impl EdgeDataType {
    pub (crate) fn is_complex(&self) -> bool {
        match self {
            Self::CustomFreqDomainComplex | Self::FreqDomainValueComplex | Self::TimeDomainValueComplex => true,
            Self::CustomFreqDomainReal | Self::FreqDomainValueReal | Self::TimeDomainValueReal | Self::TimeDomainValueInt64
            | Self::TimeDomainMinMaxReal
            | Self::TimeDomainMinMaxInt64
            | Self::TimeDomainMinMaxInt32
            | Self::TimeDomainMinMaxInt16
            | Self::TimeDomainMinMaxInt8
            | Self::TimeDomainMinMaxUInt64
            | Self::TimeDomainMinMaxUInt32
            | Self::TimeDomainMinMaxUInt16
            | Self::TimeDomainMinMaxUInt8
            | Self::TimeDomainValueInt32
            | Self::TimeDomainValueInt16
            | Self::TimeDomainValueInt8
            | Self::TimeDomainValueUInt64
            | Self::TimeDomainValueUInt32
            | Self::TimeDomainValueUInt16
            | Self::TimeDomainValueUInt8
            | Self::TimeDomainValueString => false,
        }
    }

    #[allow(dead_code)]
    pub (crate) fn is_real(&self) -> bool {
        match self {
            Self::CustomFreqDomainComplex | Self::FreqDomainValueComplex | Self::TimeDomainValueComplex | Self::TimeDomainValueString => false,
            Self::CustomFreqDomainReal | Self::FreqDomainValueReal | Self::TimeDomainValueReal | Self::TimeDomainValueInt64
            | Self::TimeDomainMinMaxReal
            | Self::TimeDomainMinMaxInt64
            | Self::TimeDomainMinMaxInt32
            | Self::TimeDomainMinMaxInt16
            | Self::TimeDomainMinMaxInt8
            | Self::TimeDomainMinMaxUInt64
            | Self::TimeDomainMinMaxUInt32
            | Self::TimeDomainMinMaxUInt16
            | Self::TimeDomainMinMaxUInt8
            | Self::TimeDomainValueInt32
            | Self::TimeDomainValueInt16
            | Self::TimeDomainValueInt8
            | Self::TimeDomainValueUInt64
            | Self::TimeDomainValueUInt32
            | Self::TimeDomainValueUInt16
            | Self::TimeDomainValueUInt8 => true,
        }
    }

    pub (crate) fn is_time_domain(&self) -> bool {
        match self {
            Self::TimeDomainValueReal | Self::TimeDomainValueComplex
                | Self::TimeDomainValueInt64
                | Self::TimeDomainValueInt32
            | Self::TimeDomainValueInt16
            | Self::TimeDomainValueInt8
            | Self::TimeDomainValueUInt64
            | Self::TimeDomainValueUInt32
            | Self::TimeDomainValueUInt16
            | Self::TimeDomainValueUInt8
            | Self::TimeDomainValueString
            | Self::TimeDomainMinMaxReal
            | Self::TimeDomainMinMaxInt64
            | Self::TimeDomainMinMaxInt32
            | Self::TimeDomainMinMaxInt16
            | Self::TimeDomainMinMaxInt8
            | Self::TimeDomainMinMaxUInt64
            | Self::TimeDomainMinMaxUInt32
            | Self::TimeDomainMinMaxUInt16
            | Self::TimeDomainMinMaxUInt8
            => true,
            Self::CustomFreqDomainComplex | Self::CustomFreqDomainReal | Self::FreqDomainValueReal | Self::FreqDomainValueComplex => false,
        }
    }

    #[allow(dead_code)]
    pub (crate) fn is_freq_domain(&self) -> bool {
        match self {
            Self::TimeDomainValueReal | Self::TimeDomainValueComplex
            | Self::TimeDomainValueInt64
            | Self::TimeDomainValueInt32
            | Self::TimeDomainValueInt16
            | Self::TimeDomainValueInt8
            | Self::TimeDomainValueUInt64
            | Self::TimeDomainValueUInt32
            | Self::TimeDomainValueUInt16
            | Self::TimeDomainValueUInt8
            | Self::TimeDomainValueString
            | Self::TimeDomainMinMaxReal
            | Self::TimeDomainMinMaxInt64
            | Self::TimeDomainMinMaxInt32
            | Self::TimeDomainMinMaxInt16
            | Self::TimeDomainMinMaxInt8
            | Self::TimeDomainMinMaxUInt64
            | Self::TimeDomainMinMaxUInt32
            | Self::TimeDomainMinMaxUInt16
            | Self::TimeDomainMinMaxUInt8
            => false,
            Self::CustomFreqDomainComplex | Self::CustomFreqDomainReal | Self::FreqDomainValueComplex | Self::FreqDomainValueReal => true,
        }
    }
}


pub type ResultsSender = tokio::sync::mpsc::Sender<AnalysisResult>;
pub type ResultsReceiver = tokio::sync::mpsc::Receiver<AnalysisResult>;