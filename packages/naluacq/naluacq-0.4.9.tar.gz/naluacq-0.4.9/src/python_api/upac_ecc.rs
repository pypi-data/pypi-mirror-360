use rayon::prelude::*;
use once_cell::sync::Lazy;

use crate::ecc;

use pyo3::{
    prelude::{pyfunction, Python},
    types::{PyByteArray, PyList},
    PyObject,
};

pub static CHANNEL_OFFSETS: Lazy<Vec<(usize, usize)>> = Lazy::new(|| {
    let max_chan = 96;
    (0..max_chan).map(|chan| {
        let start = channel_start_bytes(chan as u8);
        let stop = channel_stop_bytes(&start);
        (start, stop)
    }).collect()
});

fn channel_start_bytes(chan: u8) -> usize {
    let n_chip_header_bytes = 1;
    let n_window_headers = 1;
    let n_window_footers = 1;
    let windows = 64; // Number of windows
    let samples = 64; // Number of samples per window

    // Calculate chip offset in bytes
    let chip_stride = chip_stride();
    let chip_offset: usize = (chan as usize / 16) * chip_stride;

    // Calculate the stride in bytes for each chip
    let chan_stride_bytes = (n_window_headers + windows * samples + n_window_footers) * 2;

    chip_offset + n_chip_header_bytes + ((chan as usize % 16) * chan_stride_bytes) + n_window_headers * 2
}

pub fn channel_stop_bytes(chan_start: &usize) -> usize {
    let windows = 64; // Number of windows
    let samples = 64; // Number of samples per window

     chan_start + (windows*samples)*2
}

/// Returns the chip stride as a value
const fn chip_stride() -> usize {
    let n_chip_header_bytes = 1;
    let n_chip_footer_bytes = 3;
    let n_window_headers = 1;
    let n_window_footers = 1;
    let chips = 6; // Number of chips
    let channels = 96; // Total number of channels
    let windows = 64; // Number of windows
    let samples = 64; // Number of samples per window
    let channels_per_chip = channels / chips;

    n_chip_header_bytes
        + (n_window_headers + windows * samples + n_window_footers) * 2 * channels_per_chip
        + n_chip_footer_bytes
}

//// Extract chip numbers from the raw data.
/// This function processes the raw data to extract chip numbers based on the UPAC96 format.
/// # Arguments
/// * `raw_data` - A vector of bytes representing the raw data.
fn _chip_nums(raw_data: &Vec<u8>) -> Vec<u8> {

    // replace raw_data.len() with self.len()
    let n_chip_header_bytes = 1;
    let n_chip_footer_bytes = 3;
    let n_event_footer_bytes = 2;
    let n_bytes = raw_data.len() - n_event_footer_bytes;
    let n_window_headers = 1;
    let n_window_footers = 1;
    let chips = 6;
    let channels = 96;
    let windows = 64;
    let samples = 64;
    let channels_per_chip = channels / chips;
    let chip_stride_bytes = n_chip_header_bytes
        + (n_window_headers + windows * samples + n_window_footers) * 2 * channels_per_chip
        + n_chip_footer_bytes;
    // replace with params later

    let res = (0..n_bytes).step_by(chip_stride_bytes)
        .map(|i| raw_data[i] & 0x3F)
        .collect::<Vec<u8>>();
    res
}

struct WordIter<'a> {
    data: &'a [u8],
    index: usize,
}

impl<'a> Iterator for WordIter<'a> {
    type Item = u16;

    fn next(&mut self) -> Option<Self::Item> {
        if self.index + 2 > self.data.len() {
            return None;
        }
        let word = u16::from_le_bytes([self.data[self.index], self.data[self.index + 1]]);
        self.index += 2;
        Some(word)
    }
}

#[pyfunction]
pub fn ecc_check(raw_bytes: Vec<u8>, py: Python) -> PyObject {
    let errors = _ecc_check(&raw_bytes);
    PyList::new(py, &errors).into()
}

/// Check each word in a UPAC96 event.
/// This function iterates through the raw bytes of a UPAC96 event, checking each 16-bit word for errors using the ECC algorithm.
/// # Arguments
/// * `raw_bytes` - A vector of bytes representing the raw data of a UPAC96 event.
/// # Returns
/// A vector of tuples containing the index of the word, the byte offset in the raw data, (positions, byte offset, word, corrected word, syndrome index, global parity).
fn _ecc_check(raw_bytes: &Vec<u8>) -> Vec<(usize, usize, u16, u16, u8, u8)> {
    let channels_per_chip: usize = 16;

    // Create a list of channels
    let chips = _chip_nums(raw_bytes);
    let n_channels = chips.len() * channels_per_chip;

    let res = (0..n_channels)
        .into_par_iter()
        .flat_map_iter(|i| {
            let (start, stop) = CHANNEL_OFFSETS[i];
            let data_range: std::ops::Range<usize> = start..stop;

            let mut words= WordIter{data: &raw_bytes[data_range], index: 0};
            let mut local_res = Vec::new();
            let mut i = 0;
            while let Some(word) = words.next() {
                let s = ecc::syndrome(&word);
                let si= ecc::syndrome_to_index(&s);
                let gp = ecc::global_parity(&word);

                if si.is_none() && gp == 0 {
                    i += 2;
                    continue;
                }
                let si = si.unwrap_or(0);
                let corrected = match gp {
                    1 => ecc::correct_bit(&word, si),
                    _ => word,
                };

                local_res.push((i, start+i, word, corrected, si, gp));
                i += 2;
            };
            local_res
        })
        .collect();
    res
}

#[pyfunction]
pub fn ecc_correct(mut raw_bytes: Vec<u8>, py: Python) -> PyObject {
    let _ =_ecc_check(&raw_bytes).iter().for_each(|err| {
        match err.5 {
            1 => {
                let pos = err.1;
                let fixed = err.3;
                let _ = std::mem::replace(&mut raw_bytes[pos], (fixed&0xFF) as u8);
                let _ = std::mem::replace(&mut raw_bytes[pos + 1], (fixed >> 8) as u8);
            }
            _ => {
                // even amount of errors, can't correct
            },
        }
    });
    PyByteArray::new(py, &raw_bytes).into()
}

/// Calculate the syndrome for a given 16-bit data word.
/// The syndrome is a 4-byte array where each byte represents the parity of specific bits in the data word.
/// 
/// # Arguments
/// * `data` - A 16-bit unsigned integer representing the data word.
/// # Returns
/// * An array of 4 bytes, each representing the parity of specific bits in the data word.
///
#[pyfunction]
pub fn syndrome(data: u16) -> [u8; 4] {
    ecc::syndrome(&data)
}

/// Convert a syndrome to an index based on the corrections.
///
/// # Arguments
/// * `s` - bit position or None.
#[pyfunction]
pub fn syndrome_to_index(s: [u8; 4]) -> Option<u8> {
    ecc::syndrome_to_index(&s)
}

/// Calculate the global parity for a 16-bit data word.
/// 
/// The global parity is the XOR of all bits in the data word, excluding the last bit.
/// gp = d(0) xor  d(1) xor d(2) xor  d(3) xor  d(4) xor d(5) xor  d(6) xor d(7) xor  d(8) xor  d(9) xor d(10) xor d(11) xor d(12) xor d(13) xor d(14)
/// 
///# Arguments
/// * `data` - A 16-bit unsigned integer representing the data word.
/// # Returns
/// * An integer representing the global parity of the data word.
///
#[pyfunction]
pub fn global_parity(data: u16) -> u8 {
    ecc::global_parity(&data)
}
