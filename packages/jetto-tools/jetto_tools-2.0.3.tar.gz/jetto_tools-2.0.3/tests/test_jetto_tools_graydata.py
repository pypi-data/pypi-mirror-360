import pytest

from jetto_tools import graydata


# formatted to match serialisation output from code in graydata. if
# making these closer to fortran code, this obviously needs to change!
_GRAY_BEAM_LINE = (
    "NAME 1 2.0 3 4"
)
_GRAY_BEAMGRID_LINE = (
    "  1.0   2.0 3.0 4.0 5.0 6.0 7.0 8.0000000e+00 9.0000000e+00 10.0 11.0"
)

_GRAY_BEAM_FILE = """\
2
A1 1 180.0 1 1
B2 2 350.0 2 2

-10.0  10.0 2000.0 0.0 0.0 100.0 100.0 1.0000000e-06 1.0000000e-06 0.0 0.0

-20.0 -30.0 3000.0 0.0 0.0 200.0 200.0 1.0000000e-06 1.0000000e-06 0.0 0.0
 20.0 -30.0 3000.0 0.0 0.0 200.0 200.0 1.0000000e-06 1.0000000e-06 0.0 0.0
-20.0  30.0 3000.0 0.0 0.0 200.0 200.0 1.0000000e-06 1.0000000e-06 0.0 0.0
 20.0  30.0 3000.0 0.0 0.0 200.0 200.0 1.0000000e-06 1.0000000e-06 0.0 0.0
"""


class TestBeamDataHandling:
    def test_parse_beam(self):
        beam = graydata.GrayBeamData.parse(_GRAY_BEAM_LINE)

        assert beam.beamname == 'NAME'
        assert beam.iox == 1
        assert beam.fghz == 2.0
        assert beam.nalpha == 3
        assert beam.nbeta == 4

    def test_serialise_beam(self):
        beam = graydata.GrayBeamData(
            beamname='NAME',
            iox=1,
            fghz=2.,
            nalpha=3,
            nbeta=4,
        )
        assert beam.to_dataline() == _GRAY_BEAM_LINE

    def test_parse_beamgrid(self):
        grid = graydata.GrayBeamDataGrid.parse(_GRAY_BEAMGRID_LINE)

        assert grid.alpha == 1.0
        assert grid.beta == 2.0

        assert grid.x0 == 3.0
        assert grid.y0 == 4.0
        assert grid.z0 == 5.0

        assert grid.waist1 == 6.0
        assert grid.waist2 == 7.0

        assert grid.rci1 == 8.0
        assert grid.rci2 == 9.0

        assert grid.phi1 == 10.0
        assert grid.phi2 == 11.0

    def test_serialise_beamgrid(self):
        grid = graydata.GrayBeamDataGrid(
            alpha=1.0,
            beta=2.0,
            x0=3.0,
            y0=4.0,
            z0=5.0,
            waist1=6.0,
            waist2=7.0,
            rci1=8.0,
            rci2=9.0,
            phi1=10.0,
            phi2=11.0,
        )

        assert grid.to_dataline() == _GRAY_BEAMGRID_LINE

    def test_parse_graydata(self):
        beams = graydata.parse_graybeam_data(_GRAY_BEAM_FILE)

        assert len(beams) == 2
        assert beams[0].beamname == 'A1'
        assert len(beams[0].grid) == 1

        assert beams[1].beamname == 'B2'
        assert len(beams[1].grid) == 4

    def test_serialise_graydate(self):
        beams = graydata.parse_graybeam_data(_GRAY_BEAM_FILE)

        output = graydata.serialise_graybeam_data(beams)

        assert output == _GRAY_BEAM_FILE

    def test_graytemplate_read_write(self, tmp_path):
        src = tmp_path / 'graybeam.data'
        dst = tmp_path / 'graybeam2.data'

        with open(src, 'w') as fd:
            fd.write(_GRAY_BEAM_FILE)

        template = graydata.GrayTemplate.parse_file(src)

        template.export_to(dst)

        with open(dst) as fd:
            result = fd.read()

        assert result == _GRAY_BEAM_FILE

    def test_graytemplate_contains(self):
        orig = graydata.GrayTemplate(
            graydata.parse_graybeam_data(_GRAY_BEAM_FILE),
        )

        assert 'A1.fghz' in orig
        assert 'B2.fghz' in orig
        assert 'B2[2].waist1' in orig
        assert 'B2[3].phi2' in orig

        assert 'INVALID.fghz' not in orig
        assert 'A1[0].alpha' not in orig
        assert 'B2[1].invalid_attr' not in orig

    def test_graytemplate_withparams_success(self):
        orig = graydata.GrayTemplate(
            graydata.parse_graybeam_data(_GRAY_BEAM_FILE),
        )

        changed = orig.with_params({
            'A1.fghz': 101.0,
            'B2.fghz': 102.0,
            'B2[1].alpha': 103.0,
            'B2[4].beta': 104.0,
        })

        assert changed.beams['A1'].fghz == 101.0
        assert changed.beams['B2'].fghz == 102.0
        assert changed.beams['B2'].grid[0].alpha == 103.0
        assert changed.beams['B2'].grid[3].beta == 104.0

    def test_graytemplate_withparams_failures(self):
        orig = graydata.GrayTemplate(
            graydata.parse_graybeam_data(_GRAY_BEAM_FILE),
        )

        with pytest.raises(KeyError):
            orig.with_params({
                'INVALID.fghz': 42.0,
            })

        with pytest.raises(KeyError):
            orig.with_params({
                'B2.invalid_attr': 42.0,
            })

        with pytest.raises(IndexError):
            orig.with_params({
                'B2[0].alpha': 42.0,
            })

        with pytest.raises(IndexError):
            orig.with_params({
                'B2[5].alpha': 42.0,
            })

        with pytest.raises(KeyError):
            orig.with_params({
                'B2[1].invalid_attr': 42.0,
            })
