//! shift start time
//! this is functionally different from timedelay how?
//! yet cds-crtools channelinput.cc process() does both
//! ### References
//! 1. cds-crtools channelinput.cc process()
//!    https://git.ligo.org/cds/software/dtt/-/blob/4.1.1/src/dtt/storage/channelinput.cc#L702

use std::sync::Arc;
use futures::FutureExt;
use pipeline_macros::box_async;
use pipelines::{PipelineSubscriber, PipeResult, PipeDataPrimitive};
use pipelines::stateless::Stateless1;
use user_messages::UserMsgProvider;
use crate::analysis::types::time_domain_array::TimeDomainArray;
use ligo_hires_gps_time::PipDuration;

#[box_async]
fn time_shift_gen<T: PipeDataPrimitive>(_rc: Box<dyn UserMsgProvider>, _name: String, time_shift_pip: &PipDuration,
                           input: Arc<TimeDomainArray<T>>) -> PipeResult<TimeDomainArray<T>> {
    let mut new_array = input.as_ref().clone();
    let ts = time_shift_pip.clone();
    new_array.start_gps_pip -= ts;
    new_array.into()
}

pub (crate) async fn start_timeshift<T: PipeDataPrimitive>(rc: Box<dyn UserMsgProvider>, name: impl Into<String>,
                                    time_shift_pip: PipDuration, input: &PipelineSubscriber<TimeDomainArray<T>>)
-> PipelineSubscriber<TimeDomainArray<T>> {
    Stateless1::create(rc, name.into(), time_shift_gen, time_shift_pip, input).await
}