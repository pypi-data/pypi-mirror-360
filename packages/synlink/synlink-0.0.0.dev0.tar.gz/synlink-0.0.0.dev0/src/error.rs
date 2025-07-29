use pyo3::exceptions::PyException;
use pyo3::prelude::*;

pyo3::create_exception!(
    synlink,
    SynLinkBaseException,
    PyException,
    "Custom Base exception on the SL protocol"
);

/// A Python module implemented in Rust.
#[pymodule]
pub(crate) fn register_exception(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let error_m = PyModule::new(m.py(), "_error")?;
    error_m.add(
        "SynLinkBaseException",
        error_m.py().get_type::<SynLinkBaseException>(),
    )?;

    m.add_submodule(&error_m)
}
