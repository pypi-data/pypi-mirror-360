use crate::{acquisition::Params, error::ParsingError, Event};

use super::{
    util::{fetch_params_u16, fetch_params_usize, set_time_axis, AsU16LeExt},
    ParseInto, Result, Sample, TimeStamp, WindowLabel,
};

use crate::ecc::{syndrome, global_parity};

#[derive(Debug, Clone)]
pub struct Upac96Event {
    data: Vec<Vec<Sample>>,
    window_labels: Vec<Vec<WindowLabel>>,
    time: Vec<Vec<TimeStamp>>,
    chips: Vec<u8>,
    ecc_errors: Vec<Vec<(usize, usize, u16, u16, u16)>>, // (byte number, sample number, rawbyte, syndrome, global parity)
}

impl Upac96Event {
    pub fn new() -> Self {
        const CHANNELS: usize = 96;
        const SAMPLES: usize = 4096;
        const CHIPS: usize = 6;
        Self {
            data: Vec::from_iter((0..CHANNELS).map(|_| Vec::with_capacity(SAMPLES))),
            ecc_errors: Vec::from_iter((0..CHANNELS).map(|_| Vec::new())),
            window_labels: Vec::from_iter((0..CHANNELS).map(|_| Vec::with_capacity(SAMPLES))),
            time: Vec::from_iter((0..CHANNELS).map(|_| Vec::with_capacity(SAMPLES))),
            chips: Vec::with_capacity(CHIPS),
        }
    }
}

impl Event for Upac96Event {
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

    fn ecc_errors(&self) -> Option<&Vec<Vec<(usize, usize, u16, u16, u16)>>> {
        Some(&self.ecc_errors)
    }
}

impl ParseInto<Upac96Event> for [u8] {
    fn fast_validate(&self, params: &Params) -> Result<()> {
        if self.len() == 0 {
            return Err(ParsingError::MissingData);
        }
        if self.len() & 1 != 0 {
            return Err(ParsingError::UnexpectedLength);
        }

        let params = ParamsCache::from(params);
        let instance_data_len = params.n_chip_header_bytes
            + (params.n_window_headers + params.windows * params.samples + params.n_window_footers)
                * 2
                * params.channels_per_chip
            + params.n_chip_footer_bytes;
        if (self.len() - params.n_event_footer_bytes) % instance_data_len != 0 {
            return Err(ParsingError::UnexpectedLength);
        }
        Ok(())
    }

    /// Data Format
    ///     For each chip:
    ///     - Chip header (1 byte, 0x80)
    ///     For each channel
    ///         - 1 window header (2 bytes, 0xCCWW)
    ///         - 4096 samples (2 bytes each: 6-bits ECC + 10 bits data)
    ///         - 1 window footer (2 byte CRC, 0xZZFC)
    ///     - Chip footer (3 bytes, 0x00FACE)
    fn parse_into(&self, params: &Params) -> Result<Upac96Event> {
        <Self as ParseInto<Upac96Event>>::fast_validate(&self, params)?;
        let cache: ParamsCache = params.into();

        let mut event = Upac96Event::new();
        let raw_data = &self[..self.len() - cache.n_event_footer_bytes];

        let channel_stride =
            cache.n_window_headers + cache.windows * cache.samples + cache.n_window_footers;

        for chip_pack in raw_data.chunks(cache.chip_stride_bytes) {
            let chip = chip_pack[0] & 0x3F;
            event.chips.push(chip);

            let data_range = cache.n_chip_header_bytes..chip_pack.len() - cache.n_chip_footer_bytes;
            let words: Vec<u16> = chip_pack[data_range.clone()].iter().as_u16_le().collect();
            for window_data in words.chunks(channel_stride) {
                let start_window = window_data[0] & cache.window_mask;
                let mut channel = (window_data[0] & cache.channel_mask) >> cache.channel_shift;
                channel += chip as u16 * cache.channels_per_chip as u16;
                // event
                //     .ecc_errors
                //     .get_mut(channel as usize)
                //     .ok_or(ParsingError::InvalidChannel)?
                //     .extend(
                //         window_data
                //             [cache.n_window_headers..window_data.len() - cache.n_window_footers]
                //             .iter()
                //             .enumerate()
                //             .filter_map(|(i, &word)| {
                //                 let syndrome: u16 = (syndrome(word).iter().sum::<u8>()) as u16;
                //                 let global_parity = global_parity(word) as u16;
                //                 if syndrome != 0 || global_parity != 0 {
                //                     Some((data_range.start + i, i, word.clone(), syndrome.clone(), global_parity.clone()))
                //                 } else {
                //                     None
                //                 }
                //             }),
                //     );
                event
                    .data
                    .get_mut(channel as usize)
                    .ok_or(ParsingError::InvalidChannel)?
                    .extend(
                        window_data
                            [cache.n_window_headers..window_data.len() - cache.n_window_footers]
                            .iter()
                            .map(|&word| {
                                //  inverts the data bits
                                ((word & cache.data_bitmask) ^ cache.data_bitmask) as Sample
                            }),
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
        }

        set_time_axis(&mut event.time, &event.window_labels, params)?;

        Ok(event)
    }
}

struct ParamsCache {
    channels_per_chip: usize,
    windows: usize,
    samples: usize,
    total_samples: usize,
    data_bitmask: u16,
    channel_mask: u16,
    channel_shift: u16,
    window_mask: u16,
    n_event_footer_bytes: usize,
    n_chip_header_bytes: usize,
    n_chip_footer_bytes: usize,
    n_window_headers: usize,
    n_window_footers: usize,
    chip_stride_bytes: usize,
    chan_stride_bytes: usize,
}

impl From<&Params> for ParamsCache {
    fn from(params: &Params) -> Self {
        let chips = fetch_params_usize(params, "num_chips", 6);
        let channels = params.channels();
        let channels_per_chip = channels / chips;
        let windows = params.windows();
        let samples = params.samples();
        let total_samples = windows * samples;
        let n_chip_header_bytes = fetch_params_usize(params, "n_chip_headers", 1);
        let n_chip_footer_bytes = fetch_params_usize(params, "n_chip_footers", 3);
        let n_window_headers = fetch_params_usize(params, "n_window_headers", 1);
        let n_window_footers = fetch_params_usize(params, "n_window_footers", 1);
        let chip_stride_bytes = n_chip_header_bytes
            + (n_window_headers + windows * samples + n_window_footers) * 2 * channels_per_chip
            + n_chip_footer_bytes;
        Self {
            channels_per_chip,
            windows,
            samples,
            total_samples,
            data_bitmask: fetch_params_u16(params, "data_mask", 0x03FF),
            channel_mask: fetch_params_u16(params, "chanmask", 0xFF00),
            channel_shift: fetch_params_u16(params, "chan_shift", 8),
            window_mask: fetch_params_u16(params, "windmask", 0x00FF),
            n_event_footer_bytes: fetch_params_usize(params, "n_event_footers", 2),
            n_chip_header_bytes,
            n_chip_footer_bytes,
            n_window_headers,
            n_window_footers,
            chip_stride_bytes,
            chan_stride_bytes: n_window_headers + windows * samples + n_window_footers,
        }
    }
}
