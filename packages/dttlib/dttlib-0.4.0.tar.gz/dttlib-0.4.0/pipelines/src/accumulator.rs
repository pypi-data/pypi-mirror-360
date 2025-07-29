//! Implement pure pipelines that that
//! can be implemented with a single function from output to input.
//!
//! Except for the Accumulator, this is probably superseded by stateless/pure which does the same thing but
//! potentially can run in parallel with multithreaded async runtimes
//!
//! This pipeline will only calculate one value at function call at a time.

use std::sync::Arc;
use futures::future::BoxFuture;
use futures::FutureExt;
use tokio::runtime::Handle;
use crate::{PipeData, PipelineOutput, PipelineSubscriber, PipeResult};
use crate::pipe::Pipe1;
use user_messages::UserMsgProvider;


type AccumGenFn<I, T, U> = fn (Box<dyn UserMsgProvider>, Arc<I>, Option<Arc<T>>, n: f64) -> (Arc<T>, f64, PipeResult<U>);

/// # Accumulator
/// a 1-input accumulator produces its new value for each segment as a pipeline output
/// an average or sum could be created with an accumulator, for example
#[derive(Debug, Clone)]
pub struct Accumulator<I: PipeData, T: PipeData, U: PipeData> {
    generate_ptr: AccumGenFn<I, T, U>,
    value: Option<Arc<T>>,
    n: f64,
}

fn accum_generate<I: PipeData, T:PipeData, U: PipeData>(rc: Box<dyn UserMsgProvider>, state: &mut Accumulator<I,T, U>,
                                           input: PipelineOutput<I>) -> BoxFuture<PipeResult<U>> {

    async move {
        let g = state.generate_ptr;
        let inp = input.clone();
        let accum_val = state.value.clone();
        let n = state.n;
        let jh = Handle::current().spawn_blocking(
            move || {
                g(rc, inp.value, accum_val, n)
            }
        );
        let (value, new_n, output) = jh.await.unwrap();
        state.n = new_n;
        state.value = Some(value.clone());
        output
    }.boxed()
}


impl<I: PipeData, T: PipeData, U: PipeData> Accumulator<I, T, U> {
    pub async fn start(rc: Box<dyn UserMsgProvider>, name: String, input: &PipelineSubscriber<I>,
                       generate: AccumGenFn<I, T, U>) -> PipelineSubscriber<U> {
        let p = Accumulator {
            n: 1.0,  // start at 1.  The generator is responsible for incrementing if needed.
            generate_ptr: generate,
            value: None,
        };
        Pipe1::create(rc, name, accum_generate::<I,T,U>, p, None, None, input).await
    }
}

