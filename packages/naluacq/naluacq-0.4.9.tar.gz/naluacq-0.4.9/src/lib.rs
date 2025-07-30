//! naluacq is a Rust crate for I/O with Nalu Scientific acquisitions in the GbE-compatible format.
//!
//! The crate encompasses the following:
//! - Reading acquisitions
//! - Writing acquisitions (mainly used by `naludaq_rs`)
//! - Parsing events from acquisitions
//! - Calibration of events
//! - Exporting acquisitions to other formats
//!
//! Some of these features are made available in the Python (PyO3) bindings for this crate.
//!
//! # Structure of Acquisitions
//!
//! An acquisition in the new format is a directory containing multiple files describing various
//! aspects of the acquisition.
//!
//! - `{n}.bin` - binary event data file "n" (up to 500 MB) containing raw events back-to-back
//! - `{n}.idx` - index file containing the offset and length of each event in the corresponding .bin file
//! - `metadata.yml` - user-defined string metadata. NaluDAQ uses this to store board parameters and registers.
//! - `readout_metadata` - more user-defined binary metadata. NaluDAQ uses this for extra information about the readout.
//! - `[pedestals_calibration]` - optional binary file containing pedestal calibration data
//! - `[timing_calibration]` - optional binary file containing timing calibration data
//! - `[adc2mv_calibration]` - optional binary file containing ADC to mV calibration data
//!
//! ## Event Storage
//!
//! Events are stored in groups of 500 MB maximum known as "chunks." Each chunk is represented using two files: a `.bin` file
//! which contains the raw event data and an `.idx` file which points to each event in the `.bin` file.
//!
//! ### Bin File
//!
//! Events are stored back-to-back in the `.bin` files as unparsed binary data. A maximum of 500 MB (at the time of writing) is
//! allowed to be stored in a single `.bin` file. The rough structure is as follows:
//!
//! 1. Metadata Sector
//!     - 8-byte header indicating file version type and sector length
//!     - user-defined metadata stored as raw bytes
//! 2. Data Sector
//!     - Event 1 (raw bytes)
//!     - Event 2 (raw bytes)
//!     - ...
//!
//! ### Idx File
//!
//! Because searching through the entire file for a specific event would be painfully slow, an index file is
//! used to store the offset and length of each event in the corresponding `.bin` file. The index file is
//! comprised of several 8-byte entries, each indicating the offset and length of a single event in the `.bin` file.
//! A specific event can be found by reading the entry at `8 * index` bytes and then reading `length` bytes from
//! the `.bin` file starting at `offset` bytes.
//!
//!
//! # Examples
//!
//!
//! ## Reading an Acquisition
//!
//! ```no_run
//! use naluacq::Acquisition;
//!
//! let acq = Acquisition::open("path/to/acquisition.acq").unwrap();
//!
//! let idx = 0;
//! let raw_event = acq.get(idx).unwrap()
//! ```
//!
//!
//! ### Parsing an Acquisitions
//!
//!
//! ```no_run
//! use naluacq::{Acquisition, Aardvarcv3Event, ParseInto};
//!
//! let acq = Acquisition::open("path/to/acquisition.acq").unwrap();
//!
//! let idx = 0;
//! let raw_event = acq.get(idx).unwrap()
//!
//! let parsed_event: Aardvarcv3Event = raw_event.parse_into().unwrap();
//! ```

pub use acquisition::{
    util::{is_acquisition, list_acquisitions, list_acquisitions_async},
    Acquisition,
};
pub use calibration::Pedestals;
pub use error::{
    AcquisitionError, CalibrationError, ExportError, MetadataError, MiscDataError, ParsingError,
};
pub use parsing::{
    Aardvarcv3Event, AodsocEvent, Aodsv2Event, Asocv3Event, Asocv3SEvent, Hdsocv1Event, ParseInto,
    Trbhmv1Event, Udc16Event, Upac96Event,
};
use parsing::{Sample, TimeStamp, WindowLabel};

pub mod acquisition;
pub mod calibration;
mod error;
pub mod export;
pub mod parsing;
mod python_api;
pub mod ecc;
pub(crate) mod util;

pub type RawEvent = Vec<u8>;

/// Trait declaring the necessary methods for interpreting a type as an Event.
/// Each board model has its own event type which implements this trait.
///
/// This trait is implemented for the various types of events.
pub trait Event: Clone {
    /// Returns the event's data.
    ///
    /// The data is indexed as [channel][sample]
    fn data(&self) -> &Vec<Vec<Sample>>;
    /// Returns the event's data as mutable.
    ///
    /// The data is indexed as [channel][sample]
    fn data_mut(&mut self) -> &mut Vec<Vec<Sample>>;
    /// Returns the event's window labels.
    ///
    /// The window labels are indexed as [channel][window]
    fn window_labels(&self) -> &Vec<Vec<WindowLabel>>;
    /// Returns the event's time axis.
    ///
    /// The time axis is indexed as [channel][sample]
    fn time(&self) -> &Vec<Vec<TimeStamp>>;
    /// Returns the event's channel timing.
    ///
    /// For most data formats this will return `None` by default.
    fn channel_timing(&self) -> Option<&Vec<Vec<u32>>> {
        None
    }
    /// Returns the event's ecc errors.
    /// 
    /// This is a list of errors detected by the ECC algorithm, only for UPAC96, else it returns `None`.
    fn ecc_errors(&self) -> Option<&Vec<Vec<(usize, usize, u16, u16, u16)>>> { // (byte number, sample number, rawbyte, syndrome, global parity)>>> {
        None
    }
}
