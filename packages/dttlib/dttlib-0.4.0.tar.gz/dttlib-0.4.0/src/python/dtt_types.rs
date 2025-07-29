//! DTT data types needed to process DTT inputs and create DTT outputs
//! On user Python code run from Rust.

use pyo3::{
    pymodule,
    Bound,
    PyResult,
    types::{
        PyModule,
        PyModuleMethods
    }
};
use crate::analysis::types::frequency_domain_array::PyFreqDomainArray;
use crate::errors::DTTError;

#[pymodule]
pub (crate) fn dtt_types(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFreqDomainArray>()?;
    Ok(())
}

#[cfg(feature = "python-pipe")]
pub (crate) fn dtt_types_init() -> Result<(), DTTError> {
    #[cfg(not(feature = "python"))]
    pyo3::append_to_inittab!(dtt_types);
    Ok(())
}