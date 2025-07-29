//! This library implements a LIGO DTT kernel
//! The kernel is compatible with the real time system
//! NDS, NDS2, "ngdd" (next gen data delivery), and frame files
//! It's an async interface that internally runs on its own Tokio runtime.
#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(improper_ctypes)]

include!(concat!(env!("OUT_DIR"), "/bindings.rs"));
extern crate core;

pub mod params;
//mod time;
mod tokio_setup;
mod timeline;
pub mod user;
mod run_context;
mod errors;
mod constraints;
mod c_math;
mod run;
mod analysis;
mod gds_sigp;
pub mod data_source;
pub mod python;
pub mod scope_view;

use lazy_static::lazy_static;
use user::DTT;
use tokio_setup::tokio_init;
use crate::errors::DTTError;
pub use analysis::result::{
    record::ResultsRecord,
    AnalysisResult,
};
pub use crate::analysis::scope::inline_fft::InlineFFTParams;
use crate::user::UserOutputReceiver;
pub use analysis::types::{Accumulation, AccumulationStats};
pub use ligo_hires_gps_time::{PipDuration, PipInstant};

#[cfg(any(feature = "python", feature = "python-pipe"))]
use crate::python::python_init;
#[cfg(feature = "python")]
use pyo3::{
    pyfunction
};


pub use analysis::result::freq_domain_value::FreqDomainValue;
pub use analysis::result::result_value::ResultValue;
pub use analysis::result::time_domain_value::TimeDomainValue;

// python stub generation
#[cfg(feature = "python")]
pyo3_stub_gen::define_stub_info_gatherer!(stub_info);


/// # initialization
/// Initialize the library
/// Call once before use.
/// A call to init should be paired with a call to shutdown()
/// When the UserContext object is no longer needed.
pub fn init(runtime: &tokio::runtime::Handle) -> Result<(DTT, UserOutputReceiver), DTTError> {
    #[cfg(any(feature="python-pipe", feature = "python"))]
    python_init()?;
    tokio_init(runtime)
}

/// Initialize using the existing async runtime
/// caller should eventually call shutdown on the returned user context
pub async fn init_async() -> Result<(DTT, UserOutputReceiver), DTTError> {
    init(&tokio::runtime::Handle::current())
}


lazy_static!(
    static ref INTERNAL_RUNTIME: tokio::runtime::Runtime = tokio::runtime::Runtime::new().unwrap();
);

/// Initialize on the internal runtime
/// caller should eventually call shutdown on the returned user context
pub fn init_internal_runtime() -> Result<(DTT, UserOutputReceiver), DTTError>
{
    init(INTERNAL_RUNTIME.handle())
}

pub fn shutdown(_uc: & mut DTT) {

}

/// # setting parameters
///
/// generate an fft_params structure with default values
/// use the function to future-proof your structure
/// when new parameters are added code that doesn't set them will still work
#[cfg_attr(feature = "python", pyfunction)]
pub fn default_fft_params() -> params::test_params::TestParams {
    params::test_params::TestParams::default_fft_params()
}

