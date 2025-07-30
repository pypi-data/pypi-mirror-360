use std::path::PathBuf;

use pyo3::create_exception;
use pyo3::exceptions::PyException;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum XmlFileValidationError {
    #[error("File not found: {0:?}")]
    FileNotFound(PathBuf),

    #[error("{0:?} is not an xml file")]
    InvalidFileType(PathBuf),
}

create_exception!(_prelude_parser, FileNotFoundError, PyException);
create_exception!(_prelude_parser, InvalidFileTypeError, PyException);
create_exception!(_prelude_parser, ParsingError, PyException);
