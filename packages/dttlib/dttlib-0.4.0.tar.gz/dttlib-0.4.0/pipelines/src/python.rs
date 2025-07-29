//! A pipe that runs a python function as a generator
#![cfg(feature = "python")]


use futures::FutureExt;
use std::sync::Arc;
use pyo3::prelude::*;
use pipeline_macros::box_async;
use user_messages::UserMsgProvider;
use crate::{PipeData, PipelineSubscriber, PipeResult};
use crate::pipe::Pipe1;

pub struct PythonPipeState {
    python_fn: Py<PyAny>,
}

impl PythonPipeState {
    #[box_async]
    fn generate<'a, T: PipeData, U: PipeData>(_rc: Box<dyn UserMsgProvider>,  state: &mut PythonPipeState,
                                              input: Arc<T>) -> PipeResult<U>
    {
        Python::with_gil(|py| {
            let kwargs = pyo3::types::PyDict::new(py);
            kwargs.set_item("input", input.as_ref().clone()).unwrap();

            let py_val = state.python_fn.call(py, (), Some(&kwargs)).unwrap();
            let rv: U = py_val.extract(py).unwrap();
            rv.into()
        })
    }


    pub async fn create<T, U>(
        rc: Box<dyn UserMsgProvider>,
        name: impl Into<String>, py_module: &Py<PyModule>, input: &PipelineSubscriber<T>
    ) -> PipelineSubscriber<U>
    where
        T: PipeData,
        U: PipeData
    {
        let pyfun: Py<PyAny> = Python::with_gil(|py| {
            py_module.bind(py).getattr("dtt_generate").unwrap().into()
        });


        let state = PythonPipeState {
            python_fn: pyfun,
        };

        Pipe1::create(rc, name.into(), PythonPipeState::generate, state, None, None, input).await
    }
}


#[cfg(test)]
mod tests {
    use std::ffi::{CString};
    use std::time::Duration;
    use user_messages::TestUserMessageProvider;
    use crate::PipelineOutput;
    use crate::tests::DataSource;
    use super::*;

    const SEGMENT_COUNT: u64 = 10;
    const NEAR_PI: f64 = std::f64::consts::PI;

    #[test]
    fn python_pipe_test() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        let rc = Box::new(
            rt.block_on(TestUserMessageProvider::default() )
        );

        pyo3::prepare_freethreaded_python();

        let py_module = Python::with_gil(|py| {
            PyModule::from_code(
                py,
                CString::new("def dtt_generate(input): return input * input").unwrap().as_ref(),
                CString::new("").unwrap().as_ref(),
                CString::new("").unwrap().as_ref()
            ).unwrap().unbind()
        });

        let mut py_out  = {
            let pr =
                rt.block_on(async {DataSource::start(rc.ump_clone(), NEAR_PI, SEGMENT_COUNT) });

            rt.block_on(
                async {
                    PythonPipeState::create::<f64, f64>(rc.ump_clone(), "python_pipe", &py_module, &pr).await.subscribe_or_die(rc.ump_clone()).await
                }
            )
        };

        let mut result: Vec<f64> = Vec::new();

        rt.block_on(async{
            loop {
                tokio::select! {
                    _ = tokio::time::sleep(Duration::from_secs(2)) => {
                        panic!("ran out of time waiting for python pipeline to finish")
                    },
                    m = py_out.recv() => {
                        match m {
                            Some(PipelineOutput{value: v}) => {
                                result.push(*v.as_ref());
                            },
                            None => break,
                        }
                    },
                }
            }
        });

        let target: Vec<f64> = (0..SEGMENT_COUNT).map(|i|{
            let x = i as f64 * NEAR_PI;
            x * x
        }).collect();

        assert_eq!(target, result);
    }
}