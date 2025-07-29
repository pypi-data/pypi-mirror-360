from pathlib import Path
import numpy as np

from jetto_tools.output_to_input import convert, convert_and_write
from jetto_tools.binary import read_binary_file

def test_jsp2ex_dictionary(datadir):

    jsp_path = str(datadir / 'jetto-sanco-pencil-esco-qlknn')
    exfile_path = jsp_path

    jsp = read_binary_file(jsp_path + '/jetto.jsp')
    exfile_new_dict, extfile_new_dict = convert(jsp_path, verbosity=0)
    # Check some selected profiles at end times as that what the EXFILE is made off
    test_key = ['TE','TI','NE']
    jsp_exfile_test = {key:jsp[key][-1] for key in test_key}
    exfile_test = {key:exfile_new_dict[key] for key in test_key}

    # note the [] brackets around jsp, is becuase the shape of the arrays is strange from read_binary_file
    for key in test_key:
        np.testing.assert_array_equal([jsp_exfile_test[key]], exfile_test[key])



def test_jsp2ex_write(datadir, tmpdir):
    jsp_path = str(datadir / 'jetto-sanco-pencil-esco-qlknn')
    exfile_path = jsp_path
    test_path = Path(__file__).resolve().parent
    with tmpdir.as_cwd():
        name_ex_file = 'jetto_test.ex'
        status = convert_and_write(str(tmpdir), name_ex_file, jsp_path, verbosity=0)
        assert(Path(tmpdir / name_ex_file).is_file())
        # DEBUG ONLY
        # from IPython import embed
        # embed()
