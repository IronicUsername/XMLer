import os

import pytest

from xmler.config import CONFIG


@pytest.fixture(scope='session')
def base_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


@pytest.fixture(scope='session')
def test_data_path(base_path):
    return os.path.join(base_path, 'tests', 'data')


@pytest.fixture(scope='session')
def default_conf():
    return CONFIG
