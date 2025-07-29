
pub mod channel;
pub mod nds_data_type;
pub (crate) mod decimation_parameters;
mod channel_settings;
mod channel_type;
pub (crate) mod channel_id;

use std::vec::IntoIter;
#[cfg(feature = "python")]
use pyo3::pyclass;
#[cfg(feature = "python")]
use pyo3_stub_gen::derive::gen_stub_pyclass;

pub use channel::Channel;
pub use nds_data_type::NDSDataType;
pub use channel_type::ChannelType;
pub use channel_id::{ChannelId, TrendType, TrendStat};

pub (crate) use channel_settings::ChannelSettings;

pub trait Activate {
    fn is_active(&self) -> bool;
}

#[cfg_attr(any(feature = "python"), gen_stub_pyclass)]
#[cfg_attr(any(feature = "python"), pyclass(get_all))]
#[derive(Clone, Debug)]
pub (crate) struct ChannelSettingsParams {
    pub active: bool,
    pub channel: ChannelSettings,
}

impl Activate for ChannelSettingsParams {
    fn is_active(&self) -> bool {
        self.active
    }
}

#[cfg_attr(any(feature = "python"), gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyclass(get_all))]
#[derive(Clone, Debug)]
pub struct ChannelParams {
    pub active: bool,
    pub channel: Channel,
}

impl Activate for ChannelParams {
    fn is_active(&self) -> bool {
        self.active
    }
}

impl From<ChannelParams> for ChannelSettingsParams {
    fn from(c: ChannelParams) -> Self {
        Self {
            active: c.active,
            channel: c.channel.into(),
        }
    }
}

pub trait ActiveList<T> {
    fn active_iter(&self) -> IntoIter<&T>;
}

impl <T> ActiveList<T> for Vec<T>
    where T: Activate {
    fn active_iter(&self) -> IntoIter<&T> {
        self.into_iter()
            .filter(|s|{(*s).is_active()})
            .collect::<Vec<&T>>().into_iter()
    }
}


