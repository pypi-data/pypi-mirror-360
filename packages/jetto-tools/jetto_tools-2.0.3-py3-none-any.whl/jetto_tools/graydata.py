"""Code for handling GRAY data files."""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Iterator, Iterable

import dataclasses
from pathlib import Path
import re

# GrayBeamData parameters accessible to Scans
_BEAM_PARAMS = {
    'fghz',
    'iox',
}

# GrayBeamDataGrid parameters accessible to Scans
_GRID_PARAMS = {
    'alpha', 'beta',
    'x0', 'y0', 'z0',
    'waist1', 'waist2',
    'rci1', 'rci2',
    'phi1', 'phi2',
}


@dataclasses.dataclass(frozen=True)
class GrayBeamDataGrid:
    """Contains a row of a beam's data grid.

    Parameter names and types come from Fortran code, i.e. read_beam2
    in gray/beams.f90.
    """

    alpha: float
    beta: float
    x0: float
    y0: float
    z0: float
    # minimum size of beam
    waist1: float  # x-axis
    waist2: float  # y-axis
    # radius?  approaches planar wave front as number approaches zero, e.g. 1e-6
    rci1: float
    rci2: float
    # phase
    phi1: float
    phi2: float

    @classmethod
    def parse(cls, line: str) -> GrayBeamDataGrid:
        """Parse a line from the graybeam.data file."""
        lst = line.split(maxsplit=11)
        return cls(
            alpha=float(lst[0]),
            beta=float(lst[1]),
            x0=float(lst[2]),
            y0=float(lst[3]),
            z0=float(lst[4]),
            waist1=float(lst[5]),
            waist2=float(lst[6]),
            rci1=float(lst[7]),
            rci2=float(lst[8]),
            phi1=float(lst[9]),
            phi2=float(lst[10]),
        )

    def to_dataline(self) -> str:
        """Convert values to a string for writing to graybeam.data file."""
        return (
            f'{self.alpha:5} {self.beta:5} '
            f'{self.x0} {self.y0} {self.z0} '
            f'{self.waist1} {self.waist2} '
            f'{self.rci1:.7e} {self.rci2:.7e} '
            f'{self.phi1} {self.phi2}'
        )


@dataclasses.dataclass(frozen=True)
class GrayBeamData:
    """Contains a row of a beam's data.

    Parameter names and types come from Fortran code, i.e. read_beam2
    in gray/beams.f90.
    """

    beamname: str
    iox: int
    fghz: float
    nalpha: int
    nbeta: int

    grid: List[GrayBeamDataGrid] = dataclasses.field(default_factory=list)

    @classmethod
    def parse(cls, line: str) -> GrayBeamData:
        """Parse a line from the graybeam.data file."""
        lst = line.split(maxsplit=5)
        return cls(
            beamname=lst[0],
            iox=int(lst[1]),
            fghz=float(lst[2]),
            nalpha=int(lst[3]),
            nbeta=int(lst[4]),
        )

    def to_dataline(self) -> str:
        """Convert values to a string for writing to graybeam.data file."""
        return (
            f'{self.beamname} {self.iox} {self.fghz} '
            f'{self.nalpha} {self.nbeta}'
        )


def _iter_lines(data: str) -> Iterator[str]:
    """Iterate over non-blank lines."""
    for line in data.splitlines():
        line = line.strip()
        if line:
            yield line


def parse_graybeam_data(data: str) -> List[GrayBeamData]:
    """Parse the contents of a graybeam.data file.

    Returns a list of GrayBeamData objects as defined in the file.
    """
    lines = _iter_lines(data)
    nbeams = int(next(lines))

    beams: List[GrayBeamData] = []
    for _ in range(nbeams):
        beams.append(
            GrayBeamData.parse(next(lines))
        )

    for beam in beams:
        ngrid = beam.nalpha * beam.nbeta
        for _ in range(ngrid):
            beam.grid.append(
                GrayBeamDataGrid.parse(next(lines))
            )

    for line in lines:
        raise ValueError('expecting end of file, but got', line)

    return beams


def serialise_graybeam_data(beams: Iterable[GrayBeamData]) -> str:
    """Convert data to format used by graybeam.data files.

    Raises ValueError if the number of grid entries doesn't match the
    beam's (nalpha * nbeta).
    """
    result = [
        f'{len(beams)}'
    ]

    for beam in beams:
        result.append(beam.to_dataline())

    for beam in beams:
        # seperate the grid entries between beams nicely
        result.append('')

        if beam.nalpha * beam.nbeta != len(beam.grid):
            raise ValueError('beam should have (nalpha * nbeta) grid entries')

        for grid in beam.grid:
            result.append(grid.to_dataline())

    # end the file with a trailing new line
    result.append('')

    return '\n'.join(result)


class GrayTemplate:
    # dicts are ordered by insertion order
    beams: Dict[str, GrayBeamData]

    @classmethod
    def parse_file(cls, graybeam: Path) -> GrayTemplate:
        """Read and parse the contents of the specified file."""
        with open(graybeam) as fd:
            contents = fd.read()

        return cls(parse_graybeam_data(contents))

    def __init__(self, beams: Iterable[GrayBeamData]):
        """Create object with the specified beam data."""
        self.beams = {
            beam.beamname: beam for beam in beams
        }

    def _with_param(self, param: str, value: float) -> GrayTemplate:
        """Copy this GrayTemplate with the specified parameter changed."""
        m = re.match(r'^([^ ,.[]+)', param, re.IGNORECASE)

        if not m:
            raise KeyError(param)

        beamname = m.group(1)
        tail = param[m.end():]

        beams = self.beams.copy()
        beam = beams[beamname]

        changes = {}

        # assignment statements would be nice here!
        m1 = re.match(r'^\.([a-z0-9]+)$', tail, re.IGNORECASE)
        m2 = re.match(r'^\[([0-9]+)\]\.([a-z0-9]+)$', tail, re.IGNORECASE)

        if m1:
            name = m1.group(1)
            if name not in _BEAM_PARAMS:
                raise KeyError(name)

            changes[name] = value
        elif m2:
            idx = int(m2.group(1))
            name = m2.group(2)
            if name not in _GRID_PARAMS:
                raise KeyError(name)

            if not 0 < idx <= len(beam.grid):
                raise IndexError("invalid beam grid", idx)

            grid = beam.grid.copy()
            grid[idx-1] = dataclasses.replace(grid[idx-1], **{
                name: value
            })

            changes['grid'] = grid
        else:
            raise KeyError(tail)

        beams[beamname] = dataclasses.replace(beam, **changes)
        return GrayTemplate(beams.values())

    def with_params(self, params: Dict[str, float]) -> GrayTemplate:
        """Return a copy with the specified beams modified.

        Raises KeyError if the parameter is not of the correct form or
        one of the names can't be found, or IndexError if the index
        isn't valid for the file. Both are subclasses of LookupError.
        """
        result = self

        # TODO: optimize! the below functions create a lot of garbage.
        # this doesn't seem to be a priority as at most a couple of
        # attributes are going to get set per point
        for param, value in params.items():
            result = result._with_param(param, value)

        return result

    def serialise_graybeam_data(self) -> str:
        """Serialise GRAY beam data to a string."""
        return serialise_graybeam_data(self.beams.values())

    def export_to(self, path: Path):
        """Export GRAY beam data to the specified file."""
        contents = self.serialise_graybeam_data()
        with open(path, 'w') as fd:
            fd.write(contents)

    def _get_param_obj_attr(self, param: str) -> Tuple[Any, str]:
        m = re.match(r'^([^ ,.[]+)', param, re.IGNORECASE)
        if not m:
            raise KeyError(param)

        # will throw KeyError if the name doesn't eixst
        beam = self.beams[m.group(1)]
        tail = param[m.end():]

        m = re.match(r'^\.([a-z0-9]+)$', tail, re.IGNORECASE)
        if m:
            attr = m.group(1)
            if attr not in _BEAM_PARAMS:
                raise KeyError(attr)

            return beam, attr

        m = re.match(r'^\[([0-9]+)]\.([a-z0-9]+)$', tail, re.IGNORECASE)
        if m:
            # regex ensures this is a valid int
            idx = int(m.group(1))

            if not 0 < idx <= len(beam.grid):
                raise IndexError("invalid beam grid", idx)

            grid = beam.grid[idx-1]

            attr = m.group(2)
            if attr not in _GRID_PARAMS:
                raise KeyError(attr)

            return grid, attr

        raise KeyError(tail)

    def get_param_type_dimension(self, param: str) -> Tuple[str, str]:
        """Determine this paramater's type and dimension.

        Returns a tuple of (type, dimension), where type is either
        'int' or 'float', and dimension is either 'scalar' or
        'vector'.

        Ideally we would also know the range of supported values, as
        e.g. iox values (launch mode) only supports a few values.
        """
        obj, attr = self._get_param_obj_attr(param)

        # everything is contained in dataclasses at the moment
        type = obj.__dataclass_fields__[attr].type

        # everything is scalar at the moment
        if type is float or type == 'float':
            return 'float', 'scalar'
        elif type is int or type == 'int':
            return 'int', 'scalar'
        else:
            # something has gone wrong, need to update this!
            assert False, ('Invalid dataclass type, please fix!', type)

    def __getitem__(self, param: str) -> float:
        """Retrieve parameters of the form 'beamname[grid_idx].param'.

        Raises KeyError if parameter can't be found or not the above
        format.
        """
        obj, attr = self._get_param_obj_attr(param)

        return getattr(obj, attr)

    def __contains__(self, param: str) -> bool:
        """Check for parameters of the form 'beamname[grid_idx].param'."""
        try:
            # throws a KeyError if the parameter doesn't exist
            obj, attr = self._get_param_obj_attr(param)
            return True
        except LookupError:
            # KeyError and IndexError are both LookupErrors
            return False
