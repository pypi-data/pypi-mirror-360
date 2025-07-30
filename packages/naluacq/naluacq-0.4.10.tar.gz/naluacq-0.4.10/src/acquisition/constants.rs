/// Default maximum file size for acquisition chunks.
pub const DEFAULT_CHUNK_CAPACITY: usize = 500_000_000;
/// Multiple of the disk page size to use for buffering the data file.
/// A small value will result in small but frequent writes, while a larger
/// value will result in large but infrequent writes. Too small or too large
/// a value will have a negative impact on performance.
pub const CHUNK_BUFFERING_FACTOR: usize = 256;
/// Enable storage logging
pub const ENABLE_STORAGE_LOGGING: bool = true;
/// Latest chunk file version number
pub const LATEST_CHUNK_VERSION: usize = 1;
