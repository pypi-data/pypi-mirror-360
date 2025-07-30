//! PyO3 bindings to the [`Acquisition` crate](crate)
//!
//! The top-level `naluacquisition.pyi` file contains type declarations for everything here,
//! allowing IDEs to provide autocompletion.

use std::path::PathBuf;

use pyo3::{
    exceptions::PyKeyError,
    prelude::{
        pyclass, pyfunction, pymethods, PyResult, Python,
    },
    types::{IntoPyDict, PyBytes, PyDict},
    Py, PyObject, PyRef, PyRefMut, ToPyObject,
};

use crate::{
    acquisition::{MiscDataKind, Params},
    Acquisition,
};

use self::util::{load_misc_data, map_index_arg};

use super::{parsing::parse_to_dict, python_libs};



/// Pythonic wrapper around the [`crate::Acquisition`] class.
#[pyclass]
#[pyo3(name = "Acquisition")]
#[derive(Clone)]
pub struct PyAcquisition {
    pub inner: Acquisition,
    /// Dict object containing the board info from naluconfigs.
    pub metadata: PyObject,
    /// Acquisition params. Cached for parsing.
    pub params: Params,
}

#[pymethods]
impl PyAcquisition {
    /// Open an existing acquisition.
    ///
    /// `parse_by_default` is used to determine whether to parse events
    /// in the `__getitem__` function.
    #[new]
    #[pyo3(signature=(root))]
    fn __init__(py: Python, root: PathBuf) -> PyResult<Self> {
        let acq = Acquisition::open(root)?;
        let metadata = python_libs::yaml_safe_load(py, &acq.metadata_str()?)?;
        let params = acq.metadata()?.params().clone();
        Ok(Self {
            inner: acq,
            metadata,
            params,
        })
    }

    /// Check if the folder is a valid acquisition.
    #[getter]
    fn is_valid(&self) -> bool {
        crate::is_acquisition(self.inner.path())
    }

    /// Get the path to the acquisition directory.
    #[getter]
    fn path(&self) -> PyResult<String> {
        Ok(self.inner.path().to_str().unwrap().to_owned())
    }

    /// Get the name of the acquisition.
    #[getter]
    fn name(&self) -> PyResult<String> {
        Ok(self.inner.name().to_owned())
    }

    /// Get the number of chunks in the acquisition
    #[getter]
    fn chunk_count(&self) -> usize {
        self.inner.chunk_count()
    }

    /// Read the metadata from the acquisition.
    #[getter]
    fn metadata(&self) -> PyObject {
        self.metadata.clone()
    }

    /// Get acquisition params.
    #[getter]
    fn params(&self, py: Python) -> PyResult<PyObject> {
        let metadata: &PyDict = self.metadata.downcast(py)?;
        let params = metadata
            .get_item("params")
            .ok_or(PyKeyError::new_err("params"))?;
        Ok(params.into())
    }

    /// Read the readout metadata from the acquisition.
    #[getter]
    fn readout_metadata(&self) -> PyResult<Option<PyObject>> {
        load_misc_data(&self.inner, MiscDataKind::ReadoutMetadata)
    }

    /// Read pedestals calibration from the acquisition.
    #[getter]
    fn pedestals_calibration(&self) -> PyResult<Option<PyObject>> {
        load_misc_data(&self.inner, MiscDataKind::PedestalsCalibration)
    }

    /// Read ADC to mV calibration from the acquisition.
    #[getter]
    fn adc_to_mv_calibration(&self) -> PyResult<Option<PyObject>> {
        load_misc_data(&self.inner, MiscDataKind::AdcToMvCalibration)
    }

    /// Read timing calibration from the acquisition.
    #[getter]
    fn timing_calibration(&self) -> PyResult<Option<PyObject>> {
        load_misc_data(&self.inner, MiscDataKind::TimingCalibration)
    }

    /// Fetch a raw event as `bytes`.
    fn raw_event(&self, index: usize, py: Python) -> PyResult<PyObject> {
        let raw_data = PyBytes::new(py, &self.inner.get(index)?);
        let dict = [
            ("rawdata", raw_data.to_object(py)),
            ("pkg_num", index.to_object(py)),
            ("event_num", index.to_object(py)),
        ]
        .into_py_dict(py);
        Ok(dict.into())
    }

    /// Fetch a parsed event. Requires `naludaq` to be installed.
    fn parsed_event(&self, index: usize, py: Python) -> PyResult<PyObject> {
        let raw_data = self.inner.get(index)?;
        parse_to_dict(&self.params, raw_data, py)
    }

    /// Acquisition length
    fn __len__(&self) -> PyResult<usize> {
        Ok(self.inner.len()?)
    }

    /// Fetch either a parsed event (preferred) or a raw event.
    fn __getitem__(&self, index_or_slice: PyObject, py: Python) -> PyResult<PyObject> {
        let fetch = |i| self.parsed_event(i, py);
        map_index_arg(py, index_or_slice, self.inner.len()?, fetch)
    }

    /// Iterate over events.
    fn __iter__(slf: PyRef<Self>) -> PyResult<Py<IterEvents>> {
        let iter = IterEvents {
            acq: Py::new(slf.py(), slf.clone())?,
            index: 0,
        };
        Py::new(slf.py(), iter)
    }
}

/// Check if a folder is a valid acquisition.
#[pyfunction]
pub(crate) fn is_acquisition(path: PathBuf) -> bool {
    crate::is_acquisition(&path)
}

/// List all acquisitions in a directory.
#[pyfunction]
pub(crate) fn list_acquisitions(py: Python, root_dir: PathBuf) -> PyResult<Vec<PyAcquisition>> {
    let acqs = crate::list_acquisitions(&root_dir);
    Ok(acqs
        .into_iter()
        .map(|acq| PyAcquisition::__init__(py, acq.path().clone()))
        .filter_map(|acq| acq.ok())
        .collect())
}

/// Iterator over events in an acquisition
#[pyclass]
struct IterEvents {
    /// Source acquisition
    acq: Py<PyAcquisition>,
    /// Current event index
    index: usize,
}

#[pymethods]
impl IterEvents {
    #[new]
    fn new(acq: Py<PyAcquisition>) -> PyResult<Self> {
        Ok(Self { acq, index: 0 })
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<PyObject> {
        let py = slf.py();
        let event = {
            let acq = slf.acq.borrow(py);
            acq.__getitem__(slf.index.to_object(py), py).ok()
        }?;
        slf.index += 1;
        Some(event)
    }
}

/// Utility functions. These are not exposed to Python.
pub(crate) mod util {
    use pyo3::{
        exceptions::{PyIndexError, PyTypeError},
        types::PySlice,
        IntoPy, PyObject, PyResult, Python,
    };

    use crate::{
        acquisition::{MiscData, MiscDataKind},
        Acquisition,
    };

    use super::python_libs;

    /// Load misc data from an [`Acquisition`] and deserialize it.
    ///
    /// Depends on the `pickle` and `gzip` libraries.
    pub(crate) fn load_misc_data(
        acq: &Acquisition,
        kind: MiscDataKind,
    ) -> PyResult<Option<PyObject>> {
        match acq.misc_data(kind) {
            Ok(data) => Ok(Some(deserialize_misc_data(data)?)),
            Err(crate::AcquisitionError::NoSuchMiscData) => Ok(None),
            Err(e) => Err(e.into()),
        }
    }

    /// Uses `pickle` and `gzip` to deserialize a [`MiscData`] object.
    pub(crate) fn deserialize_misc_data(MiscData { data, .. }: MiscData) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            Ok(python_libs::pickle_loads(py, &python_libs::gzip_decompress(py, &data)?)?.into())
        })
    }

    /// Utility for handling indexing with either an int or a slice.
    ///
    /// For slices this will call `f` on each index and returning a list of the results.
    pub(crate) fn map_index_arg<F, T>(
        py: Python,
        index_or_slice: PyObject,
        len: usize,
        f: F,
    ) -> PyResult<PyObject>
    where
        F: Fn(usize) -> PyResult<T>,
        T: IntoPy<PyObject>,
        Vec<PyObject>: FromIterator<T>,
        PyObject: From<T>,
    {
        let index_or_slice = index_or_slice.as_ref(py);
        let py = index_or_slice.py();
        if let Ok(slice) = index_or_slice.downcast::<PySlice>() {
            map_slice(py, slice, len, f)
        } else if let Ok(index) = index_or_slice.extract::<isize>() {
            if index < 0 {
                return Err(PyIndexError::new_err("index out of bounds"));
            }
            Ok(f(index as usize)?.into())
        } else {
            Err(PyTypeError::new_err("index must be an int or a slice"))
        }
    }

    /// Map a function to a slice by iterating over the indices.
    ///
    /// The results are returned as a python list if all functions returned [`Ok`].
    fn map_slice<F, T>(py: Python, slice: &PySlice, len: usize, f: F) -> PyResult<PyObject>
    where
        F: Fn(usize) -> PyResult<T>,
        T: IntoPy<PyObject>,
        Vec<PyObject>: FromIterator<T>,
    {
        let indices = slice.indices((len as i32).into())?;
        if indices.start < 0 || indices.stop < 0 || indices.step < 0 {
            return Err(PyIndexError::new_err("index out of bounds"));
        }
        let results: Vec<PyObject> = (indices.start..indices.stop)
            .step_by(indices.step as usize)
            .map(|i| f(i as usize))
            .collect::<PyResult<Vec<PyObject>>>()?;
        Ok(results.into_py(py))
    }
}
