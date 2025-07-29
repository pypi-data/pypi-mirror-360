//! convert from one type into another with possible failure,
//! that is, use .into() to convert to a Result<>
//! close the pipeline (and incidentally kill the test), if the conversion fails
#![allow(dead_code)]

use std::sync::Arc;
use futures::FutureExt;
use pipeline_macros::box_async;
use pipelines::{PipeData, PipeResult, PipelineSubscriber};
use pipelines::stateless::Stateless1;
use user_messages::UserMsgProvider;
use crate::errors::DTTError;

#[box_async]
fn generate<T, U>(rc: Box<dyn UserMsgProvider>, _name: String, _config: &(), input: Arc<T>) -> PipeResult<U>
where
    T: PipeData,
    U: PipeData,
    Result<U, DTTError>: From<T>
{
    let result: Result<U, DTTError> = input.as_ref().clone().into();
    match result {
        Ok(v) => v.into(),
        Err(e) => {
            let msg = format!("Bad conversion in a maybe_into pipeline: {}", e);
            rc.user_message_handle().error(msg);
            PipeResult::Close
        }
    }
}

pub async fn create<T,U>(rc: Box<dyn UserMsgProvider>, name: impl Into<String>, input: &PipelineSubscriber<T>) -> PipelineSubscriber<U> 
where
    T: PipeData,
    U: PipeData,
    Result<U, DTTError>: From<T>
{
    Stateless1::create(rc, name.into(), generate, (), input).await
}