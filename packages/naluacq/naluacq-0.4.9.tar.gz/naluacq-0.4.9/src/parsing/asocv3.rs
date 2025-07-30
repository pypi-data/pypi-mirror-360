use std::collections::HashSet;

use ndarray::{s, Array};

use crate::{acquisition::Params, error::ParsingError, Event};

use super::{
    util::{fetch_params_u16, fetch_params_usize, set_time_axis, AsU16BeExt},
    ParseInto, Result, Sample, TimeStamp, WindowLabel,
};

#[derive(Debug, Clone)]
pub struct Asocv3Event {
    data: Vec<Vec<Sample>>,
    window_labels: Vec<Vec<WindowLabel>>,
    time: Vec<Vec<TimeStamp>>,
    prev_final_window: WindowLabel,
    trigger_time_ns: u32,
    event_id: u16,
}

impl Asocv3Event {
    pub fn new(channels: usize) -> Self {
        Self {
            data: Vec::from_iter((0..channels).map(|_| Vec::new())),
            window_labels: Vec::from_iter((0..channels).map(|_| Vec::new())),
            time: Vec::from_iter((0..channels).map(|_| Vec::new())),
            prev_final_window: 0,
            trigger_time_ns: 0,
            event_id: 0,
        }
    }

    pub fn prev_final_window(&self) -> WindowLabel {
        self.prev_final_window
    }

    pub fn trigger_time_ns(&self) -> u32 {
        self.trigger_time_ns
    }

    pub fn event_id(&self) -> u16 {
        self.event_id
    }
}

impl Event for Asocv3Event {
    fn data(&self) -> &Vec<Vec<Sample>> {
        &self.data
    }

    fn data_mut(&mut self) -> &mut Vec<Vec<Sample>> {
        &mut self.data
    }

    fn window_labels(&self) -> &Vec<Vec<WindowLabel>> {
        &self.window_labels
    }

    fn time(&self) -> &Vec<Vec<TimeStamp>> {
        &self.time
    }
}

impl ParseInto<Asocv3Event> for [u8] {
    fn fast_validate(&self, params: &Params) -> Result<()> {
        if self.len() == 0 {
            return Err(ParsingError::MissingData);
        }
        if self.len() % 2 != 0 {
            return Err(ParsingError::UnexpectedLength);
        }
        let params = ParamsCache::from(params);
        if (self.len() / 2 - params.n_event_headers - 1) % (params.samples + 1) != 0 {
            return Err(ParsingError::UnexpectedLength);
        }
        Ok(())
    }

    fn parse_into(&self, params: &Params) -> Result<Asocv3Event> {
        <Self as ParseInto<Asocv3Event>>::fast_validate(&self, params)?;
        let cache: ParamsCache = params.into();

        let mut event = Asocv3Event::new(params.channels());
        parse_event_headers(&mut event, &self)?;

        let raw_event: Vec<u16> = self.iter().as_u16_be().collect();
        let data_end = raw_event.len() - cache.n_footers;
        let event_size = data_end - cache.n_event_headers + 1;
        let packet_size = cache.n_window_headers + cache.samples;
        if event_size % packet_size != 0 {
            return Err(ParsingError::UnexpectedLength);
        }
        let n_packets = event_size / packet_size;

        // SAFETY: unwrap() is safe because we have already checked that packet_size
        // evenly divides event_size.
        let packet_matrix = Array::<u16, _>::from_vec(raw_event);
        let packet_matrix = packet_matrix
            .slice(s![cache.n_event_headers..data_end + 1])
            .into_shape((n_packets, packet_size))
            .unwrap();
        let packet_matrix = packet_matrix.t();

        let channels = packet_matrix
            .slice(s![0, ..])
            .iter()
            .take(cache.channels)
            .map(|word| ((word & cache.channel_mask) >> cache.channel_shift) as usize)
            .collect::<HashSet<_>>();
        let mut channels = Vec::from_iter(channels.into_iter());
        channels.sort();
        for (i, channel) in channels.iter().enumerate() {
            let samples = packet_matrix
                .slice(s![1..packet_size, i..;channels.len()])
                .into_iter()
                .map(|word| ((*word & cache.data_bitmask) >> cache.n_last_bits) as Sample)
                .collect::<Vec<_>>();
            let window_labels = packet_matrix
                .slice(s![0, i..;channels.len()])
                .into_iter()
                .map(|word| ((*word & cache.window_mask) >> cache.n_last_bits) as WindowLabel)
                .collect::<Vec<_>>();
            *event
                .data
                .get_mut(*channel)
                .ok_or(ParsingError::InvalidChannel)? = samples;
            *event
                .window_labels
                .get_mut(*channel)
                .ok_or(ParsingError::InvalidChannel)? = window_labels;
        }
        set_time_axis(&mut event.time, &event.window_labels, params)?;

        Ok(event)
    }
}

fn parse_event_headers(event: &mut Asocv3Event, raw_event: &[u8]) -> Result<()> {
    if raw_event.len() < 3 {
        return Err(ParsingError::UnexpectedLength);
    }
    event.trigger_time_ns = ((raw_event[0] as u32 & 255) << 16)
        + ((raw_event[1] as u32) << 4)
        + (raw_event[2] as u32 % 255);
    event.prev_final_window = raw_event[2] as u16 & 255;
    Ok(())
}

struct ParamsCache {
    channels: usize,
    samples: usize,

    data_bitmask: u16,
    channel_mask: u16,
    channel_shift: u16,
    window_mask: u16,
    n_event_headers: usize,
    n_window_headers: usize,
    n_footers: usize,
    n_last_bits: usize,
}

impl From<&Params> for ParamsCache {
    fn from(params: &Params) -> Self {
        Self {
            channels: params.channels(),
            samples: params.samples(),
            data_bitmask: fetch_params_u16(params, "databitmask", 8191),
            channel_mask: fetch_params_u16(params, "chanmask", 1536),
            channel_shift: fetch_params_u16(params, "chan_shift", 9),
            window_mask: fetch_params_u16(params, "windmask", 510),
            n_event_headers: fetch_params_usize(params, "n_event_headers", 3),
            n_window_headers: fetch_params_usize(params, "n_window_headers", 1),
            n_footers: fetch_params_usize(params, "n_footers", 2),
            n_last_bits: fetch_params_usize(params, "n_last_bits", 1),
        }
    }
}
