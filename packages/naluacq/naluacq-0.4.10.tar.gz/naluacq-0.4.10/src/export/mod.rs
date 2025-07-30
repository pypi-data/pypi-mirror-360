//! This module provides a way to export events to CSV.
//!
//! The [`ExportCsv`] trait is implemented for `Iterator<Item = E>` where `E: Event`, which
//! allows for exporting events to CSV using the `export_csv` method.
//!
//! Another method, [`export_csv_from_acq`] is provided for more fine-grained control over
//! the export process. The method may be faster(?) as it attempts to parallelize the export.

use crate::error::ExportError;

pub use self::csv::{export_csv_from_acq, ExportCsv};

pub(crate) mod csv;

pub type Result<T, E = ExportError> = core::result::Result<T, E>;
