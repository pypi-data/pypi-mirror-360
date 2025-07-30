mod errors;
mod utils;

use std::collections::HashMap;
use std::fs::read_to_string;
use std::path::PathBuf;

use chrono::{Datelike, NaiveDate};
pub use prelude_xml_parser::native::{
    site_native::SiteNative, subject_native::SubjectNative, user_native::UserNative,
};
use prelude_xml_parser::parse_site_native_file as parse_site_native_file_rs;
use prelude_xml_parser::parse_site_native_string as parse_site_native_string_rs;
use prelude_xml_parser::parse_subject_native_file as parse_subject_native_file_rs;
use prelude_xml_parser::parse_subject_native_string as parse_subject_native_string_rs;
use prelude_xml_parser::parse_user_native_file as parse_user_native_file_rs;
use prelude_xml_parser::parse_user_native_string as parse_user_native_string_rs;
use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyDict, PyList};
use roxmltree::Document;

use crate::errors::{
    FileNotFoundError, InvalidFileTypeError, ParsingError, XmlFileValidationError,
};
use crate::utils::{to_snake, validate_file};

fn check_valid_file(xml_file: &PathBuf) -> PyResult<()> {
    if let Err(e) = validate_file(xml_file) {
        match e {
            XmlFileValidationError::FileNotFound(_) => {
                return Err(FileNotFoundError::new_err(format!(
                    "File not found: {xml_file:?}"
                )))
            }
            XmlFileValidationError::InvalidFileType(_) => {
                return Err(InvalidFileTypeError::new_err(format!(
                    "{xml_file:?} is not an xml file"
                )))
            }
        };
    };

    Ok(())
}

fn py_list_append<'py>(
    py: Python<'py>,
    value: Option<&str>,
    list: &'py Bound<'py, PyList>,
) -> PyResult<&'py Bound<'py, PyList>> {
    let datetime = py.import("datetime")?;
    let date = datetime.getattr("date")?;

    match value {
        Some(t) => match t.parse::<usize>() {
            Ok(int_val) => list.append(int_val)?,
            Err(_) => match t.parse::<f64>() {
                Ok(float_val) => list.append(float_val)?,
                Err(_) => match NaiveDate::parse_from_str(t, "%d-%b-%Y") {
                    Ok(dt) => {
                        let py_date = date.call1((dt.year(), dt.month(), dt.day()))?;
                        list.append(py_date)?;
                    }
                    Err(_) => list.append(t)?,
                },
            },
        },
        None => list.append(py.None())?,
    };

    Ok(list)
}

fn add_item<'py>(
    py: Python<'py>,
    key: &str,
    value: Option<&str>,
    form_data: &'py Bound<'py, PyDict>,
) -> PyResult<&'py Bound<'py, PyDict>> {
    let datetime = py.import("datetime")?;
    let date = datetime.getattr("date")?;

    match value {
        Some(t) => match t.parse::<usize>() {
            Ok(int_val) => form_data.set_item(key, int_val)?,
            Err(_) => match t.parse::<f64>() {
                Ok(float_val) => form_data.set_item(key, float_val)?,
                Err(_) => match NaiveDate::parse_from_str(t, "%d-%b-%Y") {
                    Ok(dt) => {
                        let py_date = date.call1((dt.year(), dt.month(), dt.day()))?;
                        form_data.set_item(key, py_date)?;
                    }
                    Err(_) => form_data.set_item(key, t)?,
                },
            },
        },
        None => form_data.set_item(key, py.None())?,
    };

    Ok(form_data)
}

fn parse_xml<'py>(
    py: Python<'py>,
    xml_file: &PathBuf,
    short_names: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let reader = read_to_string(xml_file);

    match reader {
        Ok(r) => match Document::parse(&r) {
            Ok(doc) => {
                let mut data: HashMap<String, Vec<Bound<'_, PyDict>>> = HashMap::new();
                let tree = doc.root_element();
                for form in tree.children() {
                    let form_name = if short_names {
                        form.tag_name().name().to_owned().to_lowercase()
                    } else {
                        to_snake(form.tag_name().name())
                    };
                    if !form_name.is_empty() {
                        if let Some(d) = data.get_mut(&form_name) {
                            let form_data = PyDict::new(py);
                            for child in form.children() {
                                if child.is_element() && child.tag_name().name() != "" {
                                    let key = if short_names {
                                        child.tag_name().name().to_owned().to_lowercase()
                                    } else {
                                        to_snake(child.tag_name().name())
                                    };
                                    add_item(py, &key, child.text(), &form_data)?;
                                };
                            }
                            d.push(form_data);
                        } else {
                            let mut items: Vec<Bound<'_, PyDict>> = Vec::new();
                            let form_data = PyDict::new(py);
                            for child in form.children() {
                                if child.is_element() && child.tag_name().name() != "" {
                                    let key = if short_names {
                                        child.tag_name().name().to_owned().to_lowercase()
                                    } else {
                                        to_snake(child.tag_name().name())
                                    };
                                    add_item(py, &key, child.text(), &form_data)?;
                                }
                            }
                            items.push(form_data.into_py_dict(py)?);
                            data.insert(form_name, items);
                        }
                    }
                }
                let data_dict = data.into_py_dict(py)?;
                Ok(data_dict)
            }
            Err(e) => Err(ParsingError::new_err(format!(
                "Error parsing xml file: {e:?}"
            ))),
        },
        Err(e) => Err(ParsingError::new_err(format!(
            "Error parsing xml file: {e:?}"
        ))),
    }
}

fn parse_xml_pandas<'py>(
    py: Python<'py>,
    xml_file: &PathBuf,
    short_names: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let reader = read_to_string(xml_file);

    match reader {
        Ok(r) => match Document::parse(&r) {
            Ok(doc) => {
                let data = PyDict::new(py);
                let tree = doc.root_element();

                for form in tree.children() {
                    for child in form.children() {
                        if child.is_element() && child.tag_name().name() != "" {
                            let column = if short_names {
                                child.tag_name().name().to_owned().to_lowercase()
                            } else {
                                to_snake(child.tag_name().name())
                            };
                            if let Ok(Some(c)) = data.get_item(&column) {
                                py_list_append(py, child.text(), &c.extract()?)?;
                                data.set_item(column, c)?;
                            } else {
                                let list = PyList::empty(py);
                                py_list_append(py, child.text(), &list)?;
                                data.set_item(column, list)?;
                            }
                        }
                    }
                }
                let data_dict = data.into_py_dict(py)?;
                Ok(data_dict)
            }
            Err(e) => Err(ParsingError::new_err(format!(
                "Error parsing xml file: {e:?}"
            ))),
        },
        Err(e) => Err(ParsingError::new_err(format!(
            "Error parsing xml file: {e:?}"
        ))),
    }
}

#[pyfunction]
#[pyo3(signature = (xml_file, *, short_names=false))]
fn _parse_flat_file_to_dict(
    py: Python,
    xml_file: PathBuf,
    short_names: bool,
) -> PyResult<Bound<'_, PyDict>> {
    check_valid_file(&xml_file)?;
    let data = parse_xml(py, &xml_file, short_names)?;

    Ok(data)
}

#[pyfunction]
#[pyo3(signature = (xml_file, *, short_names=false))]
fn _parse_flat_file_to_pandas_dict(
    py: Python,
    xml_file: PathBuf,
    short_names: bool,
) -> PyResult<Bound<'_, PyDict>> {
    check_valid_file(&xml_file)?;
    let data = parse_xml_pandas(py, &xml_file, short_names)?;

    Ok(data)
}

#[pyfunction]
#[pyo3(signature = (xml_file))]
fn parse_site_native_file(_py: Python, xml_file: PathBuf) -> PyResult<SiteNative> {
    match parse_site_native_file_rs(&xml_file) {
        Ok(native) => Ok(native),
        Err(e) => Err(ParsingError::new_err(format!(
            "Error parsing xml file: {e:?}"
        ))),
    }
}

#[pyfunction]
#[pyo3(signature = (xml_str))]
fn parse_site_native_string(_py: Python, xml_str: &str) -> PyResult<SiteNative> {
    match parse_site_native_string_rs(xml_str) {
        Ok(native) => Ok(native),
        Err(e) => Err(ParsingError::new_err(format!("Error parsing xml: {e:?}"))),
    }
}

#[pyfunction]
#[pyo3(signature = (xml_file))]
fn parse_subject_native_file(_py: Python, xml_file: PathBuf) -> PyResult<SubjectNative> {
    match parse_subject_native_file_rs(&xml_file) {
        Ok(native) => Ok(native),
        Err(e) => Err(ParsingError::new_err(format!(
            "Error parsing xml file: {e:?}"
        ))),
    }
}

#[pyfunction]
#[pyo3(signature = (xml_str))]
fn parse_subject_native_string(_py: Python, xml_str: &str) -> PyResult<SubjectNative> {
    match parse_subject_native_string_rs(xml_str) {
        Ok(native) => Ok(native),
        Err(e) => Err(ParsingError::new_err(format!("Error parsing xml: {e:?}"))),
    }
}

#[pyfunction]
#[pyo3(signature = (xml_file))]
fn parse_user_native_file(_py: Python, xml_file: PathBuf) -> PyResult<UserNative> {
    match parse_user_native_file_rs(&xml_file) {
        Ok(native) => Ok(native),
        Err(e) => Err(ParsingError::new_err(format!(
            "Error parsing xml file: {e:?}"
        ))),
    }
}

#[pyfunction]
#[pyo3(signature = (xml_str))]
fn parse_user_native_string(_py: Python, xml_str: &str) -> PyResult<UserNative> {
    match parse_user_native_string_rs(xml_str) {
        Ok(native) => Ok(native),
        Err(e) => Err(ParsingError::new_err(format!("Error parsing xml: {e:?}"))),
    }
}

#[pymodule]
fn _prelude_parser(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SiteNative>()?;
    m.add_class::<SubjectNative>()?;
    m.add_class::<UserNative>()?;
    m.add_function(wrap_pyfunction!(_parse_flat_file_to_dict, m)?)?;
    m.add_function(wrap_pyfunction!(_parse_flat_file_to_pandas_dict, m)?)?;
    m.add_function(wrap_pyfunction!(parse_site_native_file, m)?)?;
    m.add_function(wrap_pyfunction!(parse_site_native_string, m)?)?;
    m.add_function(wrap_pyfunction!(parse_subject_native_file, m)?)?;
    m.add_function(wrap_pyfunction!(parse_subject_native_string, m)?)?;
    m.add_function(wrap_pyfunction!(parse_user_native_file, m)?)?;
    m.add_function(wrap_pyfunction!(parse_user_native_string, m)?)?;
    m.add("FileNotFoundError", py.get_type::<FileNotFoundError>())?;
    m.add(
        "InvalidFileTypeError",
        py.get_type::<InvalidFileTypeError>(),
    )?;
    m.add("ParsingError", py.get_type::<ParsingError>())?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_to_snake() {
        assert_eq!(
            to_snake("i_communications_Details"),
            String::from("i_communications_details")
        );
    }
}
