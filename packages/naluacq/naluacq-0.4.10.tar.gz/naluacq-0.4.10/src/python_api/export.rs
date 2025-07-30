use std::path::PathBuf;

use pyo3::{pyfunction, Py, PyResult, Python};

use crate::{
    acquisition::MiscDataKind, calibration::Corrections, export::export_csv_from_acq, Acquisition,
    Pedestals,
};

use super::acquisition::PyAcquisition;

const EVENTS_PER_CHUNK: usize = 1000;

#[pyfunction]
pub fn export_csv(
    acq: Py<PyAcquisition>,
    indices: Vec<usize>,
    out_dir: PathBuf,
    pedestals_correction: bool,
    py: Python,
) -> PyResult<()> {
    let acq = acq.borrow(py).inner.clone();

    // `allow_threads()` is needed since this is an expensive operations and we want
    // to release the GIL to allow other Python threads to make progress
    py.allow_threads(|| {
        let params = acq.metadata()?.params().clone();
        let pedestals = if pedestals_correction {
            extract_pedestals(&acq)
        } else {
            None
        };

        let corrections = Corrections::new(params.clone()).pedestals(pedestals);
        export_csv_from_acq(acq, &indices, corrections, out_dir, EVENTS_PER_CHUNK)?;
        Ok(())
    })
}

fn extract_pedestals(acq: &Acquisition) -> Option<Pedestals> {
    let peds = acq.misc_data(MiscDataKind::PedestalsCalibration).ok()?;
    Pedestals::from_bytes(&peds.data).ok()
}
