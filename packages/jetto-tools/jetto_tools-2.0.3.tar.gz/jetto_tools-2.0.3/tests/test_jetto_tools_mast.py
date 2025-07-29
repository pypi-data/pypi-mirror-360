import pytest
import copy

from IPython import embed  # noqa: F401 For debugging

pyuda = pytest.importorskip("pyuda")

from jetto_tools.mast_jetto_tools import *  # noqa: F403 Import everything as a test
from jetto_tools.mast_jetto_tools import MastJetto

def test_mast_jetto():
    #File exists only Freia and duplicated on Heimdall
    file = '/home/fcasson/testdata/lgarzot/cmg/catalog/jetto/mast/26887/mar2020/seq#1/'

    shot = 26887
    time = 0.25

    # Test initializing.
    # As file is not None, load the JETTO file
    # As shot is not None, load the shot file
    data = MastJetto(shot=shot,time=time,file=file)
