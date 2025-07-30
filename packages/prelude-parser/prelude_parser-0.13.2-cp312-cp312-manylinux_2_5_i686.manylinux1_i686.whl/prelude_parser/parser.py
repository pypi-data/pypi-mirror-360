from __future__ import annotations

from pathlib import Path
from typing import Any

from camel_converter import to_pascal

from prelude_parser._prelude_parser import _parse_flat_file_to_dict
from prelude_parser.types import FieldInfo, FlatFormInfo


class _MetaCls(type):
    def __new__(
        cls, clsname: str, superclasses: tuple[type, ...], attributedict: dict[str, FieldInfo]
    ) -> _MetaCls:
        return super().__new__(cls, clsname, superclasses, attributedict)


def parse_to_dict(xml_file: str | Path, *, short_names: bool = False) -> dict[str, FlatFormInfo]:
    """Parse a Prelude flat XML file into a dict.

    Args:
        xml_file: The path to the XML file to parser.
        short_names: Set to True if short names were used in the export.

    Returns:
        A Python dictionary containing the data from the XML file.

    Examples:
        >>> from prelude_parser import parse_to_dict
        >>> data = parse_to_dict("physical_examination.xml")
    """
    return _parse_flat_file_to_dict(xml_file, short_names=short_names)


def parse_to_classes(xml_file: str | Path, short_names: bool = False) -> list[Any]:
    """Parse a Prelude flat XML file into a list of Python class.

    The name of the class is taken from the form name node in the XML file converted to pascal case.
    For example a <physical_examination> node will result in a PhysicalExamination class being
    created.

    Args:
        xml_file: The path to the XML file to parser.
        short_names: Set to True if short names were used in the export.

    Returns:
        A list of Python classes containing the data from the XML file.

    Examples:
        >>> from prelude_parser import parse_to_classes
        >>> data = parse_to_classes("physical_examination.xml")
    """
    parsed = parse_to_dict(xml_file, short_names=short_names)
    formatted: list[Any] = []
    for form, data in parsed.items():
        class_name = to_pascal(form)
        for d in data:
            formatted.append(_MetaCls(class_name, (object,), d))

    return formatted
