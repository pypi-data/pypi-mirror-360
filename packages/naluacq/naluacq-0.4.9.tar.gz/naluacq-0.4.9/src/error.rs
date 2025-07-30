/// Errors used when accessing an [`Acquisition`](crate::acquisition::Acquisition).
#[derive(thiserror::Error, Debug, Clone)]
pub enum AcquisitionError {
    /// An acquisition could not be read from/written to the given path
    #[error("invalid path")]
    InvalidPath,
    /// The acquisition could not be created because it already exists.
    #[error("already exists")]
    AlreadyExists,
    /// Failed to create the acquisition
    #[error("cannot create acquisition")]
    CreationError,
    /// Failed to access some portion of the acquisition
    #[error("cannot access some portion of the acquisition")]
    AccessError(String),
    /// Attempted to access an event at an index which is out of bounds.
    #[error("bad event index")]
    IndexOutOfBounds,
    /// Could not write an event to the chunk because it is full.
    #[error("chunk is full")]
    FullChunk,
    /// Failed to write data to the chunk.
    #[error("failed to write data")]
    WriteError,
    /// An event was written before the metadata.
    #[error("metadata must be written before events")]
    MetadataMissing,
    /// Metadata was already written.
    #[error("cannot write metadata twice")]
    MetadataAlreadyWritten,
    /// The metadata is in an invalid structure.
    #[error("invalid metadata")]
    InvalidMetadata,
    /// Calibration type does not exist
    #[error("invalid calibration type")]
    NoSuchMiscData,
    /// Unknown error
    #[error("unknown")]
    Unknown,
}

/// Errors used when metadata access fails
#[derive(thiserror::Error, Debug)]
pub enum MetadataError {
    #[error("invalid metadata format")]
    InvalidFormat,
    #[error("invalid metadata format")]
    InvalidName,
    #[error("failed to serialized")]
    SerializationError(#[from] serde_yaml::Error),
}

/// Errors used when parsing events.
#[derive(Debug, thiserror::Error)]
pub enum ParsingError {
    #[error("provided parameters are invalid")]
    InvalidParameters,
    #[error("unexpected length of data")]
    UnexpectedLength,
    #[error("invalid channel number")]
    InvalidChannel,
    #[error("invalid window label")]
    InvalidWindow,
    #[error("required data missing when parsing")]
    MissingData,
    #[error("Encountered an empty Package which can't be parsed")]
    PackageEmpty,
    #[error("data is from an unsupported board model")]
    UnsupportedModel,
    #[error("unknown")]
    Other,
}

/// Errors used when exporting data.
#[derive(Debug, thiserror::Error)]
pub enum ExportError {
    #[error("invalid path")]
    InvalidPath,
    #[error("file access was denied")]
    AccessDenied,
    #[error("invalid format")]
    InvalidFormat,
    #[error("specified options are invalid for the data being exported")]
    InvalidOptions,
    #[error("error occurred while exporting as csv")]
    CsvError(#[from] csv::Error),
    #[error("error occurred while parsing")]
    ParsingError(#[from] ParsingError),
    #[error("error occurred while accessing acquisition")]
    MetadataError(#[from] MetadataError),
    #[error("unknown")]
    Unknown,
}

impl From<std::io::Error> for ExportError {
    fn from(e: std::io::Error) -> Self {
        match e {
            e if e.kind() == std::io::ErrorKind::NotFound => Self::InvalidPath,
            e if e.kind() == std::io::ErrorKind::PermissionDenied => Self::AccessDenied,
            _ => ExportError::Unknown,
        }
    }
}

/// Errors used when accessing miscellaneous data fails.
#[derive(Debug, thiserror::Error)]
pub enum MiscDataError {
    #[error("invalid path")]
    InvalidPath,
    #[error("file access was denied")]
    AccessDenied,
    #[error("the misc data is invalid")]
    InvalidMiscData,
    #[error("serialization or deserialization failed")]
    SerializationError(#[from] serde_pickle::Error),
    #[error("unknown")]
    Unknown,
}

impl From<std::io::Error> for MiscDataError {
    fn from(e: std::io::Error) -> Self {
        match e {
            e if e.kind() == std::io::ErrorKind::NotFound => Self::InvalidPath,
            e if e.kind() == std::io::ErrorKind::PermissionDenied => Self::AccessDenied,
            e if e.kind() == std::io::ErrorKind::InvalidData => Self::InvalidMiscData,
            e if e.kind() == std::io::ErrorKind::UnexpectedEof => Self::InvalidMiscData,
            _ => MiscDataError::Unknown,
        }
    }
}

/// Errors used when accessing correcting events fails.
#[derive(Debug, thiserror::Error)]
pub enum CalibrationError {
    #[error("pedestals correction failed")]
    PedestalsCorrectionFailed,
    #[error("invalid data shape")]
    InvalidDataShape,
}
