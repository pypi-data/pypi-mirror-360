use std::path::{Path, PathBuf};

use crate::Acquisition;

/// List all acquisitions in the given directory.
pub fn list_acquisitions(root: impl AsRef<Path>) -> Vec<Acquisition> {
    let dirs: Vec<std::fs::DirEntry> = match std::fs::read_dir(root) {
        Ok(dirs) => dirs.filter_map(|e| e.ok()).collect(),
        Err(_) => return Vec::new(),
    };

    dirs.into_iter()
        .filter_map(|f| Acquisition::open(f.path()).ok())
        .collect()
}

/// List all acquisitions in the given directory, but about 2x faster than sync code.
pub async fn list_acquisitions_async(root: impl AsRef<Path>) -> Vec<Acquisition> {
    const JOBS_PER_TASK: usize = 20;
    let dirs: Vec<PathBuf> = match tokio::fs::read_dir(root).await {
        Ok(mut dirs) => {
            let mut result = Vec::new();
            while let Ok(Some(entry)) = dirs.next_entry().await {
                result.push(entry.path());
            }
            result
        }
        Err(_) => return Vec::new(),
    };
    let handles = dirs
        .chunks(JOBS_PER_TASK)
        .map(|dirs_to_check| {
            let dirs_to_check = dirs_to_check.to_owned();
            tokio::task::spawn_blocking(move || {
                dirs_to_check
                    .into_iter()
                    .filter_map(|f| Acquisition::open(f).ok())
                    .collect::<Vec<Acquisition>>()
            })
        })
        .collect::<Vec<_>>();

    let mut acqs = Vec::with_capacity(dirs.len());
    for handle in handles {
        let acq_chunk = handle.await.unwrap();
        acqs.extend(acq_chunk);
    }
    acqs
}

/// Checks if the given directory is an acquisition.
pub fn is_acquisition(root: impl AsRef<Path>) -> bool {
    let root = root.as_ref();
    root.exists() && root.is_dir() && root.join("metadata.yml").exists()
}

/// Recursively compute the size of a directory.
///
/// # Errors
/// May fail if the path is not a directory, or if the directory or
/// any children cannot be read.
pub(crate) fn dir_size(path: impl AsRef<Path>) -> std::io::Result<usize> {
    fn dir_size(mut dir: std::fs::ReadDir) -> std::io::Result<usize> {
        dir.try_fold(0, |acc, file| {
            let file = file?;
            let size = match file.metadata()? {
                data if data.is_dir() => dir_size(std::fs::read_dir(file.path())?)?,
                data => data.len() as usize,
            };
            Ok(acc + size)
        })
    }
    dir_size(std::fs::read_dir(path.as_ref())?)
}
