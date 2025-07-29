//! Give the real value of a complex frequency domain input.

use std::sync::Arc;
use pipelines::complex::c128;
use pipelines::PipelineSubscriber;
use pipelines::stateless::pure::PureStatelessPipeline1;
use user_messages::UserMsgProvider;
use crate::analysis::types::frequency_domain_array::FreqDomainArray;

fn real(input: &FreqDomainArray<c128>) -> FreqDomainArray<f64> {
    let data = input.data.iter().map(|x|{x.re}).collect();
    input.clone_metadata(data)
}

fn generate(_rc: Box<dyn UserMsgProvider>, _name: String, input: Arc<FreqDomainArray<c128>>) -> Arc<FreqDomainArray<f64>> 
{
    let r = real(input.as_ref());
    Arc::new(r)
}


pub (crate) async fn create(rc: Box<dyn UserMsgProvider>, name: String, 
          input: &PipelineSubscriber<FreqDomainArray<c128>>) -> PipelineSubscriber<FreqDomainArray<f64>> {
    PureStatelessPipeline1::start(rc, name, input, generate).await
}