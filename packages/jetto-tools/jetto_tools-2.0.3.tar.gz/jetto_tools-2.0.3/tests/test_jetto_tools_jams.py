import os

import pytest

omas = pytest.importorskip("omas")
from jetto_tools.jams import *

@pytest.fixture(scope='session')
def jetto_result_dir(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), 'testdata/jetto-sanco-pencil-esco-qlknn')

@pytest.mark.skip(reason="broken venv in CI")
def test_read_in(jetto_result_dir):
    ods = Settings.read(os.path.join(jetto_result_dir, 'jetto.jset'))
    assert ods['AppPanel']['catCodeID'] == 'jetto'
