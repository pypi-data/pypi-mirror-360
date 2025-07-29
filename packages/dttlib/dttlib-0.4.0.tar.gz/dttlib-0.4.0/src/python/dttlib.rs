#![cfg(feature = "python")]
//! The python interface to the DTT library

use pyo3::{pymodule, wrap_pyfunction, Bound, PyResult};
use pyo3::prelude::{PyModule, PyModuleMethods};

use ligo_hires_gps_time::{PipDuration, PipInstant, ThumpDuration, ThumpInstant};
use crate::data_source::{
    ChannelQuery,
    nds_cache::{DataFlow, NDS2Cache}
};
use user_messages::{MessageJob, Severity, UserMessage};
use crate::params::channel_params::{Channel, NDSDataType, ChannelType, ChannelSettingsParams, ChannelId, ChannelParams, ChannelSettings, TrendType, TrendStat};
use crate::scope_view::{ScopeViewHandle, SetMember, ViewSet};
use crate::user::{ResponseToUser, DTT};
use crate::python::dtt_types::dtt_types;
use crate::default_fft_params;
use crate::analysis::result::AnalysisResult;
use crate::analysis::scope::inline_fft::InlineFFTParams;
use crate::analysis::types::frequency_domain_array::{PyFreqDomainArray};
use crate::analysis::types::time_domain_array::{PyTimeDomainArray};
use crate::gds_sigp::decimate::DecimationFilter;
use crate::params::custom_pipeline::CustomPipeline;
use crate::params::excitation_params::{Excitation, ExcitationParams, ExcitationSettings, ExcitationSettingsParams};
use crate::params::test_params::{AverageType, FFTWindow, StartTime, TestParams, TestType};


/// Module for analyzing LIGO data from Arrakis, NDS servers, and other soruces
#[pymodule]
fn dttlib(m: &Bound<'_, PyModule>) -> PyResult<()> {

    //when adding to this module, make sure to update dttlib.pyi in the root directory
    
    m.add_function(wrap_pyfunction!(default_fft_params, m)?)?;
    m.add_class::<AnalysisResult>()?;
    m.add_class::<AverageType>()?;
    m.add_class::<Channel>()?;
    m.add_class::<ChannelId>()?;
    m.add_class::<ChannelParams>()?;
    m.add_class::<ChannelQuery>()?;
    m.add_class::<ChannelSettings>()?;
    m.add_class::<ChannelSettingsParams>()?;
    m.add_class::<ChannelType>()?;
    m.add_class::<DataFlow>()?;
    m.add_class::<DecimationFilter>()?;
    m.add_class::<DTT>()?;
    m.add_class::<Excitation>()?;
    m.add_class::<ExcitationParams>()?;
    m.add_class::<ExcitationSettings>()?;
    m.add_class::<ExcitationSettingsParams>()?;
    m.add_class::<FFTWindow>()?;
    m.add_class::<PyFreqDomainArray>()?;
    m.add_class::<InlineFFTParams>()?;
    m.add_class::<MessageJob>()?;
    m.add_class::<NDS2Cache>()?;
    m.add_class::<NDSDataType>()?;
    m.add_class::<PipDuration>()?;
    m.add_class::<PipInstant>()?;
    m.add_class::<ResponseToUser>()?;
    m.add_class::<SetMember>()?;
    m.add_class::<Severity>()?;
    m.add_class::<ScopeViewHandle>()?;
    m.add_class::<StartTime>()?;
    m.add_class::<TestParams>()?;
    m.add_class::<TestType>()?;
    m.add_class::<ThumpDuration>()?;
    m.add_class::<ThumpInstant>()?;
    m.add_class::<PyTimeDomainArray>()?;
    m.add_class::<TrendType>()?;
    m.add_class::<TrendStat>()?;
    m.add_class::<UserMessage>()?;
    m.add_class::<ViewSet>()?;

    #[cfg(feature = "python-pipe")]
    m.add_class::<CustomPipeline>()?;



    let types = PyModule::new(m.py(), "types")?;
    dtt_types(&types)?;
    m.add_submodule(&types)?;
    Ok(())
}