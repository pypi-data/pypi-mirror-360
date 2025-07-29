use pipelines::complex::c128;
use std::ops::Add;
use std::sync::Arc;
use pipelines::PipeData;
#[cfg(any(feature = "python-pipe", feature = "python"))]
use pyo3::{
    Bound, FromPyObject, IntoPyObject, IntoPyObjectExt, PyAny, PyErr, PyResult, Python,

    exceptions::PyException,
    prelude::{PyAnyMethods, PyTypeMethods},
    types::PyTuple,
};
#[cfg(any(feature = "python-pipe", feature = "python"))]
use pyo3_stub_gen::{PyStubType, TypeInfo};
#[cfg(any(feature = "python-pipe", feature = "python"))]
use crate::analysis::types::frequency_domain_array::PyFreqDomainArray;
use crate::analysis::types::frequency_domain_array::{FreqDomainArrayComplex, FreqDomainArrayReal};
use crate::analysis::types::time_domain_array::{TimeDomainArray, TimeDomainArrayComplex, TimeDomainArrayReal};
use crate::errors::DTTError;
use crate::{Accumulation, AccumulationStats, FreqDomainValue, TimeDomainValue};
use crate::ResultValue::{FreqDomainValueComplex, FreqDomainValueReal, TimeDomainPairInt16, TimeDomainPairInt32, TimeDomainPairInt64, TimeDomainPairInt8, TimeDomainPairReal, TimeDomainPairUInt16, TimeDomainPairUInt32, TimeDomainPairUInt64, TimeDomainPairUInt8, TimeDomainValueComplex, TimeDomainValueInt16, TimeDomainValueInt32, TimeDomainValueInt64, TimeDomainValueInt8, TimeDomainValueReal, TimeDomainValueUInt16, TimeDomainValueUInt32, TimeDomainValueUInt64, TimeDomainValueUInt8};

/// A generic results value
/// Could be used in custom pipelines for example
#[derive(Clone, Hash, Debug, PartialEq, Eq)]
pub enum
ResultValue {
    FreqDomainValueReal(FreqDomainValue<f64>),
    FreqDomainValueComplex(FreqDomainValue<c128>),
    TimeDomainValueReal(TimeDomainValue<f64>),
    TimeDomainValueComplex(TimeDomainValue<c128>),

    TimeDomainValueInt64(TimeDomainValue<i64>),
    TimeDomainValueInt32(TimeDomainValue<i32>),
    TimeDomainValueInt16(TimeDomainValue<i16>),
    TimeDomainValueInt8(TimeDomainValue<i8>),

    TimeDomainValueUInt64(TimeDomainValue<u64>),
    TimeDomainValueUInt32(TimeDomainValue<u32>),
    TimeDomainValueUInt16(TimeDomainValue<u16>),
    TimeDomainValueUInt8(TimeDomainValue<u8>),

    TimeDomainPairReal((TimeDomainValue<f64>, TimeDomainValue<f64>)),
    TimeDomainPairInt64((TimeDomainValue<i64>, TimeDomainValue<i64>)),
    TimeDomainPairInt32((TimeDomainValue<i32>, TimeDomainValue<i32>)),
    TimeDomainPairInt16((TimeDomainValue<i16>, TimeDomainValue<i16>)),
    TimeDomainPairInt8((TimeDomainValue<i8>, TimeDomainValue<i8>)),
    TimeDomainPairUInt64((TimeDomainValue<u64>, TimeDomainValue<u64>)),
    TimeDomainPairUInt32((TimeDomainValue<u32>, TimeDomainValue<u32>)),
    TimeDomainPairUInt16((TimeDomainValue<u16>, TimeDomainValue<u16>)),
    TimeDomainPairUInt8((TimeDomainValue<u8>, TimeDomainValue<u8>)),

    //TimeDomainValueString(TimeDomainValue<String>),
}

impl From<FreqDomainValue<f64>> for ResultValue {
    fn from(value: FreqDomainValue<f64>) -> Self {
        FreqDomainValueReal(value)
    }
}

impl From<FreqDomainValue<c128>> for ResultValue {
    fn from(value: FreqDomainValue<c128>) -> Self {
        FreqDomainValueComplex(value)
    }
}

impl From<TimeDomainValue<f64>> for ResultValue {
    fn from(value: TimeDomainValue<f64>) -> Self {
        TimeDomainValueReal(value)
    }
}

impl From<TimeDomainValue<c128>> for ResultValue {
    fn from(value: TimeDomainValue<c128>) -> Self {
        TimeDomainValueComplex(value)
    }
}

impl From<TimeDomainValue<i64>> for ResultValue {
    fn from(value: TimeDomainValue<i64>) -> Self {
        TimeDomainValueInt64(value)
    }
}

impl From<TimeDomainValue<i32>> for ResultValue {
    fn from(value: TimeDomainValue<i32>) -> Self {
        TimeDomainValueInt32(value)
    }
}

impl From<TimeDomainValue<i16>> for ResultValue {
    fn from(value: TimeDomainValue<i16>) -> Self {
        TimeDomainValueInt16(value)
    }
}

impl From<TimeDomainValue<i8>> for ResultValue {
    fn from(value: TimeDomainValue<i8>) -> Self {
        TimeDomainValueInt8(value)
    }
}

impl From<TimeDomainValue<u64>> for ResultValue {
    fn from(value: TimeDomainValue<u64>) -> Self {
        TimeDomainValueUInt64(value)
    }
}

impl From<TimeDomainValue<u32>> for ResultValue {
    fn from(value: TimeDomainValue<u32>) -> Self {
        TimeDomainValueUInt32(value)
    }
}

impl From<TimeDomainValue<u16>> for ResultValue {
    fn from(value: TimeDomainValue<u16>) -> Self {
        TimeDomainValueUInt16(value)
    }
}

impl From<TimeDomainValue<u8>> for ResultValue {
    fn from(value: TimeDomainValue<u8>) -> Self {
        TimeDomainValueUInt8(value)
    }
}


impl From<(TimeDomainValue<f64>, TimeDomainValue<f64>)> for ResultValue {
    fn from(value: (TimeDomainValue<f64>, TimeDomainValue<f64>)) -> Self {
        TimeDomainPairReal(value)
    }
}

impl From<(TimeDomainValue<i64>, TimeDomainValue<i64>)> for ResultValue {
    fn from(value: (TimeDomainValue<i64>, TimeDomainValue<i64>)) -> Self {
        TimeDomainPairInt64(value)
    }
}

impl From<(TimeDomainValue<i32>, TimeDomainValue<i32>)> for ResultValue {
    fn from(value: (TimeDomainValue<i32>, TimeDomainValue<i32>)) -> Self {
        TimeDomainPairInt32(value)
    }
}

impl From<(TimeDomainValue<i16>, TimeDomainValue<i16>)> for ResultValue {
    fn from(value: (TimeDomainValue<i16>, TimeDomainValue<i16>)) -> Self {
        TimeDomainPairInt16(value)
    }
}

impl From<(TimeDomainValue<i8>, TimeDomainValue<i8>)> for ResultValue {
    fn from(value: (TimeDomainValue<i8>, TimeDomainValue<i8>)) -> Self {
        TimeDomainPairInt8(value)
    }
}

impl From<(TimeDomainValue<u64>, TimeDomainValue<u64>)> for ResultValue {
    fn from(value: (TimeDomainValue<u64>, TimeDomainValue<u64>)) -> Self {
        TimeDomainPairUInt64(value)
    }
}

impl From<(TimeDomainValue<u32>, TimeDomainValue<u32>)> for ResultValue {
    fn from(value: (TimeDomainValue<u32>, TimeDomainValue<u32>)) -> Self {
        TimeDomainPairUInt32(value)
    }
}

impl From<(TimeDomainValue<u16>, TimeDomainValue<u16>)> for ResultValue {
    fn from(value: (TimeDomainValue<u16>, TimeDomainValue<u16>)) -> Self {
        TimeDomainPairUInt16(value)
    }
}

impl From<(TimeDomainValue<u8>, TimeDomainValue<u8>)> for ResultValue {
    fn from(value: (TimeDomainValue<u8>, TimeDomainValue<u8>)) -> Self {
        TimeDomainPairUInt8(value)
    }
}

// impl From<TimeDomainValue<String>> for ResultValue {
//     fn from(value: TimeDomainValue<String>) -> Self {
//         Self::TimeDomainValueString(value)
//     }
// }

impl From<TimeDomainArrayReal> for ResultValue {
    fn from(value: TimeDomainArrayReal) -> Self {
        let v: TimeDomainValue<f64> = value.into();
        v.into()
    }
}

impl From<TimeDomainArray<i64>> for ResultValue {
    fn from(value: TimeDomainArray<i64>) -> Self {
        let v: TimeDomainValue<i64> = value.into();
        v.into()
    }
}

impl From<TimeDomainArray<i32>> for ResultValue {
    fn from(value: TimeDomainArray<i32>) -> Self {
        let v: TimeDomainValue<i32> = value.into();
        v.into()
    }
}

impl From<TimeDomainArray<i16>> for ResultValue {
    fn from(value: TimeDomainArray<i16>) -> Self {
        let v: TimeDomainValue<i16> = value.into();
        v.into()
    }
}

impl From<TimeDomainArray<i8>> for ResultValue {
    fn from(value: TimeDomainArray<i8>) -> Self {
        let v: TimeDomainValue<i8> = value.into();
        v.into()
    }
}

impl From<TimeDomainArray<u64>> for ResultValue {
    fn from(value: TimeDomainArray<u64>) -> Self {
        let v: TimeDomainValue<u64> = value.into();
        v.into()
    }
}

impl From<TimeDomainArray<u32>> for ResultValue {
    fn from(value: TimeDomainArray<u32>) -> Self {
        let v: TimeDomainValue<u32> = value.into();
        v.into()
    }
}

impl From<TimeDomainArray<u16>> for ResultValue {
    fn from(value: TimeDomainArray<u16>) -> Self {
        let v: TimeDomainValue<u16> = value.into();
        v.into()
    }
}

impl From<TimeDomainArray<u8>> for ResultValue {
    fn from(value: TimeDomainArray<u8>) -> Self {
        let v: TimeDomainValue<u8> = value.into();
        v.into()
    }
}

// impl From<TimeDomainArray<String>> for ResultValue {
//     fn from(value: TimeDomainArray<String>) -> Self {
//         let v: TimeDomainValue<String> = value.into();
//         v.into()
//     }
// }

impl From<TimeDomainArrayComplex> for ResultValue {
    fn from(value: TimeDomainArrayComplex) -> Self {
        let v: TimeDomainValue<c128> = value.into();
        v.into()
    }
}

impl From<FreqDomainArrayReal> for ResultValue {
    fn from(value: FreqDomainArrayReal) -> Self {
        let v: FreqDomainValue<f64> = value.into();
        v.into()
    }
}

impl From<FreqDomainArrayComplex> for ResultValue {
    fn from(value: FreqDomainArrayComplex) -> Self {
        let v: FreqDomainValue<c128> = value.into();
        v.into()
    }
}

impl From<(TimeDomainArrayReal, TimeDomainArrayReal)> for ResultValue {
    fn from(value: (TimeDomainArrayReal, TimeDomainArrayReal)) -> Self {
        let v: (TimeDomainValue<f64>, TimeDomainValue<f64>) = (value.0.into(), value.1.into());
        v.into()
    }
}

impl From<(TimeDomainArray<i64>, TimeDomainArray<i64>)> for ResultValue {
    fn from(value: (TimeDomainArray<i64>, TimeDomainArray<i64>)) -> Self {
        let v: (TimeDomainValue<i64>, TimeDomainValue<i64>) = (value.0.into(), value.1.into());
        v.into()
    }
}

impl From<(TimeDomainArray<i32>, TimeDomainArray<i32>)> for ResultValue {
    fn from(value: (TimeDomainArray<i32>, TimeDomainArray<i32>)) -> Self {
        let v: (TimeDomainValue<i32>, TimeDomainValue<i32>) = (value.0.into(), value.1.into());
        v.into()
    }
}

impl From<(TimeDomainArray<i16>, TimeDomainArray<i16>)> for ResultValue {
    fn from(value: (TimeDomainArray<i16>, TimeDomainArray<i16>)) -> Self {
        let v: (TimeDomainValue<i16>, TimeDomainValue<i16>) = (value.0.into(), value.1.into());
        v.into()
    }
}

impl From<(TimeDomainArray<i8>, TimeDomainArray<i8>)> for ResultValue {
    fn from(value: (TimeDomainArray<i8>, TimeDomainArray<i8>)) -> Self {
        let v: (TimeDomainValue<i8>, TimeDomainValue<i8>) = (value.0.into(), value.1.into());
        v.into()
    }
}

impl From<(TimeDomainArray<u64>, TimeDomainArray<u64>)> for ResultValue {
    fn from(value: (TimeDomainArray<u64>, TimeDomainArray<u64>)) -> Self {
        let v: (TimeDomainValue<u64>, TimeDomainValue<u64>) = (value.0.into(), value.1.into());
        v.into()
    }
}

impl From<(TimeDomainArray<u32>, TimeDomainArray<u32>)> for ResultValue {
    fn from(value: (TimeDomainArray<u32>, TimeDomainArray<u32>)) -> Self {
        let v: (TimeDomainValue<u32>, TimeDomainValue<u32>) = (value.0.into(), value.1.into());
        v.into()
    }
}

impl From<(TimeDomainArray<u16>, TimeDomainArray<u16>)> for ResultValue {
    fn from(value: (TimeDomainArray<u16>, TimeDomainArray<u16>)) -> Self {
        let v: (TimeDomainValue<u16>, TimeDomainValue<u16>) = (value.0.into(), value.1.into());
        v.into()
    }
}

impl From<(TimeDomainArray<u8>, TimeDomainArray<u8>)> for ResultValue {
    fn from(value: (TimeDomainArray<u8>, TimeDomainArray<u8>)) -> Self {
        let v: (TimeDomainValue<u8>, TimeDomainValue<u8>) = (value.0.into(), value.1.into());
        v.into()
    }
}


/// Make linear
impl Add<Arc<ResultValue>> for ResultValue {

    type Output = Result<Self, DTTError>;

    fn add(self, rhs: Arc<ResultValue>) -> Self::Output {
        match (self, rhs.as_ref()) {
            (TimeDomainValueReal(a), TimeDomainValueReal(b))
                => Ok((a + b)?.into()),
            (TimeDomainValueComplex(a), TimeDomainValueComplex(b))
                => Ok((a + b)?.into()),
            (FreqDomainValueComplex(a), FreqDomainValueComplex(b))
            => Ok((a + b)?.into()),
            (FreqDomainValueReal(a), FreqDomainValueReal(b))
                => Ok((a + b)?.into()),
            _ => Err(DTTError::AnalysisPipelineError("Mismatched types in Results Value addition".to_string())),
        }
    }
}

impl PipeData for ResultValue {

}

impl Accumulation for ResultValue {
    fn set_accumulation_stats(& self, stats: AccumulationStats) -> Self {
        match self {
            TimeDomainValueReal(t) => TimeDomainValueReal(t.set_accumulation_stats(stats)),
            TimeDomainValueComplex(t) => TimeDomainValueComplex(t.set_accumulation_stats(stats)),
            FreqDomainValueComplex(f) => FreqDomainValueComplex(f.set_accumulation_stats(stats)),
            FreqDomainValueReal(f) => FreqDomainValueReal(f.set_accumulation_stats(stats)),


            TimeDomainValueInt64(f) => TimeDomainValueInt64(f.set_accumulation_stats(stats)),
            TimeDomainValueInt32(f) => TimeDomainValueInt32(f.set_accumulation_stats(stats)),
            TimeDomainValueInt16(f) => TimeDomainValueInt16(f.set_accumulation_stats(stats)),
            TimeDomainValueInt8(f) => TimeDomainValueInt8(f.set_accumulation_stats(stats)),

            TimeDomainValueUInt64(f) => TimeDomainValueUInt64(f.set_accumulation_stats(stats)),
            TimeDomainValueUInt32(f) => TimeDomainValueUInt32(f.set_accumulation_stats(stats)),
            TimeDomainValueUInt16(f) => TimeDomainValueUInt16(f.set_accumulation_stats(stats)),
            TimeDomainValueUInt8(f) => TimeDomainValueUInt8(f.set_accumulation_stats(stats)),

            TimeDomainPairReal((a,b)) => TimeDomainPairReal((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),
            TimeDomainPairInt64((a,b)) => TimeDomainPairInt64((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),
            TimeDomainPairInt32((a,b)) => TimeDomainPairInt32((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),
            TimeDomainPairInt16((a,b)) => TimeDomainPairInt16((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),
            TimeDomainPairInt8((a,b)) => TimeDomainPairInt8((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),
            TimeDomainPairUInt64((a,b)) => TimeDomainPairUInt64((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),
            TimeDomainPairUInt32((a,b)) => TimeDomainPairUInt32((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),
            TimeDomainPairUInt16((a,b)) => TimeDomainPairUInt16((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),
            TimeDomainPairUInt8((a,b)) => TimeDomainPairUInt8((a.set_accumulation_stats(stats), b.set_accumulation_stats(stats))),

            //ResultValue::TimeDomainValueString(f) => ResultValue::TimeDomainValueString(f.set_accumulation_stats(stats)),
        }
    }

    fn get_accumulation_stats(&self) -> &AccumulationStats {
        match self {
            TimeDomainValueReal(t) => t.get_accumulation_stats(),
            TimeDomainValueComplex(t) => t.get_accumulation_stats(),
            FreqDomainValueComplex(f) => f.get_accumulation_stats(),
            FreqDomainValueReal(f) => f.get_accumulation_stats(),

            TimeDomainValueInt64(t) => t.get_accumulation_stats(),
            TimeDomainValueInt32(t) => t.get_accumulation_stats(),
            TimeDomainValueInt16(t) => t.get_accumulation_stats(),
            TimeDomainValueInt8(t) => t.get_accumulation_stats(),

            TimeDomainValueUInt64(t) => t.get_accumulation_stats(),
            TimeDomainValueUInt32(t) => t.get_accumulation_stats(),
            TimeDomainValueUInt16(t) => t.get_accumulation_stats(),
            TimeDomainValueUInt8(t) => t.get_accumulation_stats(),

            TimeDomainPairReal((a,_)) => a.get_accumulation_stats(),
            TimeDomainPairInt64((a,_)) => a.get_accumulation_stats(),
            TimeDomainPairInt32((a,_)) => a.get_accumulation_stats(),
            TimeDomainPairInt16((a,_)) => a.get_accumulation_stats(),
            TimeDomainPairInt8((a,_)) => a.get_accumulation_stats(),
            TimeDomainPairUInt64((a,_)) => a.get_accumulation_stats(),
            TimeDomainPairUInt32((a,_)) => a.get_accumulation_stats(),
            TimeDomainPairUInt16((a,_)) => a.get_accumulation_stats(),
            TimeDomainPairUInt8((a,_)) => a.get_accumulation_stats(),

            //ResultValue::TimeDomainValueString(t) => t.get_accumulation_stats(),
        }
    }
}

impl ResultValue {
    pub fn len(&self) -> usize {
        match self {
            TimeDomainValueReal(t) => t.len(),
            TimeDomainValueComplex(t) => t.len(),
            FreqDomainValueComplex(f) => f.len(),
            FreqDomainValueReal(f) => f.len(),

            TimeDomainValueInt64(t) => t.len(),
            TimeDomainValueInt32(t) => t.len(),
            TimeDomainValueInt16(t) => t.len(),
            TimeDomainValueInt8(t) => t.len(),

            TimeDomainValueUInt64(t) => t.len(),
            TimeDomainValueUInt32(t) => t.len(),
            TimeDomainValueUInt16(t) => t.len(),
            TimeDomainValueUInt8(t) => t.len(),

            TimeDomainPairReal((a,_)) => a.len(),
            TimeDomainPairInt64((a,_)) => a.len(),
            TimeDomainPairInt32((a,_)) => a.len(),
            TimeDomainPairInt16((a,_)) => a.len(),
            TimeDomainPairInt8((a,_)) => a.len(),
            TimeDomainPairUInt64((a,_)) => a.len(),
            TimeDomainPairUInt32((a,_)) => a.len(),
            TimeDomainPairUInt16((a,_)) => a.len(),
            TimeDomainPairUInt8((a,_)) => a.len(),

            //ResultValue::TimeDomainValueString(t) => t.len(),
        }
    }
}

/// # Python implementation
#[cfg(any(feature = "python-pipe", feature = "python"))]
impl<'py> FromPyObject<'py> for ResultValue {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let type_name_res = Python::with_gil(|py| {
            ob.get_type().name()?.unbind().extract::<String>(py)
        })?;

        if type_name_res == "FreqDomainArray" {
            PyFreqDomainArray::extract_result_value(ob)
        }
        else {
            Err(PyErr::new::<PyException, _>(format!("Could convert type {} to ResultValue", type_name_res)))
        }
    }
}

#[cfg(any(feature = "python-pipe", feature = "python"))]
impl<'py> IntoPyObject<'py> for ResultValue {

    type Target = PyAny;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        match self {
            FreqDomainValueReal(v) => Ok(v.into_bound_py_any(py)?),
            FreqDomainValueComplex(v) => Ok(v.into_bound_py_any(py)?),
            TimeDomainValueReal(v) => Ok(v.into_bound_py_any(py)?),
            TimeDomainValueComplex(v) => Ok(v.into_bound_py_any(py)?),

            TimeDomainValueInt64(v) => Ok(v.into_bound_py_any(py)?),
            TimeDomainValueInt32(v) => Ok(v.into_bound_py_any(py)?),
            TimeDomainValueInt16(v) => Ok(v.into_bound_py_any(py)?),
            TimeDomainValueInt8(v) => Ok(v.into_bound_py_any(py)?),

            TimeDomainValueUInt64(v) => Ok(v.into_bound_py_any(py)?),
            TimeDomainValueUInt32(v) => Ok(v.into_bound_py_any(py)?),
            TimeDomainValueUInt16(v) => Ok(v.into_bound_py_any(py)?),
            TimeDomainValueUInt8(v) => Ok(v.into_bound_py_any(py)?),

            TimeDomainPairReal((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            },
            TimeDomainPairInt64((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            }
            TimeDomainPairInt32((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            }
            TimeDomainPairInt16((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            }
            TimeDomainPairInt8((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            }
            TimeDomainPairUInt64((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            }
            TimeDomainPairUInt32((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            }
            TimeDomainPairUInt16((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            }
            TimeDomainPairUInt8((a, b)) => {
                let tup = vec![a.into_bound_py_any(py)?, b.into_bound_py_any(py)?];
                let pytup = PyTuple::new(py, tup)?;
                Ok(pytup.into_any())
            }




            //ResultValue::TimeDomainValueString(v) => Ok(v.into_bound_py_any(py)?),
        }
    }
}

/// Sub parts of a ResultsValue implement this to create a ResultsValue object from the corresponding python object
/// Used to handle return values from user defined functions.
#[cfg(any(feature = "python-pipe", feature = "python"))]
pub (crate) trait PyIntoResultValue<'py>
{
    fn extract_result_value(ob: &Bound<'py, PyAny>) -> PyResult<ResultValue>;
}

#[cfg(any(feature = "python-pipe", feature = "python"))]
impl PyStubType for ResultValue {
    fn type_output() -> TypeInfo {
        TypeInfo::any()
    }
}