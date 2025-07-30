use crate::{acquisition::Params, error::ParsingError};

use super::{Result, TimeStamp, WindowLabel};

pub use iterext::{AsU16Be, AsU16BeExt, AsU16Le, AsU16LeExt};

/// Add a time axis to the event under the `time` field based on the window labels
/// and the start window.
///
/// # Errors
/// Returns a variant of [`ParsingError`] if the data is invalid.
pub(super) fn set_time_axis(
    time: &mut Vec<Vec<TimeStamp>>,
    window_labels: &Vec<Vec<WindowLabel>>,
    params: &Params,
) -> Result<()> {
    let channels = params.channels();
    let windows = params.windows();
    let samples = params.samples();

    for chan in 0..channels {
        let window_labels = window_labels.get(chan).ok_or(ParsingError::MissingData)?;
        if window_labels.len() == 0 {
            continue;
        }
        let start_window = window_labels[0] as i32;
        let time = time.get_mut(chan).ok_or(ParsingError::MissingData)?;
        time.extend(window_labels.iter().flat_map(|&label| {
            let mut wind = label as i32;
            if wind < start_window {
                wind += windows as i32;
            }
            let wind = (wind - start_window) as TimeStamp;
            (0..samples).map(move |sample| (samples as TimeStamp * wind) + sample as TimeStamp)
        }));
    }
    Ok(())
}

/// Extract an "others" parameter as `u16`
pub fn fetch_params_u16(params: &Params, name: &str, default: u16) -> u16 {
    params
        .others()
        .get(name)
        .and_then(|x| x.as_u64())
        .unwrap_or(default as u64) as u16
}

/// Extract an "others" parameter as `usize`
pub fn fetch_params_usize(params: &Params, name: &str, default: usize) -> usize {
    params
        .others()
        .get(name)
        .and_then(|x| x.as_u64())
        .unwrap_or(default as u64) as usize
}

mod iterext {
    use std::borrow::Borrow;

    /// Iterator over bytes as u16 in big endian order.
    pub struct AsU16Be<I: Iterator> {
        inner: I,
    }

    /// Iterator over bytes as u16 in little endian order.
    pub struct AsU16Le<I: Iterator> {
        inner: I,
    }

    impl<I, B> Iterator for AsU16Be<I>
    where
        I: Iterator<Item = B>,
        B: Borrow<u8>,
    {
        type Item = u16;

        fn next(&mut self) -> Option<Self::Item> {
            let a = *self.inner.next()?.borrow();
            let b = *self.inner.next()?.borrow();
            Some(u16::from_be_bytes([a, b]))
        }
    }

    impl<I, B> Iterator for AsU16Le<I>
    where
        I: Iterator<Item = B>,
        B: Borrow<u8>,
    {
        type Item = u16;

        fn next(&mut self) -> Option<Self::Item> {
            let a = *self.inner.next()?.borrow();
            let b = *self.inner.next()?.borrow();
            Some(u16::from_le_bytes([a, b]))
        }
    }

    /// Extension trait for [`AsU16Be`].
    pub trait AsU16BeExt: Iterator {
        fn as_u16_be(self) -> AsU16Be<Self>
        where
            Self: Sized,
        {
            AsU16Be { inner: self }
        }
    }

    /// Extension trait for [`AsU16Le`].
    pub trait AsU16LeExt: Iterator {
        fn as_u16_le(self) -> AsU16Le<Self>
        where
            Self: Sized,
        {
            AsU16Le { inner: self }
        }
    }

    impl<I: Iterator> AsU16BeExt for I {}
    impl<I: Iterator> AsU16LeExt for I {}
}
