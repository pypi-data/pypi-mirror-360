use std::path::PathBuf;

use crate::errors::XmlFileValidationError;

pub fn to_snake(camel_string: &str) -> String {
    let mut snake_string = String::with_capacity(
        camel_string.len() + camel_string.chars().filter(|c| c.is_uppercase()).count(),
    );

    let mut chars = camel_string.chars().peekable();
    while let Some(c) = chars.next() {
        snake_string.push(c);
        if let Some(next) = chars.peek() {
            if next.is_uppercase() && c != '_' {
                snake_string.push('_');
            }
        }
    }

    snake_string.to_lowercase()
}

pub fn validate_file(xml_file: &PathBuf) -> Result<(), XmlFileValidationError> {
    if !xml_file.is_file() {
        return Err(XmlFileValidationError::FileNotFound(xml_file.to_owned()));
    } else if xml_file.extension().unwrap() != "xml" {
        return Err(XmlFileValidationError::InvalidFileType(xml_file.to_owned()));
    }

    Ok(())
}
