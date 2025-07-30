use crate::{acquisition::Params, error::ParsingError, Event};

use super::{
    util::{fetch_params_u16, fetch_params_usize, set_time_axis, AsU16BeExt},
    ParseInto, Result, Sample, TimeStamp, WindowLabel,
};

#[derive(Debug, Clone)]
pub struct AodsocEvent {
    data: Vec<Vec<Sample>>,
    window_labels: Vec<Vec<WindowLabel>>,
    time: Vec<Vec<TimeStamp>>,
}

impl AodsocEvent {
    pub fn new(channels: usize) -> Self {
        Self {
            data: Vec::from_iter((0..channels).map(|_| Vec::new())),
            window_labels: Vec::from_iter((0..channels).map(|_| Vec::new())),
            time: Vec::from_iter((0..channels).map(|_| Vec::new())),
        }
    }
}

impl Event for AodsocEvent {
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

impl ParseInto<AodsocEvent> for [u8] {
    fn fast_validate(&self, _params: &Params) -> Result<()> {
        if self.len() == 0 {
            return Err(ParsingError::MissingData);
        }
        if self.len() % 2 != 0 {
            return Err(ParsingError::UnexpectedLength);
        }
        Ok(())
    }

    fn parse_into(&self, params: &Params) -> Result<AodsocEvent> {
        <Self as ParseInto<AodsocEvent>>::fast_validate(&self, params)?;
        let cache: ParamsCache = params.into();
        let window_stride = cache.n_window_headers + cache.samples;

        let raw_event: Vec<u16> = self.iter().as_u16_be().collect();
        let mut event = AodsocEvent::new(params.channels());

        for chip_data in raw_event[..raw_event.len() - 1].split(|&x| x == cache.chip_footer) {
            if chip_data.len() < cache.n_chip_headers
                || (chip_data.len() - cache.n_chip_headers) % window_stride != 0
            {
                return Err(ParsingError::UnexpectedLength);
            }
            let chip_number = chip_data[0] as usize >> 12;
            let window_data = &chip_data[cache.n_chip_headers..];
            for channel_data in window_data.chunks_exact(window_stride) {
                let window = channel_data[0] & cache.window_mask;
                let channel = (channel_data[0] & cache.channel_mask) >> cache.channel_shift;
                let channel = channel as usize + chip_number * cache.channels_per_chip;
                event
                    .window_labels
                    .get_mut(channel)
                    .ok_or(ParsingError::InvalidChannel)?
                    .push(window);
                event
                    .data
                    .get_mut(channel)
                    .ok_or(ParsingError::InvalidChannel)?
                    .extend(
                        channel_data[cache.n_window_headers..]
                            .iter()
                            .map(|word| (*word & cache.data_bitmask) as Sample),
                    );
            }
        }

        set_time_axis(&mut event.time, &event.window_labels, params)?;

        Ok(event)
    }
}

struct ParamsCache {
    channels_per_chip: usize,
    samples: usize,

    data_bitmask: u16,
    channel_mask: u16,
    channel_shift: u16,
    window_mask: u16,
    chip_footer: u16,
    n_chip_headers: usize,
    n_window_headers: usize,
}

impl From<&Params> for ParamsCache {
    fn from(params: &Params) -> Self {
        let n_chips = fetch_params_usize(params, "num_chips", 2);

        Self {
            channels_per_chip: params.channels() / n_chips,
            samples: params.samples(),
            data_bitmask: fetch_params_u16(params, "databitmask", 0xFFF),
            channel_mask: fetch_params_u16(params, "chanmask", 0x300),
            channel_shift: fetch_params_u16(params, "chan_shift", 8),
            window_mask: fetch_params_u16(params, "windmask", 0x0FF),
            chip_footer: fetch_params_u16(params, "chip_stop_word", 0xFFFF),
            n_chip_headers: fetch_params_usize(params, "n_chip_headers", 3),
            n_window_headers: fetch_params_usize(params, "n_window_headers", 1),
        }
    }
}
