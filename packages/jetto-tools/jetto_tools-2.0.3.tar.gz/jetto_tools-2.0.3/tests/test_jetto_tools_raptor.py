import os

import pytest

from jetto_tools.matlab import loadmat
from jetto_tools.classes import OODS
from jetto_tools.raptor import *  # noqa: F403 Import everything as a test


@pytest.fixture(scope='session')
def raptor_out_dir(pytestconfig):
    return pytestconfig.rootdir / 'testdata/raptor-out'


@pytest.fixture(scope='session')
def raptor_out_path(raptor_out_dir):
    raptor_out_name = 'ITERinductive_RAPTORdyn_QLKNN_fromJETTOprofs_01.mat'
    return raptor_out_dir / raptor_out_name


@pytest.fixture
def raptor_ds(raptor_out_path):
    raptor_out_raw = loadmat(raptor_out_path)
    ods = OODS(raptor_out_raw)
    subname = 'out'
    ds = deconstruct_raptor_out(ods, subname, on_read_error='warn')
    return ds


def test_check_raptor_sanity(raptor_ds):
    # We start with a sane raptor run
    assert check_raptor_sanity(raptor_ds)

    # Create negative temperature
    te = raptor_ds['te']
    te[0, 0] = -1
    assert not check_raptor_sanity(raptor_ds)


def test_extrapolate_raptor_out(raptor_ds):
    ds = extrapolate_raptor_out(raptor_ds)
    assert min(ds['rho']) == 0
    assert max(ds['rho']) == 1
