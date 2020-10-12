import pytest


@pytest.fixture(scope='session')
def tmp_dir(tmpdir_factory):
    tmpdir_factory.mktemp('data')
