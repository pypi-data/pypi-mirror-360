//! Module containing utilities for acquisition I/O.
//!
//! For simple read-only access, use the [`Acquisition`] type.
//!
//! For writing, use the [`WriteChunkFile`](chunk::WriteChunkFile) type.
//!
//! For more information on the data format, see the [crate] home.

pub mod chunk;
mod constants;
pub mod util;

use std::{
    fmt::Debug,
    fs::{self, create_dir},
    io::ErrorKind,
    path::PathBuf,
    str::FromStr,
};

use crate::{
    error::{AcquisitionError, MetadataError},
    RawEvent,
};

use chunk::ReadChunkFile;
use serde::{Deserialize, Serialize};
use util::is_acquisition;

use self::util::dir_size;

/// This is the main entry point for accessing acquisitions on the disk.
///
/// Has several methods for accessing data held in an acquisition.
///
/// The acquisition is read-only for events; for write operations see [`WriteChunkFile`].
///
///
/// # Examples
///
/// The [`Acquisition`] struct is the main entry point for accessing acquisitions. It can be created
/// using the path to an acquisition directory on disk.
///
/// Reading an acquisition:
///
/// ```no_run
///
/// use naluacq::{Acquisition};
///
///
/// let acq = Acquisition::open("path/to/acquisition").unwrap();
///
/// // Get the number of events in the acquisition
/// let num_events = acq.len();
/// println!("Number of events: {}", num_events);
///
/// // Get event 5
/// let event = acq.get(5).unwrap();
/// ```
#[derive(Debug, Clone)]
pub struct Acquisition {
    /// Root directory of the acquisition.
    root: PathBuf,
}

impl Acquisition {
    /// Create an acquisition at the given path.
    #[tracing::instrument(err, skip(metadata))]
    pub fn create(root: PathBuf, metadata: &Metadata) -> Result<Self, AcquisitionError> {
        tracing::debug!("Creating acquisition: {root:?}");

        let metadata = metadata
            .to_yaml()
            .or(Err(AcquisitionError::InvalidMetadata))?;

        match create_dir(root.clone()) {
            Ok(()) => (),
            Err(e) if e.kind() == ErrorKind::AlreadyExists => Err(AcquisitionError::AlreadyExists)?,
            Err(_) => Err(AcquisitionError::InvalidPath)?,
        }

        std::fs::write(root.join("metadata.yml"), metadata)
            .or(Err(AcquisitionError::CreationError))?;

        Self::open(root)
    }

    /// Open the acquisition at the given path.
    pub fn open<P: AsRef<std::path::Path> + Debug>(root: P) -> Result<Self, AcquisitionError> {
        let root = root.as_ref().to_path_buf();
        match is_acquisition(&root) {
            true => Ok(Acquisition { root }),
            false => Err(AcquisitionError::InvalidPath),
        }
    }

    /// Give the acquisition a new home.
    ///
    ///
    /// # Errors
    /// - [`AcquisitionError::InvalidPath`] is returned if the source acquisition is no longer valid
    /// - [`AcquisitionError::AlreadyExists`] is returned if the destination path already exists
    /// - [`AcquisitionError::Unknown`] is returned if the acquisition could not be moved for some other reason.
    pub fn move_to<P: AsRef<std::path::Path>>(&mut self, dest: P) -> Result<(), AcquisitionError> {
        let source = self.path();
        let dest = dest.as_ref();
        // It's possible for the acquisition to become invalid after instantiation
        if !is_acquisition(source) {
            return Err(AcquisitionError::InvalidPath);
        }
        match fs::rename(self.path(), &dest) {
            Ok(()) => {
                tracing::info!("Moved acquisition from {:?} to {:?}", self.path(), dest);
                self.root = dest.to_path_buf();
                Ok(())
            }
            Err(e) if e.kind() == ErrorKind::AlreadyExists => Err(AcquisitionError::AlreadyExists),
            Err(e) => {
                tracing::error!(
                    "Failed to move acquisition from {:?} to {:?} due to {e:?}",
                    source,
                    dest
                );
                Err(AcquisitionError::Unknown)
            }
        }
    }

    /// Get the acquisition path.
    pub fn path(&self) -> &PathBuf {
        &self.root
    }

    /// Get the acquisition name.
    pub fn name(&self) -> String {
        self.root
            .file_name()
            .expect("could not get acquisition name")
            .to_str()
            .expect("invalid acquisition name")
            .to_owned()
    }

    /// Read the acquisition metadata.
    pub fn metadata(&self) -> Result<Metadata, MetadataError> {
        let metadata = self.metadata_str().or(Err(MetadataError::InvalidName))?;
        Metadata::try_from(metadata)
    }

    /// Read the acquisition metadata as a string.
    pub fn metadata_str(&self) -> Result<String, AcquisitionError> {
        let path = self.root.join("metadata.yml");
        fs::read_to_string(path).or(Err(AcquisitionError::AccessError(
            "failed to read metadata".to_string(),
        )))
    }

    /// Read the specified misc data from the disk.
    ///
    /// # Errors
    /// - [`AcquisitionError::NoSuchMiscData`] is returned if the misc data does not exist for this acquisition.
    /// - [`AcquisitionError::AccessError] is returned if the misc data exists but could not be read.
    pub fn misc_data(&self, kind: MiscDataKind) -> Result<MiscData, AcquisitionError> {
        let path = self.root.join(kind.to_string());
        match std::fs::read(path) {
            Ok(data) => Ok(MiscData::new(data, kind)),
            Err(e) if e.kind() == ErrorKind::NotFound => Err(AcquisitionError::NoSuchMiscData),
            Err(e) => Err(AcquisitionError::AccessError(e.to_string())),
        }
    }

    /// Write the specified misc data to disk.
    ///
    /// # Errors
    /// [`AcquisitionError::WriteError`] is returned if the misc data could not be written.
    pub fn set_misc_data(&self, data: &MiscData) -> Result<(), AcquisitionError> {
        let path = self.root.join(data.kind().to_string());
        std::fs::write(path, data.data()).or(Err(AcquisitionError::WriteError))
    }

    /// Get the last event in the acquisition.
    pub fn end(&mut self) -> Result<RawEvent, AcquisitionError> {
        let len = self.len()?;

        // avoid overflow from -1
        if len == 0 {
            Err(AcquisitionError::IndexOutOfBounds)
        } else {
            self.get(len - 1)
        }
    }

    /// Get an event at the given index.
    pub fn get(&self, mut index: usize) -> Result<RawEvent, AcquisitionError> {
        for chunk in self.iter_read_chunks() {
            let chunk_len = chunk.len()?;
            if index < chunk_len {
                return chunk.get(index);
            }
            index -= chunk_len;
        }
        Err(AcquisitionError::IndexOutOfBounds)
    }

    /// Get the events at the given indices.
    pub fn get_all(&mut self, indices: &Vec<usize>) -> Result<Vec<RawEvent>, AcquisitionError> {
        indices.iter().map(|i| self.get(*i)).collect()
    }

    /// Get the number of events in the acquisition.
    pub fn len(&self) -> Result<usize, AcquisitionError> {
        Ok(self
            .iter_read_chunks()
            .map(|chunk| chunk.len())
            .collect::<Result<Vec<_>, _>>()?
            .iter()
            .sum())
    }

    /// Get the total size of the acquisitions
    ///
    /// # Errors
    /// * [`AcquisitionError::AccessError`] if the acquisition directory or any
    ///   of its children could not be read.
    pub fn total_size(&self) -> Result<usize, AcquisitionError> {
        dir_size(&self.root).or(Err(AcquisitionError::AccessError(
            "failed to read acquisition".to_owned(),
        )))
    }

    /// Get the number of chunks in the acquisition.
    pub fn chunk_count(&self) -> usize {
        self.iter_read_chunks().count()
    }

    /// Returns an iterator yielding read-only chunk files.
    pub fn iter_read_chunks(&self) -> impl Iterator<Item = ReadChunkFile> + '_ {
        (0..)
            .map(|i| ReadChunkFile::open_with_index(&self.root, i))
            .take_while(|c| c.is_ok())
            .map(|chunk| chunk.unwrap())
    }
}

/// Acquisition metadata containing board parameters and registers.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Metadata {
    params: Params,
    registers: serde_yaml::Mapping,
}

impl Metadata {
    /// Returns the board model name, if present.
    pub fn model(&self) -> Option<String> {
        Some(self.params.model().to_owned())
    }

    /// Returns the board parameters.
    pub fn params(&self) -> &Params {
        &self.params
    }

    /// Returns the board registers.
    pub fn registers(&self) -> &serde_yaml::Mapping {
        &self.registers
    }

    /// Convenience method for serializing the metadata to YAML.
    pub fn to_yaml(&self) -> Result<String, MetadataError> {
        Ok(serde_yaml::to_string(self)?)
    }
}

impl TryInto<String> for Metadata {
    type Error = MetadataError;

    fn try_into(self) -> Result<String, Self::Error> {
        Ok(self.to_yaml()?)
    }
}

impl TryFrom<String> for Metadata {
    type Error = MetadataError;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        Ok(serde_yaml::from_str(&value)?)
    }
}

/// Board parameters.
///
/// This struct provides fast access to common board parameters, and
/// slightly slower access to less commonly-used parameters.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Params {
    model: String,
    channels: usize,
    windows: usize,
    samples: usize,

    ///
    #[serde(flatten)]
    others: serde_yaml::Mapping,
}

impl Params {
    /// Returns the board model.
    pub fn model(&self) -> &str {
        &self.model
    }

    /// Returns the number of channels on the board as indicated by NaluConfigs.
    pub fn channels(&self) -> usize {
        self.channels
    }

    /// Returns the number of windows in the sampling array as indicated by NaluConfigs.
    pub fn windows(&self) -> usize {
        self.windows
    }

    /// Returns the number of samples per window as indicated by NaluConfigs.
    pub fn samples(&self) -> usize {
        self.samples
    }

    /// Returns all other parameters as a mapping.
    ///
    /// The existence of certain parameters exist will vary from board to board, and
    /// don't have a well-defined structure. This method provides access to those
    /// parameters.
    pub fn others(&self) -> &serde_yaml::Mapping {
        &self.others
    }
}

/// Container for raw misc data.
///
/// Misc data is merely a big collection of raw bytes
/// without any means of interpreting it from the Rust side. The responsibility
/// for storing well-defined data and later interpreting it falls on the caller
/// of the API.
pub struct MiscData {
    /// The type of misc data
    pub(crate) kind: MiscDataKind,
    /// The raw misc data
    pub(crate) data: Vec<u8>,
}

impl MiscData {
    /// Create a new [`MiscData`] object from the given data and kind
    pub fn new(data: Vec<u8>, kind: MiscDataKind) -> Self {
        Self {
            kind: kind,
            data: data,
        }
    }

    /// The kind of data
    pub fn kind(&self) -> MiscDataKind {
        self.kind
    }

    /// Set the kind of data
    pub fn set_kind(&mut self, kind: MiscDataKind) {
        self.kind = kind
    }

    /// Get the raw data
    pub fn data(&self) -> &Vec<u8> {
        &self.data
    }

    /// Get the raw data as mutable
    pub fn data_mut(&mut self) -> &mut Vec<u8> {
        &mut self.data
    }

    /// Set the raw data
    pub fn set_data(&mut self, data: Vec<u8>) {
        self.data = data
    }

    /// Consume `self` and return the raw data
    pub fn into_data(self) -> Vec<u8> {
        self.data
    }
}

/// Representation of the misc data kind.
#[derive(Debug, Copy, Clone)]
pub enum MiscDataKind {
    ReadoutMetadata,
    PedestalsCalibration,
    TimingCalibration,
    AdcToMvCalibration,
}

impl ToString for MiscDataKind {
    fn to_string(&self) -> String {
        match *self {
            Self::ReadoutMetadata => "readout_metadata".to_string(),
            Self::PedestalsCalibration => "pedestals_calibration".to_string(),
            Self::TimingCalibration => "timing_calibration".to_string(),
            Self::AdcToMvCalibration => "adc2mv_calibration".to_string(),
        }
        .to_string()
    }
}

impl FromStr for MiscDataKind {
    type Err = MetadataError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "readout_metadata" => Ok(Self::ReadoutMetadata),
            "pedestals_calibration" => Ok(Self::PedestalsCalibration),
            "timing_calibration" => Ok(Self::TimingCalibration),
            "adc2mv_calibration" => Ok(Self::AdcToMvCalibration),
            _ => Err(MetadataError::InvalidName),
        }
    }
}
