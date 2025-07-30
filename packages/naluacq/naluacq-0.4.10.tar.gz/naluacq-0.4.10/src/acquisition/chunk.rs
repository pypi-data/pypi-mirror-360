use std::{
    fmt::Debug,
    fs::{File, OpenOptions},
    io::{BufWriter, Write},
    path::{Path, PathBuf},
};

use memmap2::Mmap;
use zerocopy::{AsBytes, FromBytes};

use super::{
    constants::{
        CHUNK_BUFFERING_FACTOR, DEFAULT_CHUNK_CAPACITY, ENABLE_STORAGE_LOGGING,
        LATEST_CHUNK_VERSION,
    },
    AcquisitionError, RawEvent,
};

/// Utility for reading a chunk file.
pub struct ReadChunkFile {
    /// Handle to the bin file.
    bin_file: File,
    /// Handle to the index file.
    index_file: File,
}

impl ReadChunkFile {
    /// Open the chunk file with the bin/index files.
    pub fn open(
        bin_path: impl AsRef<Path>,
        index_path: impl AsRef<Path>,
    ) -> Result<Self, AcquisitionError> {
        let bin_file = OpenOptions::new()
            .read(true)
            .open(bin_path)
            .or(Err(AcquisitionError::InvalidPath))?;
        let index_file = OpenOptions::new()
            .read(true)
            .open(index_path)
            .or(Err(AcquisitionError::InvalidPath))?;
        Ok(Self {
            bin_file,
            index_file,
        })
    }

    /// Open a chunk with the given index under the given acquisition root.
    pub fn open_with_index(root: impl AsRef<Path>, index: usize) -> Result<Self, AcquisitionError> {
        let root = root.as_ref();
        Self::open(
            root.join(format!("{index}.bin")),
            root.join(format!("{index}.idx")),
        )
    }

    /// Get the number of events in the chunk.
    pub fn len(&self) -> Result<usize, AcquisitionError> {
        const ENTRY_SIZE: usize = std::mem::size_of::<IndexEntry>();
        let mmap = Self::make_mmap(&self.index_file)?;
        Ok(mmap.len() / ENTRY_SIZE)
    }

    /// Get an event at the given index.
    pub fn get(&self, index: usize) -> Result<RawEvent, AcquisitionError> {
        let index_entry = self.entry(index)?;
        let start = index_entry.offset as usize;
        let end = start + index_entry.length as usize;

        // Need to rebuild the mmap since the underlying file can change between builds
        let bin_mmap = Self::make_mmap(&self.bin_file)?;
        Ok(bin_mmap
            .get(start..end)
            .ok_or(AcquisitionError::IndexOutOfBounds)?
            .to_vec())
    }

    /// Get the index entry for an event at the given index.
    fn entry(&self, index: usize) -> Result<IndexEntry, AcquisitionError> {
        const ENTRY_SIZE: usize = std::mem::size_of::<IndexEntry>();

        // Need to rebuild the mmap since the underlying file can change between builds
        let index_mmap = Self::make_mmap(&self.index_file)?;
        if ENTRY_SIZE * (index + 1) > index_mmap.len() {
            return Err(AcquisitionError::IndexOutOfBounds);
        }
        IndexEntry::read_from(&index_mmap[ENTRY_SIZE * index..ENTRY_SIZE * (index + 1)]).ok_or(
            AcquisitionError::AccessError(String::from("failed to read index file")),
        )
    }

    /// Get the physical size of the data file on disk
    pub fn physical_size(&self) -> Result<usize, AcquisitionError> {
        Ok(self
            .bin_file
            .metadata()
            .or(Err(AcquisitionError::AccessError(
                "Failed to read binary file metadata".to_string(),
            )))?
            .len() as _)
    }

    /// Build a read-only mmap for the given file
    fn make_mmap(file: &File) -> Result<Mmap, AcquisitionError> {
        unsafe { Ok(Mmap::map(file).or(Err(AcquisitionError::InvalidPath))?) }
    }
}

/// Builder for a [`WriteChunkFile`].
#[derive(Debug, Clone)]
pub struct WriteChunkFileBuilder {
    /// Maximum capacity for the chunk in bytes
    capacity: usize,
    /// Buffer size for events in bytes.
    buffering: usize,
    /// Metadata for the event.
    ///
    /// If `Some`, the metadata is written on open.
    metadata: Option<String>,
}

impl WriteChunkFileBuilder {
    /// Creates a new builder for a [`WriteChunkFile`].
    pub fn new() -> Self {
        Self::with_capacity(DEFAULT_CHUNK_CAPACITY)
    }

    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            buffering: page_size::get() * CHUNK_BUFFERING_FACTOR,
            capacity,
            metadata: None,
        }
    }

    /// Opens the chunk at the given location.
    ///
    /// # Errors
    /// An [`AcquisitionError`] is returned if the chunk could not be opened.
    pub fn open(
        &self,
        acq_root: &PathBuf,
        index: usize,
    ) -> Result<WriteChunkFile, AcquisitionError> {
        let bin_file = Self::open_bin(&acq_root.join(format!("{index}.bin")))?;
        let index_file = Self::open_index(&acq_root.join(format!("{index}.idx")))?;

        let mut chunk = WriteChunkFile {
            bin_file: bin_file
                .try_clone()
                .or(Err(AcquisitionError::CreationError))?,
            buf_bin_file: BufWriter::new(bin_file),
            index_file,
            metadata_sector_written: false,
            allocated: false,
            buffering: self.buffering,
            capacity: self.capacity,
            last_event_offset: 0,
        };
        if let Some(ref metadata) = self.metadata {
            chunk.write_metadata(metadata)?;
        }
        Ok(chunk)
    }

    /// Set the maximum capacity of the chunk file.
    /// If unspecified, the value is assumed to be the global default.
    pub fn capacity(&mut self, capacity: usize) -> &mut Self {
        self.capacity = capacity;
        self
    }

    /// Set the event buffer capacity.
    /// If unspecified, the value is a default multiple of the disk page size.
    pub fn buffering(&mut self, buffering: usize) -> &mut Self {
        self.buffering = buffering;
        self
    }

    /// Set the chunk metadata.
    /// If specified, this will write the metadata on open.
    pub fn metadata(&mut self, metadata: &str) -> &mut Self {
        self.metadata = Some(metadata.to_string());
        self
    }

    /// Open the binary file for writing.
    fn open_bin(path: &PathBuf) -> Result<File, AcquisitionError> {
        // use std::os::windows::prelude::OpenOptionsExt;
        // use winapi::um::winbase::*;
        OpenOptions::new()
            // .custom_flags(FILE_FLAG_NO_BUFFERING)
            .read(true)
            .write(true)
            .create(true)
            .open(path)
            .or(Err(AcquisitionError::InvalidPath))
    }

    /// Open the index file for writing.
    fn open_index(path: &PathBuf) -> Result<File, AcquisitionError> {
        OpenOptions::new()
            .write(true)
            .create(true)
            .open(path)
            .or(Err(AcquisitionError::InvalidPath))
    }
}

/// Utility for writing events to a chunk file.
pub struct WriteChunkFile {
    /// Handle to the binary file.
    bin_file: File,
    /// Buffered writer for the binary file.
    buf_bin_file: BufWriter<File>,
    /// Handle to the index file.
    index_file: File,
    /// Whether the metadata sector has been written yet
    metadata_sector_written: bool,
    /// Whether the file has been allocated
    allocated: bool,
    /// Amount of data to store in the buffer before flushing
    buffering: usize,
    /// Capacity of the chunk file in bytes
    capacity: usize,
    /// Number of bytes written to disk
    last_event_offset: usize,
}

impl WriteChunkFile {
    /// Creates a new builder for this type.
    pub fn builder() -> WriteChunkFileBuilder {
        WriteChunkFileBuilder::new()
    }

    /// Writes the given metadata to the beginning of the bin file.
    pub fn write_metadata(&mut self, metadata: &String) -> Result<(), AcquisitionError> {
        if self.metadata_sector_written {
            return Err(AcquisitionError::MetadataAlreadyWritten);
        }

        let header = MetadataSectorHeader {
            version: LATEST_CHUNK_VERSION as _,
            metadata_sector_length: metadata.len() as _,
            _reserved: 0,
        };

        self.buf_bin_file
            .write(header.as_bytes())
            .or(Err(AcquisitionError::CreationError))?;
        self.buf_bin_file
            .write(metadata.as_bytes())
            .or(Err(AcquisitionError::CreationError))?;
        self.buf_bin_file
            .flush()
            .or(Err(AcquisitionError::CreationError))?;
        self.last_event_offset = std::mem::size_of::<MetadataSectorHeader>() + metadata.len();
        self.metadata_sector_written = true;
        Ok(())
    }

    /// Get the number of outstanding bytes not written to disk.
    pub fn unwritten_amount(&self) -> usize {
        self.buf_bin_file.buffer().len()
    }

    /// Check if the chunk has the capacity to fit an additional event.
    #[inline]
    pub fn can_fit(&self, event: &RawEvent) -> bool {
        self.last_event_offset + event.len() < self.capacity
    }

    /// Writes an event to the chunk.
    ///
    /// If the chunk cannot accept any more events, an [`AcquisitionError::FullChunk`] error is returned.
    pub fn write(&mut self, event: RawEvent) -> Result<(), AcquisitionError> {
        if !self.metadata_sector_written {
            return Err(AcquisitionError::MetadataMissing);
        }
        if !self.can_fit(&event) {
            return Err(AcquisitionError::FullChunk);
        }
        self.allocate()?;

        let entry = IndexEntry {
            offset: self.last_event_offset as _,
            length: event.len() as _,
        };
        self.last_event_offset += event.len();

        self.buf_bin_file
            .write_all(&event)
            .or(Err(AcquisitionError::WriteError))?;
        self.index_file
            .write_all(entry.as_bytes())
            .or(Err(AcquisitionError::WriteError))?;

        Ok(())
    }

    /// Flushes all outstanding data to disk.
    pub fn flush(&mut self) -> Result<(), AcquisitionError> {
        self.buf_bin_file
            .flush()
            .or(Err(AcquisitionError::WriteError))?;
        self.index_file
            .flush()
            .or(Err(AcquisitionError::WriteError))?;
        Ok(())
    }

    /// Truncates the binary data file to the smallest possible size.
    /// If additional data is written later, it will require reallocation
    /// of the file.
    ///
    /// Any outstanding data will be flushed before truncating the file.
    #[tracing::instrument(err)]
    pub fn truncate(&mut self) -> Result<(), AcquisitionError> {
        tracing::debug!("Finalizing chunk");
        self.flush()?;

        self.bin_file
            .set_len(self.last_event_offset as _)
            .or(Err(AcquisitionError::WriteError))?;
        Ok(())
    }

    /// Allocates space for the file on disk. If successful,
    /// the file size will be that of the requested capacity.
    #[tracing::instrument(err)]
    fn allocate(&mut self) -> Result<(), AcquisitionError> {
        if self.allocated {
            return Ok(());
        }
        if ENABLE_STORAGE_LOGGING {
            tracing::debug!(
                "Allocating chunk with capacity {} MB",
                self.capacity / 1_000_000
            );
        }
        self.bin_file
            .set_len(self.capacity as _)
            .or(Err(AcquisitionError::WriteError))?;
        self.allocated = true;
        Ok(())
    }
}

impl Drop for WriteChunkFile {
    /// Truncates the file on drop.
    fn drop(&mut self) {
        let _ = self.truncate();
    }
}

impl Debug for WriteChunkFile {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("WriteChunkFile")
            .field("allocated", &self.allocated)
            .field("bin_file", &self.buf_bin_file)
            .field("buffering", &self.buffering)
            .field("capacity", &self.capacity)
            .field("last_event_offset", &self.last_event_offset)
            .field("unwritten_amount", &self.unwritten_amount())
            .finish()
    }
}

/// Represents an entry in the index file.
///
/// Comes with zero-copy methods for interpreting the struct as/from bytes.
#[derive(FromBytes, AsBytes, Debug)]
#[repr(C)]
struct IndexEntry {
    /// Offset in bytes of the event in the chunk.
    offset: u32,
    /// Length of the event
    length: u32,
}

/// Represents the header of the metadata sector of a bin file.
///
/// Comes with zero-copy methods for interpreting the struct as/from bytes.
#[derive(FromBytes, AsBytes, Debug)]
#[repr(C)]
struct MetadataSectorHeader {
    /// Format revision number
    version: u16,
    /// Padding to make the header a power of two
    _reserved: u16,
    /// Length of the metadata sector
    metadata_sector_length: u32,
}
