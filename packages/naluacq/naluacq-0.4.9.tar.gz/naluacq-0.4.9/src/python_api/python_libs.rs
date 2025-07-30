//! Contains some wrappers for frequently-used python functions.
//!
//! These functions are cached to minimize import/lookup times.

use pyo3::prelude::PyModule;
use pyo3::types::PyBytes;
use pyo3::{once_cell::GILOnceCell, PyObject, PyResult, Python};

/// Cache for the `pickle.loads()` function.
static PICKLE_LOADS: GILOnceCell<PyObject> = GILOnceCell::new();
/// Cache for the `gzip.decompress()` function.
static GZIP_DECOMPRESS: GILOnceCell<PyObject> = GILOnceCell::new();
/// Cache for the `yaml.safe_load()` function.
static YAML_SAFE_LOAD: GILOnceCell<PyObject> = GILOnceCell::new();

/// Pass-through to `pickle.loads()`.
pub fn pickle_loads(py: Python, data: &PyObject) -> PyResult<PyObject> {
    PICKLE_LOADS
        .get_or_try_init(py, || {
            let pickle = PyModule::import(py, "pickle")?;
            PyResult::Ok(pickle.getattr("loads")?.into())
        })?
        .call1(py, (data,))
}

/// Pass-through to `gzip.decompress()`.
pub fn gzip_decompress(py: Python, data: &Vec<u8>) -> PyResult<PyObject> {
    GZIP_DECOMPRESS
        .get_or_try_init(py, || {
            let gzip = PyModule::import(py, "gzip")?;
            PyResult::Ok(gzip.getattr("decompress")?.into())
        })?
        .call1(py, (PyBytes::new(py, data),))
}

/// Pass-through to `yaml.safe_load()`.
pub fn yaml_safe_load(py: Python, data: &str) -> PyResult<PyObject> {
    YAML_SAFE_LOAD
        .get_or_try_init(py, || {
            let yaml = PyModule::import(py, "yaml")?;
            PyResult::Ok(yaml.getattr("safe_load")?.into())
        })?
        .call1(py, (data,))
}
