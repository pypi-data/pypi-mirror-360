use crate::{acquisition::Params, error::ParsingError, Event};

use super::{
    util::{fetch_params_u16, fetch_params_usize, set_time_axis, AsU16LeExt},
    ParseInto, Result, Sample, TimeStamp, WindowLabel,
};

#[derive(Debug, Clone)]
pub struct Udc16Event {
    data: Vec<Vec<Sample>>,
    window_labels: Vec<Vec<WindowLabel>>,
    time: Vec<Vec<TimeStamp>>,
}

impl Udc16Event {
    pub fn new(channels: usize) -> Self {
        Self {
            data: Vec::from_iter((0..channels).map(|_| Vec::new())),
            window_labels: Vec::from_iter((0..channels).map(|_| Vec::new())),
            time: Vec::from_iter((0..channels).map(|_| Vec::new())),
        }
    }
}

impl Event for Udc16Event {
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

impl ParseInto<Udc16Event> for [u8] {
    fn fast_validate(&self, params: &Params) -> Result<()> {
        if self.len() == 0 {
            return Err(ParsingError::MissingData);
        }

        let params = ParamsCache::from(params);
        let expected_len = params.n_event_header_bytes
            + (params.n_window_headers + params.windows * params.samples + params.n_window_footers)
                * 2
                * params.channels
            + params.n_event_footer_bytes;
        if self.len() != expected_len {
            return Err(ParsingError::UnexpectedLength);
        }
        Ok(())
    }

    /// The dataformat is:
    ///     header: b'10' + "CHIP_ID"(6-bits) (1 byte)
    ///     16 ea: (16 x 8196 bytes = 131_136 bytes)
    ///         - "WINDOW"(8-bit) + "CHANNEL"(8-bit) (2 byte)
    ///         - 4096 samples (each 16-bits) (8192 BYTES)
    ///         - CRC + 0xFC (2 bytes)
    ///     footer: 0xCAFE (2 byte)
    ///
    ///     131,139 bytes total
    fn parse_into(&self, params: &Params) -> Result<Udc16Event> {
        <Self as ParseInto<Udc16Event>>::fast_validate(&self, params)?;
        let cache: ParamsCache = params.into();

        let mut event = Udc16Event::new(cache.channels);
        let raw_data: Vec<_> = self[1..].iter().as_u16_le().collect();
        let channel_stride =
            cache.n_window_headers + cache.windows * cache.samples + cache.n_window_footers;

        for words in raw_data.chunks_exact(channel_stride) {
            let start_window = words[0] & cache.window_mask;
            let channel = (words[0] & cache.channel_mask) >> cache.channel_shift;
            event
                .data
                .get_mut(channel as usize)
                .ok_or(ParsingError::InvalidChannel)?
                .extend(
                    words[cache.n_window_headers..words.len() - cache.n_window_footers]
                        .iter()
                        .map(|&x| ((x & cache.data_bitmask) ^ cache.data_bitmask) as Sample),
                );
            event
                .window_labels
                .get_mut(channel as usize)
                .ok_or(ParsingError::InvalidChannel)?
                .extend(
                    (start_window..start_window + cache.windows as u16)
                        .map(|win| win % cache.windows as u16),
                );
        }

        set_time_axis(&mut event.time, &event.window_labels, params)?;

        Ok(event)
    }
}

struct ParamsCache {
    channels: usize,
    windows: usize,
    samples: usize,

    data_bitmask: u16,
    channel_mask: u16,
    channel_shift: u16,
    window_mask: u16,
    n_event_header_bytes: usize,
    n_event_footer_bytes: usize,
    n_window_headers: usize,
    n_window_footers: usize,
}

impl From<&Params> for ParamsCache {
    fn from(params: &Params) -> Self {
        Self {
            channels: params.channels(),
            windows: params.windows(),
            samples: params.samples(),
            data_bitmask: fetch_params_u16(params, "data_mask", 0x03FF),
            channel_mask: fetch_params_u16(params, "chanmask", 0xFF00),
            channel_shift: fetch_params_u16(params, "chan_shift", 8),
            window_mask: fetch_params_u16(params, "windmask", 0x00FF),
            n_event_header_bytes: fetch_params_usize(params, "n_chip_headers", 1),
            n_event_footer_bytes: fetch_params_usize(params, "n_chip_footers", 2),
            n_window_headers: fetch_params_usize(params, "n_window_headers", 1),
            n_window_footers: fetch_params_usize(params, "n_window_footers", 1),
        }
    }
}
