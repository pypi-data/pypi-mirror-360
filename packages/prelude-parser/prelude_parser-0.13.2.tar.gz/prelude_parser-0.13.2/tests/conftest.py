from pathlib import Path

import pytest

ASSETS_PATH = Path().absolute() / "tests/assets"


@pytest.fixture
def test_file_1():
    return ASSETS_PATH / "test1.xml"


@pytest.fixture
def test_file_2():
    return ASSETS_PATH / "test2.xml"


@pytest.fixture
def test_file_3():
    return ASSETS_PATH / "test3.xml"


@pytest.fixture
def test_file_4():
    return ASSETS_PATH / "test4.xml"


@pytest.fixture
def site_native_xml():
    return ASSETS_PATH / "site_native.xml"


@pytest.fixture
def site_native_small_xml():
    return ASSETS_PATH / "site_native_small.xml"


@pytest.fixture
def subject_native_xml():
    return ASSETS_PATH / "subject_native.xml"


@pytest.fixture
def subject_native_small_xml():
    return ASSETS_PATH / "subject_native_small.xml"


@pytest.fixture
def user_native_xml():
    return ASSETS_PATH / "user_native.xml"


@pytest.fixture
def user_native_small_xml():
    return ASSETS_PATH / "user_native_small.xml"
