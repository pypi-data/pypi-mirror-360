use crate::{acquisition::Params, Event, ParseInto, ParsingError};

use super::{
    util::{fetch_params_usize, set_time_axis, AsU16BeExt},
    Result, Sample, TimeStamp, WindowLabel,
};

#[derive(Debug, Clone)]
pub struct Trbhmv1Event {
    data: Vec<Vec<Sample>>,
    window_labels: Vec<Vec<WindowLabel>>,
    time: Vec<Vec<TimeStamp>>,
}

impl Trbhmv1Event {
    pub fn new(channels: usize) -> Self {
        Self {
            data: Vec::from_iter((0..channels).map(|_| Vec::new())),
            window_labels: Vec::from_iter((0..channels).map(|_| Vec::new())),
            time: Vec::from_iter((0..channels).map(|_| Vec::new())),
        }
    }
}

impl Event for Trbhmv1Event {
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

impl ParseInto<Trbhmv1Event> for [u8] {
    fn fast_validate(&self, params: &Params) -> Result<()> {
        let cache: ParamsCache = params.into();

        if self.len() & 1 != 0 || self.len() < cache.header_step_size * 2 {
            Err(ParsingError::UnexpectedLength)
        } else {
            Ok(())
        }
    }

    fn parse_into(&self, params: &Params) -> Result<Trbhmv1Event> {
        <Self as ParseInto<Trbhmv1Event>>::fast_validate(&self, params)?;
        let cache: ParamsCache = params.into();

        let mut event = Trbhmv1Event::new(cache.channels);

        self.get(0..self.len().saturating_sub(4))
            .ok_or(ParsingError::UnexpectedLength)?
            .chunks(cache.header_step_size * 2)
            .try_for_each(|data| {
                let chip = u16::from_be_bytes([data[0], data[1]]) as usize;

                data.get(
                    cache.n_event_headers * 2
                        ..cache.n_event_headers * 2 + cache.window_step_size * 2 - 2,
                )
                .ok_or(ParsingError::UnexpectedLength)?
                .chunks((cache.samples + cache.n_window_headers) * 2)
                .try_for_each(|data| {
                    if data.len() != (cache.samples + cache.n_window_headers) * 2 {
                        return Err(ParsingError::UnexpectedLength);
                    }
                    let window = u16::from_be_bytes([data[0], data[1]]);
                    let channel = u16::from_be_bytes([data[2], data[3]]) as usize
                        + cache.channels_per_chip * chip;

                    event
                        .data
                        .get_mut(channel)
                        .ok_or(ParsingError::InvalidChannel)?
                        .extend(
                            data.get(4..4 + cache.samples * 2)
                                .ok_or(ParsingError::UnexpectedLength)?
                                .iter()
                                .as_u16_be()
                                .map(|x| x as f32),
                        );
                    event
                        .window_labels
                        .get_mut(channel)
                        .ok_or(ParsingError::InvalidChannel)?
                        .push(window);
                    Ok(())
                })
            })?;

        set_time_axis(&mut event.time, &event.window_labels, params)?;
        Ok(event)
    }
}

#[allow(unused)]
struct ParamsCache {
    channels: usize,
    windows: usize,
    samples: usize,

    n_event_headers: usize,
    n_window_headers: usize,
    n_footers: usize,
    channels_per_chip: usize,
    window_step_size: usize,
    header_step_size: usize,
}

impl From<&Params> for ParamsCache {
    fn from(params: &Params) -> Self {
        let samples = params.samples();
        let n_window_headers = fetch_params_usize(params, "n_window_headers", 2);
        let n_event_headers = fetch_params_usize(params, "n_event_headers", 7);
        let n_footers = fetch_params_usize(params, "n_footer_words", 1);
        let channels_per_chip = 4;
        let window_step_size = (samples + n_window_headers) * channels_per_chip + n_footers;

        Self {
            channels: params.channels(),
            windows: params.windows(),
            samples,
            n_event_headers,
            n_window_headers,
            n_footers,
            window_step_size,
            channels_per_chip,
            header_step_size: window_step_size + n_event_headers + 1,
        }
    }
}
