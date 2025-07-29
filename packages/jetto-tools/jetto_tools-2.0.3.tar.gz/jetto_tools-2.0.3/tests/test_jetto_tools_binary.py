import os

import pytest

from jetto_tools.binary import *

jetto_binary_files = [
    'jetto.ex',
    'jetto.jse',
    'jetto.jsp',
    'jetto.jss',
    'jetto.jst',
]

sanco_binary_files = [
    'jetto.ssp',
    'jetto.ssp1',
    'jetto.sst',
    'jetto.sst1',
]

@pytest.fixture(scope='session')
def jetto_result_dir(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), 'testdata/jetto-sanco-pencil-esco-qlknn')

@pytest.mark.parametrize('test_file_name', jetto_binary_files + sanco_binary_files)
def test_read_binary(jetto_result_dir, test_file_name):
    read_file = read_binary_file(os.path.join(jetto_result_dir, test_file_name))
