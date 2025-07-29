//! convert input type to output type using .into()
//! typically used to convert from a specific value type to an enum.
#![allow(dead_code)]

use std::sync::Arc;
use pipelines::PipeData;
use user_messages::UserMsgProvider;

pub fn generate<T, U> (_rc: Box<dyn UserMsgProvider>, _name: String, input: Arc<T>) -> Arc<U>
where
    T: PipeData,
    U: PipeData + From<T>
{
    Arc::new(U::from(input.as_ref().clone()))
}