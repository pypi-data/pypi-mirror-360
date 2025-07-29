import pytest
from pathlib import Path
import tempfile

netCDF4 = pytest.importorskip("netCDF4")

from jetto_tools import transp

@pytest.mark.freia
def test_common_explicit_load(tmpdir):
    cdf_path = '/common/projects/physics/omfit/data/TRANSP/result/MAST/29782/S07/29782S07.CDF'
    with tmpdir.as_cwd():
        ierr = transp.convert_cdf_to_exfile('DUMMY', 99999, inpath=cdf_path)
        assert ierr == 0
        cdf_path = Path(cdf_path)
        basename = cdf_path.name[:-len(cdf_path.suffix)]
        exfile = Path(basename + '.ex')
        extfile = Path(basename + '.ext')
        assert exfile.is_file()
        assert extfile.is_file()

def test_convert_jsp_jst_to_netcdf(datadir: Path, tmpdir):
    '''
    Test conversion script for writing JETTO profiles (JSP)
    and timetraces (JST) output to TRANSP style netCDF4 file.
    '''
    run_dir = datadir.joinpath('jetto-sanco-pencil-esco-qlknn')
    jsp_file = run_dir.joinpath("jetto.jsp")
    jst_file = run_dir.joinpath("jetto.jst")

    with tempfile.TemporaryDirectory() as tmpdir:
        ierr = transp.convert_jsp_jst_to_netcdf(None, None, None,
            jsp_file, jst_file, output_directory=tmpdir, legacy=True)
        
    assert ierr == 0

    with tempfile.TemporaryDirectory() as tmpdir:
        ierr = transp.convert_jsp_jst_to_netcdf(None, None, None,
            jsp_file, jst_file, output_directory=tmpdir, legacy=False)
        
    assert ierr == 0
