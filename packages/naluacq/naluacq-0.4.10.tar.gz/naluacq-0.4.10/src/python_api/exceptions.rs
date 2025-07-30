//! Helpers for python exceptions
use pyo3::create_exception;
use pyo3::exceptions::*;
use pyo3::prelude::*;

create_exception!(acquisition, FullChunkError, pyo3::exceptions::PyException);
create_exception!(acquisition, MetadataError, pyo3::exceptions::PyException);
create_exception!(acquisition, ParsingError, pyo3::exceptions::PyException);
create_exception!(acquisition, ExportError, pyo3::exceptions::PyException);

/// Lets us use `.into()` to easily convert `AcquisitionError` to several different
/// types of python exceptions.
impl From<crate::AcquisitionError> for PyErr {
    fn from(e: crate::AcquisitionError) -> Self {
        map_acq_error(e)
    }
}

/// Lets us use `.into()` to easily convert `ParsingError` to several different
/// types of python exceptions.
impl From<crate::ParsingError> for PyErr {
    fn from(e: crate::ParsingError) -> Self {
        ParsingError::new_err(format!("Failed to parse event: {}", e))
    }
}

/// Lets us use `.into()` to easily convert `ParsingError` to several different
/// types of python exceptions.
impl From<crate::MetadataError> for PyErr {
    fn from(e: crate::MetadataError) -> Self {
        MetadataError::new_err(format!("Could not process metadata: {}", e))
    }
}

/// Lets us use `.into()` to easily convert `ExportError` to several different
/// types of python exceptions.
impl From<crate::ExportError> for PyErr {
    fn from(e: crate::ExportError) -> Self {
        ExportError::new_err(format!("Could not export: {}", e))
    }
}

/// Map an [`AcquisitionError`](crate::AcquisitionError) to a python exception.
///
/// Some error variants are mapped to built-in Python exceptions, while others
/// use the custom exceptions defined in this module.
pub fn map_acq_error(e: crate::AcquisitionError) -> PyErr {
    match e {
        crate::AcquisitionError::InvalidPath => PyFileNotFoundError::new_err("Invalid path"),
        crate::AcquisitionError::AlreadyExists => {
            PyFileExistsError::new_err("Acquisition already exists")
        }
        crate::AcquisitionError::CreationError => {
            PyIOError::new_err("Could not create acquisition")
        }
        crate::AcquisitionError::AccessError(e) => {
            PyIOError::new_err(format!("Could not read acquisition: {}", e))
        }
        crate::AcquisitionError::IndexOutOfBounds => PyIndexError::new_err("Index out of bounds"),
        crate::AcquisitionError::FullChunk => FullChunkError::new_err("Chunk capacity exceeded"),
        crate::AcquisitionError::WriteError => PyIOError::new_err("Failed to write data"),
        crate::AcquisitionError::MetadataMissing => {
            MetadataError::new_err("Acquisition is missing metadata")
        }
        crate::AcquisitionError::MetadataAlreadyWritten => {
            MetadataError::new_err("Cannot write metadata twice")
        }
        crate::AcquisitionError::NoSuchMiscData => {
            PyValueError::new_err("No such misc data".to_owned())
        }
        crate::AcquisitionError::InvalidMetadata => {
            PyValueError::new_err("Invalid metadata".to_owned())
        }
        crate::AcquisitionError::Unknown => {
            PyIOError::new_err("Unknown error".to_owned())
        }
    }
}
