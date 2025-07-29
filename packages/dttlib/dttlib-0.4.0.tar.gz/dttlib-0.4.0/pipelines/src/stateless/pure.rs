//! Pure stateless pipelines can be created with only a function from output type and input type
//! 


use std::sync::Arc;
use futures::future::BoxFuture;
use futures::FutureExt;
use tokio::runtime::Handle;
use user_messages::UserMsgProvider;
use crate::{PipeData, PipelineOutput, PipelineSubscriber, PipeResult};
use crate::stateless::{ Stateless1, Stateless2};

/// # One input pipelines
type Pipe1GenFn<T, U> = fn (Box<dyn UserMsgProvider>, String, Arc<T>) -> Arc<U>;

#[derive(Debug, Clone)]
pub struct PureStatelessPipeline1<T: PipeData, U: PipeData> {

     generate_ptr: Pipe1GenFn<T, U>,
}

impl<T: PipeData, U: PipeData> PureStatelessPipeline1<T, U> {


    fn generate(rc: Box<dyn UserMsgProvider>, name: String, config: &Self,
                input: PipelineOutput<T>) -> BoxFuture<PipeResult<U>> {
        async move {
        let g = config.generate_ptr;
        let inp = input.clone();
        let jh = Handle::current().spawn_blocking(
            move || {
                g(rc, name, inp.value)
            }
        );
        let value = jh.await.unwrap();
        vec!{value}.into()
    }.boxed() }

    pub async fn start(rc: Box<dyn UserMsgProvider>, name: impl Into<String>, input: &PipelineSubscriber<T>,
                       generate: Pipe1GenFn<T, U>) -> PipelineSubscriber<U> {
        let config = PureStatelessPipeline1 {
            generate_ptr: generate,
        };
        Stateless1::create(rc, name.into(), Self::generate, config, input).await
    }
}


/// # Two input pipelines
type Pipe2GenFn<T, S, U> = fn (Box<dyn UserMsgProvider>, String, Arc<T>, Arc<S>) -> Arc<U>;

#[derive(Clone, Debug)]
pub struct PureStatelessPipeline2<T: PipeData, S: PipeData, U: PipeData> {

    generate_ptr: Pipe2GenFn<T, S, U>,
}

impl<T: PipeData, S: PipeData, U: PipeData> PureStatelessPipeline2<T, S, U> {
    fn generate(rc: Box< dyn UserMsgProvider>, name: String, config: &Self,
                input1: PipelineOutput<T>, input2: PipelineOutput<S>) -> BoxFuture<PipeResult<U>> {
        async move {
            let g = config.generate_ptr;
            let inp1 = input1.clone();
            let inp2 = input2.clone();
            let jh = Handle::current().spawn_blocking(
                move || {
                    g(rc, name, inp1.value, inp2.value)
                }
            );
            let value = jh.await.unwrap();
            value.into()
        }.boxed() }

    pub async fn start(rc: Box<dyn UserMsgProvider>, name: impl Into<String>, input1: &PipelineSubscriber<T>, input2: &PipelineSubscriber<S>,
                       generate: Pipe2GenFn<T, S, U>) -> PipelineSubscriber<U> {
        let config = PureStatelessPipeline2 {
            generate_ptr: generate,
        };
        Stateless2::create(rc, name.into(), Self::generate, config, input1, input2).await
    }
}
