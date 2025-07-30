use passrs;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyfunction]
fn show(name: String) -> PyResult<String> {
    match passrs::password::show(name, false, false) {
        Ok(r) => match r {
            Some(p) => Ok(p),
            None => Err(PyValueError::new_err("Failed to get password")),
        },
        Err(e) => Err(PyValueError::new_err(e.to_string()))
    }
}

#[pyfunction]
#[pyo3(signature = (path=None, name=None))]
fn init(path: Option<String>, name: Option<String>) -> PyResult<bool> {
    match passrs::directory::init(path, name) {
        Ok(_) => Ok(true),
        Err(e) => Err(PyValueError::new_err(e.to_string())),
    }
}

#[pyfunction]
fn edit(path: String, password: String) -> PyResult<bool> {
    match passrs::password::edit(path.to_owned(), password.to_owned()) {
        Ok(_) => Ok(true),
        Err(e) => Err(PyValueError::new_err(e.to_string()))
    }
}

#[pyfunction]
fn mv(src: String, dest: String, force: bool, remove: bool) -> PyResult<bool> {
    match passrs::password::mv(src.to_owned(), dest.to_owned(), force, remove) {
        Ok(_) => Ok(true),
        Err(e) => Err(PyValueError::new_err(e.to_string()))
    }
}

#[pyfunction]
fn insert(path: String, password: String, force: bool) -> PyResult<bool> {
    match passrs::password::insert(path.to_owned(), force, password.to_owned()) {
        Ok(_) => Ok(true),
        Err(e) => Err(PyValueError::new_err(e.to_string()))
    }
}

#[pyfunction]
#[pyo3(signature = (path=None, query=None))]
fn tree(path: Option<String>, query: Option<Vec<String>>) -> PyResult<String> {
    match passrs::directory::show_tree(path, query) {
        Ok(t) => Ok(t),
        Err(e) => Err(PyValueError::new_err(e.to_string()))
    }
}

#[pyfunction]
#[pyo3(signature = (symbols, qr, force, length, path=None))]
fn generate(symbols: bool, qr: bool, force: bool, length: usize, path: Option<String>) -> PyResult<Option<String>> {
    match passrs::password::generate(path.to_owned(), symbols, false, qr, force, length) {
        Ok(r) => match r {
            Some(p) => Ok(Some(p)),
            None => match path {
                Some(_) => Ok(None),
                None => Err(PyValueError::new_err("Failed to generate password"))
            }
        },
        Err(e) => Err(PyValueError::new_err(e.to_string()))
    }
}

#[pyfunction]
fn rm(path: String, recursive: bool) -> PyResult<bool> {
    match passrs::password::rm(path.to_owned(), recursive) {
        Ok(_) => Ok(true),
        Err(e) => Err(PyValueError::new_err(e.to_string()))
    }
}

#[pymodule]
fn pypassrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(show, m)?)?;
    m.add_function(wrap_pyfunction!(init, m)?)?;
    m.add_function(wrap_pyfunction!(edit, m)?)?;
    m.add_function(wrap_pyfunction!(mv, m)?)?;
    m.add_function(wrap_pyfunction!(insert, m)?)?;
    m.add_function(wrap_pyfunction!(tree, m)?)?;
    m.add_function(wrap_pyfunction!(generate, m)?)?;
    m.add_function(wrap_pyfunction!(rm, m)?)?;
    Ok(())
}