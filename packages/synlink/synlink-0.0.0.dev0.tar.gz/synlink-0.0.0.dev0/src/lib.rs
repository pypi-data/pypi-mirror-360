use pyo3::prelude::*;

mod error;
use error::register_exception;

/// A Python module implemented in Rust.
#[pymodule]
fn _synlink_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // register exception submodule
    register_exception(m)?;

    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
