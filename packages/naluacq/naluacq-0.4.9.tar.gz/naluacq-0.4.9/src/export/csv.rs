//! Ugly and inefficient CSV export functionality. This code is a direct port from the Python code
//! in NaluDAQ and needs a ton of work.

use std::{
    collections::HashSet,
    fs::OpenOptions,
    io::{self, BufWriter},
    path::Path,
};

use ndarray::prelude::*;

use csv::{ByteRecord, Writer};

use crate::{
    acquisition::Params,
    calibration::{CorrectedExt, Corrections},
    parsing::{Sample, WindowLabel},
    util::dispatch_by_event_type,
    Acquisition, Event, ExportError, ParseInto, ParsingError,
};

use super::Result;

/// Export CSV from an acquisition.
///
/// # Arguments
/// * `acq` - Acquisition to export from.
/// * `indices` - Indices of events to export.
/// * `corrections` - `Corrections` struct with correction to apply on output.
/// * `out` - Path to output file.
/// * `chunk_size` - Number of events to export per chunk. Avoid disk issues by exporting in chunks.
pub fn export_csv_from_acq(
    acq: Acquisition,
    indices: &[usize],
    corrections: Corrections,
    out: impl AsRef<Path>,
    chunk_size: usize,
) -> Result<()> {
    let params = acq.metadata()?.params().clone();

    for (chunk_num, chunk_indices) in indices.chunks(chunk_size).enumerate() {
        let path = out
            .as_ref()
            .join(format!("{} (chunk {}).csv", acq.name(), chunk_num));
        dispatch_by_event_type!(
            params.model(),
            ParsingError::UnsupportedModel,
            export_chunk,
            &acq,
            &params,
            corrections.clone(),
            chunk_indices,
            path
        )??;
    }
    Ok(())
}

fn export_chunk<T: Event>(
    acq: &Acquisition,
    params: &Params,
    corrections: Corrections,
    indices: &[usize],
    path: impl AsRef<Path>,
) -> Result<(), ExportError>
where
    [u8]: ParseInto<T>,
{
    let file = OpenOptions::new().create(true).write(true).open(path)?;
    let file = BufWriter::with_capacity(5000, file);
    let events = indices
        .iter()
        .filter_map(|i| acq.get(*i).ok())
        .filter_map(|raw| {
            let event: T = raw.parse_into(params).ok()?;
            Some(event)
        })
        .corrected(corrections)
        .filter_map(|event| event.ok())
        .collect::<Vec<_>>();
    events.iter().export_csv(file, params)
}

pub trait ExportCsv<W: io::Write> {
    fn export_csv(&mut self, out: W, params: &Params) -> Result<()>;
}

impl<'a, I, W, E> ExportCsv<W> for I
where
    I: Iterator<Item = &'a E> + Clone,
    E: Event + 'a,
    W: io::Write,
{
    fn export_csv(&mut self, out: W, params: &Params) -> Result<()> {
        let mut writer = Writer::from_writer(out);
        let channels = channels(self.clone());
        write_header(&mut writer, self.clone(), &channels)?;
        self.enumerate()
            .try_for_each(|(i, event)| write_event(&mut writer, params, event, &channels, i))?;

        Ok(())
    }
}

fn write_header<'a, I, E, W>(
    writer: &mut Writer<W>,
    mut events: I,
    channels: &[usize],
) -> Result<()>
where
    W: io::Write,
    I: Iterator<Item = &'a E> + Clone,
    E: Event + 'a,
{
    let include_timing = events.any(|event| event.channel_timing().is_some());

    let mut header = Vec::from(["acq_num".to_owned(), "evt_num".to_owned()]);
    channels.iter().for_each(|chan| {
        header.push(format!("windnum_ch{chan}"));
        header.push(format!("data_ch{chan}"));
        header.push(format!("time_ch{chan}"));
        if include_timing {
            header.push(format!("timing_ch{chan}"));
        }
    });

    writer.write_record(header)?;
    Ok(())
}

fn write_event<W: io::Write>(
    writer: &mut Writer<W>,
    params: &Params,
    event: &impl Event,
    channels: &[usize],
    index: usize,
) -> Result<()> {
    let samples = params.samples();
    let include_timing = event.channel_timing().is_some();

    let merged_labels = merge_window_labels(event.window_labels());

    let columns_per_channel = 3 + include_timing as usize;
    let columns = 2 + channels.len() * columns_per_channel;
    let rows = merged_labels.len() * samples;

    let mut result = Array::<f32, _>::zeros((rows, columns));
    result.slice_mut(s![.., 1_usize]).fill(index as f32);
    result.slice_mut(s![.., 2_usize..]).fill(f32::NAN);

    for (i, channel) in channels.iter().enumerate() {
        let data = &event.data()[*channel];
        let time = &event.time()[*channel];
        let window_labels = &event.window_labels()[*channel];
        if data.len() == 0 {
            continue;
        }

        let (row_start, row_end) = data_endpoints(&data, &window_labels, &merged_labels, samples);
        if row_end > merged_labels.len() * samples {
            println!("Bad channel {} at Event {}", channel, index);
            continue;
        }
        let first_column = 2 + i * columns_per_channel;

        let label_column = tile_u16(&window_labels, samples);
        result
            .slice_mut(s![row_start..row_end, first_column])
            .assign(&label_column);
        result
            .slice_mut(s![row_start..row_end, first_column + 1])
            .assign(&ArrayView::from(data).map(|x| (*x as f32 * 10.0).round() / 10.0));
        result
            .slice_mut(s![row_start..row_end, first_column + 2])
            .assign(&ArrayView::from(time).map(|x| *x as f32));
        if let Some(timing) = event.channel_timing() {
            result
                .slice_mut(s![row_start..row_end, first_column + 3])
                .assign(&tile_u32(&timing[*channel], samples));
        }
    }

    for row in result.rows() {
        let mut record = ByteRecord::with_capacity(128, row.len());
        for value in row {
            if value.is_nan() {
                record.push_field(b"");
                continue;
            }
            record.push_field(value.to_string().as_bytes());
        }
        writer.write_byte_record(&record)?;
    }

    Ok(())
}

fn tile_u16(x: &[u16], repetitions: usize) -> Array1<f32> {
    let n = x.len();
    Array::from_shape_fn((repetitions * n,), |i| x[i / repetitions] as f32)
}

fn tile_u32(x: &[u32], repetitions: usize) -> Array1<f32> {
    let n = x.len();
    Array::from_shape_fn((repetitions * n,), |i| x[i / repetitions] as f32)
}

fn data_endpoints(
    data: &[Sample],
    win_labels: &[WindowLabel],
    labels: &[WindowLabel],
    samples: usize,
) -> (usize, usize) {
    let label_pos = labels.iter().position(|&x| x == win_labels[0]).unwrap_or(0);
    let start = label_pos * samples;
    let end = start + data.len();
    (start, end)
}

fn merge_window_labels(window_labels: &Vec<Vec<WindowLabel>>) -> Vec<WindowLabel> {
    let mut output: Vec<u16> = Vec::new();
    let mut nextround: Vec<Vec<u16>> = window_labels
        .iter()
        .filter(|x| x.len() > 0)
        .cloned()
        .collect();

    while !nextround.is_empty() {
        let longest_remaining = nextround.iter().map(|x| x.len()).max().unwrap_or(0);
        if longest_remaining == 0 {
            break;
        }

        let topop = calculate_first_window_idx(&nextround);
        let nxt_lbl = nextround[topop][0];

        if let Some(last_lbl) = output.last() {
            if *last_lbl != nxt_lbl {
                output.push(nxt_lbl);
            }
        } else {
            output.push(nxt_lbl);
        }

        let available_labels: Vec<Vec<u16>> =
            nextround.iter().filter(|y| y.len() > 0).cloned().collect();

        nextround = available_labels
            .iter()
            .map(|x| {
                if x[0] == nxt_lbl {
                    x[1..].to_vec()
                } else {
                    x.clone()
                }
            })
            .collect();
    }

    output
}

fn calculate_first_window_idx(labels: &Vec<Vec<WindowLabel>>) -> usize {
    let rollovers: Vec<(usize, u16)> = labels
        .iter()
        .enumerate()
        .filter(|(_, x)| !x.is_empty() && x[0] > x[x.len() - 1])
        .map(|(p, x)| (p, x[0]))
        .collect();

    let no_rollover: Vec<(usize, &[u16])> = labels
        .iter()
        .enumerate()
        .filter(|(_, x)| !x.is_empty() && x[0] < x[x.len() - 1])
        .map(|(p, x)| (p, x.as_slice()))
        .collect();

    let mut first = Vec::new();

    if !rollovers.is_empty() {
        for f in rollovers.iter() {
            for n in no_rollover.iter() {
                if n.1.contains(&f.1) {
                    break;
                }
                first.push(*f);
            }
        }
    }

    if first.is_empty() {
        first.extend(
            labels
                .iter()
                .enumerate()
                .filter(|(_, x)| !x.is_empty())
                .map(|(pos, x)| (pos, x[0])),
        );
    }

    let topop = first.iter().min_by_key(|x| x.1).unwrap();

    topop.0
}

/// Get a sorted list of channels present in the given events.
///
/// The returned channels are the set of channels which contain data in at least one event.
fn channels<'a, T>(events: impl Iterator<Item = &'a T>) -> Vec<usize>
where
    T: Event + 'a,
{
    let channels: HashSet<usize> =
        HashSet::from_iter(events.flat_map(|event| {
            event.data().iter().enumerate().filter_map(|(chan, data)| {
                if data.len() == 0 {
                    None
                } else {
                    Some(chan)
                }
            })
        }));

    // Channels need to be sorted since the order produced by a HashSet is random
    let mut channels = Vec::from_iter(channels);
    channels.sort();
    channels
}
