use std::hash::{Hash, Hasher};
use std::sync::Arc;
use std::ops::{Add, Mul};
use pipelines::{PipeData, PipeDataPrimitive};
#[cfg(any(feature = "python-pipe", feature = "python"))]
use pyo3::{
    Bound, FromPyObject, IntoPyObject, IntoPyObjectExt, PyAny, PyErr, PyResult, Python,
    types::{PyTuple},
};
#[cfg(any(feature = "python-pipe", feature = "python"))]
use pyo3_stub_gen::{PyStubType, TypeInfo};
#[cfg(any(feature = "python-pipe", feature = "python"))]
use crate::analysis::types::time_domain_array::PyTimeDomainArray;
use crate::{Accumulation, AccumulationStats};
use crate::analysis::types::time_domain_array::{TimeDomainArray};
use crate::errors::DTTError;
use crate::TimeDomainValue::FixedStepArrayPair;
use super::FixedStepArray;

/// Time domain results
#[derive(Clone, Debug)]
pub enum TimeDomainValue<T> {
    FixedStepArray(Arc<TimeDomainArray<T>>),
    FixedStepArrayPair(Arc<(TimeDomainArray<T>, TimeDomainArray<T>)>),
}

impl<T> From<Arc<TimeDomainArray<T>>> for TimeDomainValue<T> {
    fn from(arc: Arc<TimeDomainArray<T>>) -> Self {
        FixedStepArray(arc)
    }
}

impl<T> From<Arc<(TimeDomainArray<T>, TimeDomainArray<T>)>> for TimeDomainValue<T> {
    fn from(arc: Arc<(TimeDomainArray<T>, TimeDomainArray<T>)>) -> Self {
        FixedStepArrayPair(arc)
    }
}

impl<T> From<TimeDomainArray<T>> for TimeDomainValue<T> {
    fn from(value: TimeDomainArray<T>) -> Self {
        Arc::new(value).into()
    }
}

impl<T> From<(TimeDomainArray<T>, TimeDomainArray<T>)> for TimeDomainValue<T> {
    fn from(value: (TimeDomainArray<T>, TimeDomainArray<T>)) -> Self {
        FixedStepArrayPair(Arc::new(value))
    }
}

impl<T> PartialEq<Self> for TimeDomainValue<T> {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (FixedStepArray(f),
            FixedStepArray(g)) => f == g,
            (FixedStepArrayPair(f),
            FixedStepArrayPair(g)) => f == g,
            _ => false,
        }
    }
}

impl<T> Eq for TimeDomainValue<T> {

}

impl<T> Hash for TimeDomainValue<T> {

    /// hash the start time so different time slices are stored separately
    fn hash<H: Hasher>(&self, state: &mut H) {
        match self {
            FixedStepArray(t) => t.start_gps_pip.hash(state),
            FixedStepArrayPair(p) => p.0.start_gps_pip.hash(state),
        }
    }
}

/// needed for Average pipeline
impl<T> Add<&TimeDomainValue<T>> for TimeDomainValue<T>
where
    T: Copy + Add<T, Output = T>,
{

    type Output = Result<TimeDomainValue<T>, DTTError>;

    fn add(self, rhs: &TimeDomainValue<T>) -> Self::Output {
        match (self, rhs) {
            (FixedStepArray(a),
                FixedStepArray(b))
                => Ok((a.as_ref() + b.clone())?.into()) ,
            _ => {
              let msg = "Can only add singular, fixed step arrays".into();
              Err(DTTError::AnalysisPipelineError(msg))
            },
        }
    }
}

impl<T> Mul<f64> for TimeDomainValue<T>
where
    T: Copy + Mul<f64, Output = T>,
{
    type Output = TimeDomainValue<T>;

    fn mul(self, rhs: f64) -> Self::Output {
        match self {
            FixedStepArray(a) => (a.as_ref().clone() * rhs).into(),
            FixedStepArrayPair(p) => {
                let (a, b) = p.as_ref();
                (a.clone()*rhs, b.clone()*rhs).into()
            }
        }
    }
}

impl<T> PipeData for TimeDomainValue<T>
where
    T: PipeDataPrimitive
{

}

impl<T: Clone> Accumulation for TimeDomainValue<T> {
    fn set_accumulation_stats(& self, stats: AccumulationStats) -> Self {
        match self {
            FixedStepArray(t) => FixedStepArray(Arc::new(t.set_accumulation_stats(stats))),
            FixedStepArrayPair(p) => {
                let (a, b) = p.as_ref();
                FixedStepArrayPair(Arc::new((a.set_accumulation_stats(stats), b.clone()))).into()
            }
        }
    }

    fn get_accumulation_stats(&self) -> &AccumulationStats {
        match self {
            FixedStepArray(t) => t.get_accumulation_stats(),
            FixedStepArrayPair(p) => p.0.get_accumulation_stats(),
        }
    }
}

impl <T> TimeDomainValue<T> {
    pub fn len(&self) -> usize {
        match self {
            FixedStepArray(a) => a.len(),
            FixedStepArrayPair(p) => p.0.len(),
        }
    }
}

/// # Python interface
#[cfg(any(feature = "python-pipe", feature = "python"))]
impl<'py, T: PipeData> FromPyObject<'py> for TimeDomainValue<T> {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        TimeDomainArray::<T>::extract_bound(ob).map(|x| x.into())
    }
}

#[cfg(any(feature = "python-pipe", feature = "python"))]
impl<'py, T: PipeDataPrimitive> IntoPyObject<'py> for TimeDomainValue<T> {

    type Target = PyAny;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        match self {
            FixedStepArray(a)  => Ok(a.as_ref().clone().into_bound_py_any(py)?),
            FixedStepArrayPair(p) => {
                let (a,b) = p.as_ref();
                let tuple = vec![a.clone().into_bound_py_any(py)?, b.clone().into_bound_py_any(py)?];
                let pytuple = PyTuple::new(py, tuple)?;
                Ok(pytuple.into_any())
            }
        }
    }
}


#[cfg(any(feature = "python-pipe", feature = "python"))]
impl<T: PipeData> PyStubType for TimeDomainValue<T> {
    fn type_output() -> TypeInfo {
        PyTimeDomainArray::type_output()
    }
}