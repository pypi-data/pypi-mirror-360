use std::cmp::Ordering;
use std::hash::{Hash, Hasher};
use ligo_hires_gps_time::PipDuration;
use nds_cache_rs::buffer::Buffer;
#[cfg(any(feature = "python", feature = "python-pipe"))]
use pyo3::{
    pymethods,
    pyclass,
};
#[cfg(any(feature = "python", feature = "python-pipe"))]
use pyo3_stub_gen::{
    derive::{
        gen_stub_pyclass, gen_stub_pymethods,
    }
};
#[cfg(not(any(feature = "python", feature = "python-pipe")))]
use dtt_macros::{new, getter};
use crate::errors::DTTError;
use super::{ChannelSettings, NDSDataType, ChannelType, TrendType, TrendStat};


#[derive(Clone, Debug, Default)]
#[cfg_attr(any(feature = "python", feature = "python-pipe"), gen_stub_pyclass)]
#[cfg_attr(any(feature = "python", feature = "python-pipe"), pyclass(eq, get_all, hash, frozen))]
pub struct Channel {
    pub name: String,
    pub data_type: NDSDataType,
    pub channel_type: ChannelType,
    pub rate_hz: f64,
    pub dcu_id: Option<i64>,
    pub channel_number: Option<i64>,
    pub calibration: Option<i64>,
    pub heterodyne_freq_hz: Option<f64>,
    pub gain: Option<f64>,
    pub slope: Option<f64>,
    pub offset: Option<f64>,
    pub use_active_time: bool,
    pub units: Option<String>,

    // trend info

    pub trend_stat: TrendStat,
    pub trend_type: TrendType,
}


/// Identification and calibration data for a channel
/// The sort of info we might expect from a data server channel list.
impl Hash for Channel {
    /// always update hash and PartialEq::eq to use the same data subset
    fn hash<H: Hasher>(&self, state: &mut H) {
        // channel name
        self.name.hash(state);

        // rate
        // get period in pips_per_sec
        let period_pips = PipDuration::freq_hz_to_period(self.rate_hz);
        period_pips.hash(state);

        // type
        self.data_type.hash(state);

        // trend info
        self.trend_stat.hash(state);
        self.trend_type.hash(state);
    }
}

impl PartialEq<Self> for Channel {
    /// always update hash and PartialEq::eq to use the same data subset
    fn eq(&self, other: &Self) -> bool {

        let self_period_pips = PipDuration::freq_hz_to_period(self.rate_hz);
        let other_period_pips = PipDuration::freq_hz_to_period(other.rate_hz);

        (self.name == other.name)
            && (self_period_pips == other_period_pips)
            && (self.data_type == other.data_type)
            && (self.trend_stat == other.trend_stat)
            && (self.trend_type == other.trend_type)
    }
}

impl Eq for Channel {

}

#[cfg(feature = "nds")]
impl From<Channel> for nds2_client_rs::Channel {
    fn from(value: Channel) -> Self {
        Self {
            name: value.name,
            channel_type: value.channel_type.into(),
            data_type: value.data_type.into(),
            sample_rate: value.rate_hz,
            gain: value.gain.unwrap_or(1.0) as f32,
            slope: value.slope.unwrap_or(1.0) as f32,
            offset: value.offset.unwrap_or(0.0) as f32,
            units: value.units.unwrap_or("".to_string()),
        }
    }
}

impl From<Channel> for nds_cache_rs::buffer::Channel {
    fn from(value: Channel) -> Self {
        nds_cache_rs::buffer::Channel::new(
            value.name,
            nds_cache_rs::buffer::ChannelType::Raw,
            value.data_type.into(),
            value.rate_hz,
            value.gain.unwrap_or(1.0) as f32,
            value.slope.unwrap_or(1.0) as f32,
            value.offset.unwrap_or(0.0) as f32,
            value.units.unwrap_or(String::new()),
        )
    }
}

/// break down an NDS2 channel name into name, trend type, and trend stat
fn nds_name_to_name_and_trend(name: &str) -> Result<(String, TrendType, TrendStat), DTTError> {
    match name.rsplit_once('.') {
        Some((prefix, trend_info)) => {
            match trend_info.rsplit_once(',') {
                Some((stat, trend)) => {
                    Ok((prefix.to_string(), trend.try_into()?, stat.try_into()?))
                }
                None => Ok((name.to_string(), TrendType::Raw, TrendStat::Raw))
                // Err(DTTError::BadTrendSpecifier(trend_info.to_string(),not all channels
                //     "No comma found.\n\tMust be in the form <trend_stat>,<trend_type>".to_string(),
                //     name.to_string()
                // ))
            }
        }
        None => Ok((name.to_string(), TrendType::Raw, TrendStat::Raw))
    }
}

impl TryFrom<nds_cache_rs::buffer::Channel> for Channel {

    type Error = DTTError;

    fn try_from(value: nds_cache_rs::buffer::Channel) -> Result<Self, Self::Error> {

        let (name, trend_type, trend_stat) = nds_name_to_name_and_trend(value.name())?;

        Ok(Self {
            name,
            data_type: value.data_type().into(),
            channel_type: value.channel_type().into(),
            rate_hz: value.sample_rate().into(),
            gain: Some(value.gain() as f64),
            offset: Some(value.offset() as  f64),
            slope: Some(value.slope() as f64),
            units: Some(value.units().to_owned()),
            trend_type,
            trend_stat,
            ..Default::default()
        })
    }
}

impl TryFrom<&crate::data_source::buffer::Buffer> for Channel {
    type Error = DTTError;

    fn try_from(value: &crate::data_source::buffer::Buffer) -> Result<Self, Self::Error> {
        (&value.cache_buffer).try_into()        
    }
}

impl TryFrom<&Buffer> for Channel {
    type Error = DTTError;

    fn try_from(buffer: &Buffer) -> Result<Self, Self::Error> {
        buffer.channel().clone().try_into()
    }
}

impl From<ChannelSettings> for Channel {
    fn from(value: ChannelSettings) -> Self {
        value.channel
    }
}

impl PartialOrd for Channel {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        if self.name < other.name {
            Some(Ordering::Less)
        }
        else if self.name > other.name {
            Some(Ordering::Greater)
        }
        else if self.rate_hz < other.rate_hz {
            Some(Ordering::Less)
        }
        else if self.rate_hz > other.rate_hz {
            Some(Ordering::Greater)
        }
        else if self.data_type == other.data_type {
            Some(Ordering::Equal)
        }
        else {
            None
        }
    }
}

#[cfg_attr(any(feature = "python", feature = "python-pipe"), gen_stub_pymethods)]
#[cfg_attr(any(feature = "python", feature = "python-pipe"), pymethods)]
impl Channel {
    #[new]
    pub fn new(name: String, data_type: NDSDataType, rate_hz: f64) -> Self {
        Channel {
            name,
            data_type,
            rate_hz,
            ..Default::default()
        }
    }
    
    ///
    #[getter]
    pub fn online(&self) -> bool {
        self.channel_type == ChannelType::Online || self.channel_type == ChannelType::TestPoint
    }
    
    #[getter]
    pub fn testpoint(&self) -> bool {
        self.channel_type == ChannelType::TestPoint
    }
}