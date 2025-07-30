use std::collections::HashMap;

use crate::{acquisition::Params, error::ParsingError, Event};

use super::{
    util::{fetch_params_u16, fetch_params_usize, set_time_axis, AsU16BeExt},
    ParseInto, Result, Sample, TimeStamp, WindowLabel,
};

pub type WindowTiming = u16;

#[derive(Debug, Clone)]
pub struct Asocv3SEvent {
    data: Vec<Vec<Sample>>,
    window_labels: Vec<Vec<WindowLabel>>,
    time: Vec<Vec<TimeStamp>>,
    window_timings: Vec<WindowTiming>,
}

impl Asocv3SEvent {
    pub fn new(channels: usize) -> Self {
        Self {
            data: Vec::from_iter((0..channels).map(|_| Vec::new())),
            window_labels: Vec::from_iter((0..channels).map(|_| Vec::new())),
            time: Vec::from_iter((0..channels).map(|_| Vec::new())),
            window_timings: Vec::new(),
        }
    }

    pub fn window_timings(&self) -> &Vec<WindowTiming> {
        &self.window_timings
    }

    pub fn window_timings_mut(&mut self) -> &mut Vec<WindowTiming> {
        &mut self.window_timings
    }
}

impl Event for Asocv3SEvent {
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

impl ParseInto<Asocv3SEvent> for [u8] {
    fn fast_validate(&self, _params: &Params) -> Result<()> {
        if self.len() == 0 {
            return Err(ParsingError::MissingData);
        }
        if self.len() % 2 != 0 {
            return Err(ParsingError::UnexpectedLength);
        }
        // let params = ParamsCache::from(params);
        // let _ = get_chan_winds(self, &params).ok_or(ParsingError::UnexpectedLength)?;
        Ok(())
    }

    fn parse_into(&self, params: &Params) -> Result<Asocv3SEvent> {
        <Self as ParseInto<Asocv3SEvent>>::fast_validate(&self, params)?;
        let cache: ParamsCache = params.into();
        let (chans, n_packets) =
            get_chan_winds(self, &cache).ok_or(ParsingError::UnexpectedLength)?;
        let raw_event: Vec<u16> = self.iter().as_u16_be().collect();

        let packet_size = cache.channel_step_size * chans + cache.n_window_headers;
        let data = &raw_event[cache.n_event_headers..raw_event.len() - cache.n_event_footers];

        let mut event = Asocv3SEvent::new(chans);

        // reserve ahead of time to avoid reallocation
        for i in 0..chans {
            let channel =
                (data[i * cache.channel_step_size] & cache.channel_mask) >> cache.channel_shift;
            event
                .data
                .get_mut(channel as usize)
                .ok_or(ParsingError::InvalidChannel)?
                .reserve(packet_size * cache.samples);
            event
                .window_labels
                .get_mut(channel as usize)
                .ok_or(ParsingError::InvalidChannel)?
                .reserve(n_packets);
        }

        let n_packets = data.len() / packet_size;
        event.window_timings.reserve_exact(n_packets);

        for packet in data.chunks_exact(packet_size) {
            for channel_data in packet.chunks_exact(cache.channel_step_size) {
                let channel = (channel_data[0] & cache.channel_mask) >> cache.channel_shift;
                let window = (channel_data[0] & cache.window_mask) >> cache.n_last_bits;

                event
                    .data
                    .get_mut(channel as usize)
                    .ok_or(ParsingError::InvalidChannel)?
                    .extend(
                        channel_data[1..]
                            .iter()
                            .map(|x| (x & cache.data_mask) >> cache.n_last_bits)
                            .map(|x| x as Sample),
                    );
                event
                    .window_labels
                    .get_mut(channel as usize)
                    .ok_or(ParsingError::InvalidChannel)?
                    .push(window)
            }

            event.window_timings.push(packet[packet.len() - 1]);
        }

        set_time_axis(&mut event.time, &event.window_labels, params)?;

        Ok(event)
    }
}

fn get_chan_winds(raw_event: impl AsRef<[u8]>, params: &ParamsCache) -> Option<(usize, usize)> {
    let raw_event = raw_event.as_ref();
    let chanwinds = params.valid_bitlengths.get(&raw_event.len())?;
    if chanwinds.len() == 1 {
        return Some(chanwinds[0]);
    }
    chanwinds.iter().find_map(|(chan, wind)| {
        if test_chanwinds(raw_event, params, *chan).is_ok() {
            Some((*chan, *wind))
        } else {
            None
        }
    })
}

/// Check whether the data is valid for the given number of channels.
///
/// All windows should be the same within one block of channels.
fn test_chanwinds(
    raw_event: impl AsRef<[u8]>,
    params: &ParamsCache,
    channels: usize,
) -> Result<()> {
    let raw_event = raw_event.as_ref();
    let step_size = (params.channel_step_size * channels + params.n_window_headers as usize) * 2;
    let test_windows = 3;

    if raw_event.len() < params.n_event_headers * 2 + step_size {
        return Err(ParsingError::UnexpectedLength);
    }

    raw_event
        .get(params.n_event_headers * 2..)
        .ok_or(ParsingError::UnexpectedLength)?
        .chunks_exact(step_size)
        .take(test_windows)
        .try_for_each(|packet| {
            let mut windows = packet.chunks_exact(step_size).map(|channel| {
                // indexing is safe because the size is guaranteed by `chunks_exact`
                let window_header = u16::from_be_bytes([channel[0], channel[1]]);
                (window_header & params.window_mask) >> params.n_last_bits
            });

            let first_window = windows.next().ok_or(ParsingError::UnexpectedLength)?;
            if windows.any(|w| w != first_window) {
                return Err(ParsingError::InvalidWindow);
            }
            Ok(())
        })
}

fn update_valid_bitlengths(cache: &mut ParamsCache) {
    let windows = cache.windows;
    let channels = cache.channels;
    let channel_step_size = cache.channel_step_size;
    let headers = cache.n_event_headers;
    let footers = cache.n_event_footers;
    let win_footers = cache.n_window_footers;
    let bitlengths = &mut cache.valid_bitlengths;

    (1..windows).for_each(|win| {
        (1..(channels + 1)).for_each(|chan| {
            let mut packlen = (channel_step_size * chan + win_footers) * win + headers + footers;
            packlen *= 2; // 2 bytes per word
            bitlengths
                .entry(packlen)
                .or_insert_with(|| Vec::with_capacity(1))
                .push((chan, win));
        })
    });

    bitlengths.iter_mut().for_each(|(_, v)| {
        v.sort_by(|(chan_a, _), (chan_b, _)| chan_a.partial_cmp(chan_b).unwrap().reverse())
    });
}

struct ParamsCache {
    channels: usize,
    windows: usize,
    samples: usize,

    channel_mask: u16,
    channel_shift: u16,
    window_mask: u16,
    data_mask: u16,
    n_event_headers: usize,
    n_event_footers: usize,
    n_window_headers: usize,
    n_window_footers: usize,
    n_last_bits: usize,
    channel_step_size: usize,
    valid_bitlengths: HashMap<usize, Vec<(usize, usize)>>,
}

impl From<&Params> for ParamsCache {
    fn from(params: &Params) -> Self {
        let n_channel_headers = fetch_params_usize(params, "n_channel_headers", 1);
        let mut cache = Self {
            channels: params.channels(),
            windows: params.windows(),
            samples: params.samples(),
            channel_mask: fetch_params_u16(params, "chanmask", 0x3FF),
            channel_shift: fetch_params_u16(params, "chan_shift", 8),
            window_mask: fetch_params_u16(params, "windmask", 0xFF),
            data_mask: fetch_params_u16(params, "datamask", 0x1FFF),
            n_event_headers: fetch_params_usize(params, "n_event_headers", 3),
            n_event_footers: fetch_params_usize(params, "n_footer_words", 1),
            n_window_headers: fetch_params_usize(params, "n_window_headers", 0),
            n_window_footers: fetch_params_usize(params, "n_window_footers", 0),
            n_last_bits: fetch_params_usize(params, "n_last_bits", 0),
            channel_step_size: params.samples() + n_channel_headers as usize,
            valid_bitlengths: HashMap::new(),
        };
        update_valid_bitlengths(&mut cache);
        cache
    }
}
