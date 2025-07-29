use std::collections::{HashSet};
#[cfg(feature = "python")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pyclass_rich_enum, gen_stub_pymethods};
#[cfg(feature = "python")]
use pyo3::{pyclass, pymethods};
#[cfg(not(feature = "python"))]
use dtt_macros::{
    staticmethod,
};
use crate::data_source::DataBlock;
use crate::params::channel_params::{Channel, ChannelId, TrendType};
use crate::params::channel_params::channel_id::ChannelHeader;

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
#[cfg_attr(feature = "python", gen_stub_pyclass_rich_enum)]
#[cfg_attr(feature = "python", pyclass)]
pub enum SetMember {
    Channel(Channel),
    //Function(String, Vec<isize>),
}


#[derive(Clone, Debug)]
#[cfg_attr(feature = "python", gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyclass)]
pub struct ViewSet {
    members: HashSet<SetMember>,

    /// Index map by of expected channel name to source channel name that's not resolved.
    unresolved_chans: HashSet<ChannelHeader>,
}

impl From<ViewSet> for Vec<Channel> {
    fn from(value: ViewSet) -> Self {
        let mut cvec = Vec::new();
        for m in value.members {
            let SetMember::Channel(c) =  m;
            cvec.push(c);
        }
        cvec
    }
}

impl From<Vec<Channel>> for ViewSet {
    fn from(value: Vec<Channel>) -> Self {
        Self {
            members: value.into_iter().map(|c| { SetMember::Channel(c) }).collect(),
            unresolved_chans: HashSet::new()
        }
    }
}

impl From<Vec<ChannelId>> for ViewSet {
    fn from(value: Vec<ChannelId>) -> Self {

        let mut unresolved_chans = HashSet::new();
        value.into_iter().for_each(|c| { unresolved_chans.extend(c.to_channel_headers()) });

        Self {
            members: HashSet::new(),
            unresolved_chans,
        }
    }
}

#[cfg_attr(feature = "python", gen_stub_pymethods)]
#[cfg_attr(feature = "python", pymethods)]
impl ViewSet {

    /// convenience function
    /// for turning a simple list of channels into a ViewSet
    #[staticmethod]
    pub fn from_channels(channels: Vec<Channel>) -> Self {
        channels.into()
    }

    /// convenience function
    /// for turning a simple list of channel names into a ViewSet with
    /// unresolved channel names
    #[staticmethod]
    pub fn from_channel_names(channel_names: Vec<String>, trend: TrendType) -> Self {
        let ids: Vec<_> = channel_names.into_iter().map(|n| ChannelId::new(n, trend.clone())).collect();
        ids.into()
    }


    pub fn has_unresolved_channels(&self) -> bool {
        !self.unresolved_chans.is_empty()
    }

    /// Return the resolved names of any channels in the set
    /// Including expected resolved names of unresolved channels.
    pub fn to_resolved_channel_names(&self) -> Vec<String> {


        let mut headers: Vec<ChannelHeader> = self.members.iter()
            .map(|m|
                match m {
                    SetMember::Channel(c) => {c.into()}
                }
            ).collect();

        headers.extend(self.unresolved_chans.iter().map(|c| c.clone()));

        headers.iter().map(|c| c.nds_name()).collect()
    }
}

impl ViewSet {

    /// Change any unresolved channel names to resolved channels.
    pub (super) async fn resolve_channels(&mut self, block: DataBlock) -> Option<DataBlock> {
        println!("resolve channels on a block");
        for channel in block.keys() {
            println!("looking for channel {}:{}", channel.name, channel.trend_stat);
            let header = channel.into();
            if self.unresolved_chans.contains(&header) {
                self.unresolved_chans.remove(&header);
                self.members.insert(SetMember::Channel(channel.clone()));
            }
        }

        if self.has_unresolved_channels() {
            None
        } else {
            Some(block)
        }
    }
}