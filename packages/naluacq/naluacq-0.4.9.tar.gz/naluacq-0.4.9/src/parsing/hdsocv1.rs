use crate::{
    acquisition::Params,
    error::ParsingError,
    parsing::{Result, TimeStamp},
    Event,
};

use super::{
    util::{fetch_params_u16, fetch_params_usize, AsU16BeExt},
    ParseInto, Sample, WindowLabel,
};

#[derive(Debug, Clone)]
pub struct Hdsocv1Event {
    data: Vec<Vec<Sample>>,
    window_labels: Vec<Vec<WindowLabel>>,
    time: Vec<Vec<TimeStamp>>,
    channel_timing: Vec<Vec<u32>>,
}

impl Hdsocv1Event {
    pub fn new(channels: usize) -> Self {
        Self {
            data: Vec::from_iter((0..channels).map(|_| Vec::new())),
            window_labels: Vec::from_iter((0..channels).map(|_| Vec::new())),
            time: Vec::from_iter((0..channels).map(|_| Vec::new())),
            channel_timing: Vec::from_iter((0..channels).map(|_| Vec::new())),
        }
    }
}

impl Event for Hdsocv1Event {
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

    fn channel_timing(&self) -> Option<&Vec<Vec<u32>>> {
        Some(&self.channel_timing)
    }
}

impl ParseInto<Hdsocv1Event> for [u8] {
    fn parse_into(&self, params: &Params) -> Result<Hdsocv1Event> {
        if self.len() % 2 != 0 {
            return Err(ParsingError::UnexpectedLength);
        }
        let cache = ParamsCache::from(params);
        let words: Vec<u16> = self.iter().as_u16_be().collect();
        let packages = packages(&words, &cache);
        if packages.is_empty() {
            return Err(ParsingError::PackageEmpty);
        }
        let mut event = Hdsocv1Event::new(cache.channels);
        packages
            .iter()
            .filter(|pkg| is_disabled_package(pkg, &cache))
            .try_for_each(|pkg| {
                let channel = (pkg[0] & cache.channel_mask) as usize;
                let abs_window = pkg[3] & cache.window_mask;
                let timing = (((pkg[1] & cache.timing_mask) as u32) << cache.timing_shift as u32)
                    | (pkg[2] & cache.timing_mask) as u32;

                event
                    .data
                    .get_mut(channel)
                    .ok_or(ParsingError::InvalidChannel)?
                    .extend(
                        pkg[cache.n_headers..cache.n_headers + cache.samples]
                            .iter()
                            .map(|x| *x as Sample),
                    );
                event
                    .window_labels
                    .get_mut(channel)
                    .ok_or(ParsingError::InvalidChannel)?
                    .push(abs_window);
                event
                    .channel_timing
                    .get_mut(channel)
                    .ok_or(ParsingError::InvalidChannel)?
                    .push(timing);

                Result::<(), ParsingError>::Ok(())
            })?;

        set_time_axis(&mut event, params)?;

        Ok(event)
    }

    fn fast_validate(&self, params: &Params) -> Result<(), ParsingError> {
        let words: Vec<u16> = self.iter().as_u16_be().collect();
        let packages = packages(&words, &ParamsCache::from(params));

        if packages.is_empty() {
            return Err(ParsingError::PackageEmpty);
        }
        Ok(())
    }
}

fn packages(words: &[u16], cache: &ParamsCache) -> Vec<Vec<u16>> {
    let mut packages = Vec::with_capacity(words.len() / cache.package_len);
    let mut pkg_start = 0;

    for (i, word) in words.iter().enumerate() {
        if *word != cache.package_stop_word {
            continue;
        }
        if i - pkg_start + 1 == cache.package_len {
            packages.push(words[pkg_start..=i].to_vec());
        }
        pkg_start = i + 1;
    }

    packages
}

fn set_time_axis(event: &mut Hdsocv1Event, params: &Params) -> Result<()> {
    let window_labels = &mut event.window_labels;
    let samples = params.samples() as usize;
    let min_timing = event
        .channel_timing
        .iter()
        .filter(|x| x.len() > 0)
        .map(|x| x[0])
        .min()
        .ok_or(ParsingError::MissingData)?;

    for chan in 0..params.channels() {
        let window_labels = window_labels.get(chan).ok_or(ParsingError::MissingData)?;
        if window_labels.is_empty() {
            continue;
        }
        let timing = event.channel_timing.get(chan).ok_or(ParsingError::MissingData)?;

        // Correction should be 0 for the smallest, and increase for there.
        let correction: TimeStamp = (timing[0] as u16 - min_timing as u16) * samples as u16;
        let n_windows = window_labels.len() as u16;
        let time_axis: Vec<TimeStamp> = (correction..(samples as u16 * n_windows + correction as u16) as u16).collect();

        event.time[chan] = time_axis;
    }

    Ok(())
}

/// Check if the package came from a disabled channel.
///
/// Samples with all zeros are considered to be disabled.
fn is_disabled_package(pkg: &[u16], params: &ParamsCache) -> bool {
    pkg.iter()
        .skip(params.n_headers)
        .take(params.samples)
        .any(|&x| x != 0)
}

struct ParamsCache {
    channels: usize,
    samples: usize,
    channel_mask: u16,
    window_mask: u16,
    timing_mask: u16,
    timing_shift: u16,
    package_len: usize,
    package_stop_word: u16,
    n_headers: usize,
}

impl From<&Params> for ParamsCache {
    fn from(params: &Params) -> Self {
        Self {
            channels: params.channels(),
            samples: params.samples(),
            channel_mask: fetch_params_u16(params, "chanmask", 0x3F),
            window_mask: fetch_params_u16(params, "abs_wind_mask", 0x3F),
            timing_mask: fetch_params_u16(params, "timing_mask", 0xFFF),
            timing_shift: fetch_params_u16(params, "timing_shift", 12),
            package_len: fetch_params_usize(params, "packet_size", 72) / 2 + 1,
            n_headers: fetch_params_usize(params, "headers", 4),
            package_stop_word: stop_word(params).unwrap_or(0xFA5A),
        }
    }
}

fn stop_word(params: &Params) -> Result<u16> {
    let stop_word = params
        .others()
        .get("stop_word")
        .ok_or(ParsingError::InvalidParameters)?
        .as_str()
        .ok_or(ParsingError::InvalidParameters)?;
    let stop_word =
        usize::from_str_radix(stop_word, 16).or(Err(ParsingError::InvalidParameters))? as u16;
    Ok(stop_word)
}
