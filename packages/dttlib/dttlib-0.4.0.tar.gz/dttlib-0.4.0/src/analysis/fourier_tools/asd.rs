//! Calculate the ASD directly from an FFT
//! Since ASD should be calculated from a PSD, this should not be used.

/// Pipeline for calculating Asd from FFT
use std::sync::Arc;
use futures::FutureExt;
use pipeline_macros::box_async;
use pipelines::complex::c128;
use pipelines::{PipelineSubscriber, PipeResult};
use pipelines::stateless::Stateless1;
use user_messages::UserMsgProvider;
use crate::{Accumulation};
use crate::analysis::types::frequency_domain_array::FreqDomainArray;
use crate::gds_sigp::asd::asd;

#[derive(Clone, Debug)]
pub struct ASD {
    has_dc: bool
}

impl ASD {
    #[box_async]
    fn generate(_rc: Box<dyn UserMsgProvider>, _name: String, config: &Self, input: Arc<FreqDomainArray<c128>>)
    -> PipeResult<FreqDomainArray<f64>> {

        let a  = asd(input.data.as_slice(), config.has_dc);
        Arc::new(
            FreqDomainArray::new(
                input.start_gps_pip,
                input.start_hz,
                input.bucket_width_hz,
                input.overlap,
                a,
                input.get_accumulation_stats().clone(),
            )
        ).into()
    }

    pub async fn create(rc: Box<dyn UserMsgProvider>, name: impl Into<String>, has_dc: bool,
                        input: &PipelineSubscriber<FreqDomainArray<c128>>)
    -> PipelineSubscriber<FreqDomainArray<f64>> {

        let config = Self {
            has_dc,
        };

        Stateless1::create(rc, name.into(), Self::generate, config, input).await
    }
}