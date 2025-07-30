use crate::{acquisition::Params, util::dispatch_by_event_type, Event, ParseInto, ParsingError};

use pyo3::{
    prelude::{PyResult, Python, pyfunction},
    types::IntoPyDict, types::PyDict,
    PyObject, ToPyObject,
};

pub fn parse_to_dict(params: &Params, raw_event: Vec<u8>, py: Python) -> PyResult<PyObject> {
    dispatch_by_event_type!(
        params.model(),
        ParsingError::UnsupportedModel,
        parse_generic,
        params,
        raw_event,
        py
    )?
}

fn parse_generic<T: Event>(params: &Params, raw_event: Vec<u8>, py: Python) -> PyResult<PyObject>
where
    [u8]: ParseInto<T>,
{
    let event: T = raw_event.parse_into(params)?;
    let dict = [
        ("data", event.data().to_object(py)),
        ("window_labels", event.window_labels().to_object(py)),
        ("time", event.time().to_object(py)),
        ("timing", event.channel_timing().to_object(py)),
        ("ecc_errors", event.ecc_errors().to_object(py)),
    ]
    .into_py_dict(py);
    Ok(dict.into())
}

// #[pyfunction]
// pub fn parse_py(event: &PyDict, py: Python) -> PyResult<PyObject> {
//     let rawdata: &PyBytes = event.get_item("rawdata").unwrap().downcast()?;

// }