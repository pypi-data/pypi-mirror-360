use pyo3::{Python, types::PyModule, PyResult, wrap_pyfunction, pymodule};


use self::acquisition::{PyAcquisition, list_acquisitions, is_acquisition};


mod acquisition;
mod parsing;
mod exceptions;
mod python_libs;
mod export;
mod upac_ecc;


/// Register PyO3 bindings to naluacquisition.
#[pymodule]
fn naluacq(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyAcquisition>()?;
    m.add_function(wrap_pyfunction!(list_acquisitions, m)?)?;
    m.add_function(wrap_pyfunction!(is_acquisition, m)?)?;
    m.add_function(wrap_pyfunction!(export::export_csv, m)?)?;
    m.add_function(wrap_pyfunction!(upac_ecc::syndrome, m)?)?;
    m.add_function(wrap_pyfunction!(upac_ecc::global_parity, m)?)?;
    m.add_function(wrap_pyfunction!(upac_ecc::syndrome_to_index, m)?)?;
    m.add_function(wrap_pyfunction!(upac_ecc::ecc_check, m)?)?;
    m.add_function(wrap_pyfunction!(upac_ecc::ecc_correct, m)?)?;
    Ok(())
}
