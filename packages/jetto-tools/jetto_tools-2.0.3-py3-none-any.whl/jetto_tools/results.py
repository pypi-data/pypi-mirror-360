"""Code for reading JETTO results into Python."""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Iterable, Iterator, Union, Optional

import dataclasses
import itertools
from io import StringIO
from pathlib import Path
import re
import warnings
import os
import json
import glob
import copy

import numpy as np
import pandas as pd
import yaml
from netCDF4 import Dataset
from scipy import interpolate

from jetto_tools.graydata import *
from jetto_tools.transp import convert_jsp_jst_to_netcdf
from jetto_tools.binary import read_binary_file
from jetto_tools.jset import JSET, read as jset_read
from jetto_tools.job import Job, JobError, Status
from jetto_tools.config import Scan, _CoupledScan


@dataclasses.dataclass(frozen=True)
class JsetEcrhParams:
    """Class to interpreted ECRH settings from JSET file."""
    index: int
    beam: str
    selectBeam: bool
    selectInputPower: bool
    selectPolInj: bool
    selectTorInj: bool
    angpec: Optional[float] = None
    angtec: Optional[float] = None
    powec: Optional[float] = None

    @classmethod
    def from_jset(cls, jset: JSET, *, limit=20, only_selected=True) -> List[JsetEcrhParams]:
        results = []
        for idx in range(limit):
            panel = f'ECRHPanel.ECRHGray[{idx}]'
            if f'{panel}.beam' not in jset:
                continue

            selected = jset[f'{panel}.selectBeam']
            if only_selected and not selected:
                continue

            results.append(cls(
                index=idx,
                beam=jset[f'{panel}.beam'],
                angpec=jset[f'{panel}.angpec'],
                angtec=jset[f'{panel}.angtec'],
                powec=jset[f'{panel}.powec'],
                selectBeam=selected,
                selectInputPower=jset[f'{panel}.selectInputPower'],
                selectPolInj=jset[f'{panel}.selectPolInj'],
                selectTorInj=jset[f'{panel}.selectTorInj'],
            ))

        return results


GrayFortHeader = Dict[str, Dict[str, str]]


# see testdata/results/fort.604 for an example of this file
class GrayFortFile:
    """GRAY fort.* output file.

    Header values are retrived by file.get_int('iox').

    Data values are retrived by file.data['rhot'].
    """

    _header: GrayFortHeader
    data: pd.DataFrame

    @classmethod
    def load(cls, path: Union[str, Path]) -> List[GrayFortFile]:
        """Load from the specified file."""
        with open(path) as fd:
            return cls.parse_sections(fd.read())

    @classmethod
    def load_first(cls, paths: Iterable[Union[str, Path]]) -> List[GrayFortFile]:
        """Load from the first specified file that exists.

        Designed to help with cases where files are transitioning to a
        new name, while maintaining backwards compatibility with the
        older names.
        """
        for path in paths:
            try:
                fd = open(path)
                break
            except FileNotFoundError as err:
                last_err = err
        else:
            raise last_err

        with fd:
            return cls.parse_sections(fd.read())

    def __init__(self, header, data):
        """Initialise with contents of a file."""
        self.data = pd.read_csv(StringIO(''.join(data)), delim_whitespace=True)
        self._header = self._parse_header(header)

    def __repr__(self):
        """Return string representation of store."""
        return repr(self._header)

    def get_value(self, key, *, category: Optional[str] = None) -> str:
        """Get string value associated with key.

        Optionally disambiguate via the category, for example
        file.get_value('iox', category='ANT')
        """
        entry = self._header[key]
        if category:
            return entry[category]
        if len(entry) != 1:
            raise KeyError('ambiguous category')
        [value] = entry.values()
        return value

    def get_int(self, key, *, category: Optional[str] = None) -> int:
        """Get integer value associated with key."""
        return int(self.get_value(key, category=category))

    def get_float(self, key, *, category: Optional[str] = None) -> float:
        """Get float value associated with key."""
        return float(self.get_value(key, category=category))

    _RE_HEADER_PREFIX = re.compile(r'^ *#')
    _RE_HEADER_LINE = re.compile(r'^ *# *([A-Z]+) +([a-zA-Z0-9 ]+) *: *([-+ .0-9eE]+) *$')

    @classmethod
    def _split_header_data(cls, lines: Iterable[str]) -> Iterator[Tuple[List[str], List[str]]]:
        re = cls._RE_HEADER_PREFIX

        groupiter = itertools.groupby(lines, key=lambda s: re.match(s) is None)
        for _, header_g in groupiter:
            # must consume this grouper before moving onto the next item
            header = list(header_g)

            _, data_g = next(groupiter)
            data = list(data_g)

            # move the column names from the header into the data for
            # parsing by pandas
            data.insert(0, header.pop().strip(' #'))

            yield header, data

    @classmethod
    def _parse_header(cls, lines: List[str]) -> GrayFortHeader:
        re = cls._RE_HEADER_LINE

        header: GrayFortHeader = {}
        for line in lines:
            m = re.match(line)
            if not m:
                continue
            category = m.group(1)
            keys = m.group(2).split()
            vals = m.group(3).split()
            if len(keys) != len(vals) and vals:
                # we expect some rows have keys but no values!
                warnings.warn('number of keys and values does not match')
            for key, val in zip(keys, vals):
                if key in header:
                    entry = header[key]
                else:
                    entry = header[key] = {}
                entry[category] = val

        return header

    @classmethod
    def parse_sections(cls, contents: str) -> List[GrayFortFile]:
        sections = []
        for header, data in cls._split_header_data(contents.splitlines(True)):
            sections.append(cls(header, data))
        return sections


class EqdskFileError(Exception):
    """Exception from parsing EQDSK files."""

    pass


def _eqdsk_next(lines: Iterator[str]) -> List[float]:
    # get the next line and parse as floats
    line = next(lines)
    # recent code uses 16 characters per field
    if len(line) % 16 == 0:
        field_width = 16
    elif len(line) % 15 == 0:
        field_width = 15
    else:
        raise EqdskFileError('unable to determine field width')

    # fields tend to run together, e.g.:
    #   "0.260981491E+01-0.557889436E-06" is two floats
    # so need to split manually
    result = []
    for i in range(0, len(line), field_width):
        result.append(float(line[i:i+field_width]))
    return result


def _eqdsk_read_vector(lines: Iterator[str], length: int) -> np.ndarray:
    result: List[float] = []

    while len(result) < length:
        result.extend(_eqdsk_next(lines))

    if len(result) > length:
        raise EqdskFileError('line boundary not consistant with field width')

    return np.array(result)


def _calc_rho_tor(psip_n, psiax, psisep, qpsi, nw):
    # create rho_tor grid on even psi_pol grid
    # there is an issue with psiax, psisep from eqdsk file; it needs psiax<psisep
    # but with psisep~0 sometimes psiax>0 and univariate spline complains for
    # non-increasing x.
    # Check psiax, psisep and reverse sign if psiax>psisep
    if psiax > psisep:
        psiax = -psiax
        psisep = -psisep
    interpol_order = 3
    psi_pol = np.empty(len(psip_n))
    for i in range(len(psip_n)):
        psi_pol[i] = psiax+psip_n[i]*(psisep-psiax)
    q_spl_psi = interpolate.UnivariateSpline(psi_pol, qpsi, k=interpol_order, s=1e-5)
    psi_pol_fine = np.linspace(psi_pol[0], psi_pol[-1], nw*10)
    psi_tor_fine = np.empty((nw*10), dtype=float)
    psi_tor_fine[0] = 0.
    for i in range(1, nw*10):
        x = psi_pol_fine[:i+1]
        y = q_spl_psi(x)
        psi_tor_fine[i] = np.trapz(y, x)
    rhot_n_fine = np.sqrt(psi_tor_fine/(psi_tor_fine[-1]-psi_tor_fine[0]))
    rho_tor_spl = interpolate.UnivariateSpline(psi_pol_fine, rhot_n_fine, k=interpol_order, s=1e-5)
    # rhot_n grid (not uniform, on even grid of psi_pol) of resolution=nw
    rhot_n = rho_tor_spl(psi_pol)
    # rho_tor_spl takes value of psi_pol (not normalized) and convert into rhot_n
    return rhot_n


def _calc_B_fields_obmp(Rgrid, rmag, Zgrid, zmag, psirz, psiax, psisep, F, nw, psip_n):
    # Z0_ind is the index of Zgrid of midplane
    Z0_ind = np.argmin(np.abs(Zgrid-zmag))
    # psi_midplane is psi_pol at midplane on even Rgrid
    psi_pol_mp = psirz[Z0_ind, :]
    # Rmag_ind is index of unif_R at rmag
    Rmag_ind = np.argmin(np.abs(Rgrid - rmag))
    psi_pol_obmp = psi_pol_mp[Rmag_ind:].copy()
    # normalize psi_pol_obmp to psip_n_temp
    psip_n_temp = np.empty(len(psi_pol_obmp))
    for i in range(len(psi_pol_obmp)):
        psip_n_temp[i] = (psi_pol_obmp[i]-psiax)/(psisep-psiax)
    unif_R = np.linspace(Rgrid[Rmag_ind], Rgrid[-1], nw*10)
    psip_n_unifR = _interp(Rgrid[Rmag_ind:], psip_n_temp, unif_R)
    psisep_ind = np.argmin(abs(psip_n_unifR-1.02))
    psip_n_obmp = psip_n_unifR[:psisep_ind].copy()
    R_obmp = unif_R[:psisep_ind].copy()
    B_pol_obmp = _fd_d1_o4(psip_n_obmp*(psisep-psiax)+psiax, R_obmp) / R_obmp
    # convert F(on even psi_pol grid) to F(on even R grid)
    F_obmp = _interp(psip_n, F, psip_n_obmp)
    # B_tor = F/R
    B_tor_obmp = F_obmp/R_obmp

    # psip_n_obmp is normalized psi_pol at outboard midplane on uniform unif_R
    # B_tor and B_pol are on uniform unif_R as well
    # psip_n_obmp is unlike psip_n ([0,1]), it goes from 0 to 1.06 here
    return psip_n_obmp, R_obmp, B_pol_obmp, B_tor_obmp


def _calc_B_fields(Rgrid, rmag, Zgrid, zmag, psirz, psiax, psisep, F, nw, psip_n):
    # on Rgrid, Zgrid grid
    # Bp, via BpR and BpZ
    Z0_ind = np.argmin(abs(Zgrid-zmag))
    nR = len(Rgrid)
    nZ = len(Zgrid)

    Bp_Z_grid = np.empty(np.shape(psirz))
    for i in range(nZ):
        Bp_Z_grid[i, :] = _first_derivative(psirz[i, :].flatten(), Rgrid) / Rgrid

    Bp_R_grid = np.empty(np.shape(psirz))
    for i in range(nR):
        Bp_R_grid[:, i] = -_first_derivative(psirz[:, i].flatten(), Zgrid) / Rgrid[i]

    Bp_grid = np.sqrt(Bp_R_grid**2+Bp_Z_grid**2)

    # Bt
    psirz_n = (psirz-psiax)/(psisep-psiax)
    Fma = _interp(psip_n, F, psirz_n[Z0_ind, :])
    # B_tor = F/R
    B_tor = Fma/Rgrid
    Bt_grid = np.empty(np.shape(psirz))
    for i in range(nZ):
        Bt_grid[i, :] = B_tor

    return Bp_grid, Bt_grid


def _fd_d1_o4(var: np.ndarray, grid: np.ndarray, mat: Optional[np.ndarray] = None):
    """Centered finite difference, first derivative, 4th order.

    var: quantity to be differentiated.
    grid: grid for var
    mat: matrix for the finite-differencing operator.

    if mat=None then it is created
    """
    if mat is None:
        mat = _get_mat_fd_d1_o4(len(var), grid[1] - grid[0])

    dvar = np.dot(mat, var)
    dvar[:2] = 0.0
    dvar[-2:] = 0.0
    return dvar


def _get_mat_fd_d1_o4(size, dx):
    """Create a matrix for centered finite difference, first derivative, 4th order.

    size: size of (number of elements in) quantity to be differentiated
    dx: grid spacing (for constant grid).
    """
    mat = np.zeros((size, size))

    i1 = np.arange(size - 1)
    i2 = np.arange(size - 2)

    # set up off diagonals
    mat[i2, i2+2] = +1.0
    mat[i1, i1+1] = -8.0
    mat[i1+1, i1] = +8.0
    mat[i2+2, i2] = -1.0

    # prefactor
    mat /= 12.0 * dx

    return mat


def _interp(xin: np.ndarray, yin: np.ndarray, xnew: np.ndarray):
    """
    xin: x variable input
    yin: y variable input
    xnew: new x grid on which to interpolate
    yout: new y interpolated on xnew
    """
    # splrep returns a knots and coefficients for cubic spline
    rho_tck = interpolate.splrep(xin, yin)

    # Use these knots and coefficients to get new y
    return interpolate.splev(xnew, rho_tck, der=0)


def _first_derivative(f_in, x_in):
    x = x_in.flatten()
    f = f_in.flatten()
    dx = x[1]-x[0]
    dfdx = np.empty(len(f))
    for i in range(len(f)):
        if i == 0:
            dfdx[i] = (f[i+1] - f[i])/dx
        elif i == 1 or i == len(f)-2:
            dfdx[i] = (f[i+1]-f[i-1])/2./dx
        elif i == len(f)-1:
            dfdx[i] = (f[i] - f[i-1])/dx
        else:
            dfdx[i] = (-f[i+2]+8.*f[i+1]-8.*f[i-1]+f[i-2])/12./dx

    return dfdx


@dataclasses.dataclass(frozen=True)
class EqdskFile:
    """Class to store a loaded EQDSK file."""

    nw: int
    nh: int
    nbdry: int
    nlim: int

    rdim: float
    zdim: float
    rctr: float
    rmin: float
    zmid: float
    rmag: float
    zmag: float
    psiax: float
    psisep: float
    Bctr: float

    # even grid of psi_pol, on which all 1D fields are defined
    psip_n: np.ndarray

    # F, p, ffprime, pprime, qpsi are on psip_n
    F: np.ndarray
    p: np.ndarray
    ffprime: np.ndarray
    pprime: np.ndarray
    qpsi: np.ndarray

    # uniform (R,Z) grid, psirz is on this grid
    psirz: np.ndarray
    psirz_n: np.ndarray
    Rgrid: np.ndarray
    Zgrid: np.ndarray

    # boundary units are meters, shape = (nbdry)
    rbdry: np.ndarray
    zbdry: np.ndarray
    # shape = (nlim)
    xlim: np.ndarray
    ylim: np.ndarray
    #
    rhot_n: np.ndarray
    #
    B_pol: np.ndarray
    B_tor: np.ndarray

    @classmethod
    def parse(cls, contents: str) -> EqdskFile:
        """Parse a file that's been read into memory.

        Files are relatively small, <1MB, so loading the whole thing
        seems reasonable!
        """
        # jetto-sanco/jetto/setbnd.f is a useful reference for seeing how the file is written

        lines = iter(contents.splitlines())

        # parse header to get grid size
        header = next(lines).split()
        nw, nh = int(header[-2]), int(header[-1])

        # not sure what these are!
        rdim, zdim, rctr, rmin, zmid = _eqdsk_next(lines)
        rmag, zmag, psiax, psisep, Bctr = _eqdsk_next(lines)
        _, psiax2, _, rmag2, _ = _eqdsk_next(lines)
        zmag2, _, psisep2, _, _ = _eqdsk_next(lines)

        # validation from Krassimir's code
        if rmag != rmag2:
            raise EqdskFileError(f"Inconsistent rmag {rmag} != {rmag2}")
        if psiax != psiax2:
            raise EqdskFileError(f"Inconsistent psiax {psiax} != {psiax2}")
        if zmag != zmag2:
            raise EqdskFileError(f"Inconsistent zmag: {zmag} != {zmag2}")
        if psisep != psisep2:
            raise EqdskFileError(f"Inconsistent psisep: {psisep} != {psisep2}")

        # read out vectors and matrix
        F = _eqdsk_read_vector(lines, nw)
        p = _eqdsk_read_vector(lines, nw)
        ffprime = _eqdsk_read_vector(lines, nw)
        pprime = _eqdsk_read_vector(lines, nw)
        psirz = _eqdsk_read_vector(lines, nh*nw).reshape(nh, nw)
        qpsi = _eqdsk_read_vector(lines, nw)

        # finally get optional boundary and limits
        nbdry, nlim = map(int, next(lines).split())
        rzbdry = _eqdsk_read_vector(lines, nbdry * 2) if nbdry > 0 else np.array([0., 0.])
        xylim = _eqdsk_read_vector(lines, nlim * 2) if nlim > 0 else np.array([0., 0.])

        # rhot, B
        psip_n = np.linspace(0, 1, nw)
        psirz_n = (psirz - psiax) / (psisep - psiax)
        Rgrid = rmin + np.linspace(0, rdim, nw)
        Zgrid = zmid + np.linspace(-zdim, zdim, nh) / 2
        rhot_n = _calc_rho_tor(psip_n, psiax, psisep, qpsi, nw)
        B_pol, B_tor = _calc_B_fields(Rgrid, rmag, Zgrid, zmag, psirz, psiax, psisep, F, nw, psip_n)

        return cls(
            nw=nw, nh=nh,
            nbdry=nbdry, nlim=nlim,

            rdim=rdim, zdim=zdim, rctr=rctr,
            rmin=rmin, zmid=zmid, rmag=rmag,
            zmag=zmag, psiax=psiax, psisep=psisep,
            Bctr=Bctr,

            psip_n=psip_n,

            F=F, p=p, ffprime=ffprime,
            pprime=pprime, qpsi=qpsi,

            psirz=psirz, psirz_n=psirz_n,
            Rgrid=Rgrid,
            Zgrid=Zgrid,

            rbdry=rzbdry[0::2], zbdry=rzbdry[1::2],
            xlim=xylim[0::2], ylim=xylim[1::2],

            rhot_n=rhot_n,
            B_pol=B_pol, B_tor=B_tor
        )

    @classmethod
    def load(cls, path: Union[Path, str]) -> EqdskFile:
        """Load and parse the contents of an on disk file."""
        with open(path) as fd:
            return cls.parse(fd.read())


class JettoResults:
    root: Path
    device: str
    spn: int

    def __init__(
            self, *,
            path: Optional[Path] = None, run: Optional[str] = None,
            device=None, spn=None,
    ):
        if path:
            root = Path(path)
        elif run:
            root = Path.home() / 'jetto/runs' / run
        else:
            raise ValueError('please specify either a path or run')

        if not root.is_dir():
            raise ValueError('Jetto results should be in a directory')

        self.root = root
        self.device = device
        self.spn = spn

    def _convert_jsp_jst_to_netcdf(self):
        convert_jsp_jst_to_netcdf(
            self.device, self.spn, 0,
            self.root / 'jetto.jsp', self.root / 'jetto.jst',
        )

    def load_jset(self):
        path = self.root / 'jetto.jset'
        return jset_read(path)

    def load_profiles(self) -> Dataset:
        path = self.root / 'profiles.CDF'

        if not path.exists():
            self._convert_jsp_jst_to_netcdf()

        return Dataset(path)

    def load_timetraces(self) -> Dataset:
        path = self.root / 'timetraces.CDF'

        if not path.exists():
            self._convert_jsp_jst_to_netcdf()

        return Dataset(path)

    def load_jsp(self) -> Dict[str, Any]:
        return read_binary_file(self.root / 'jetto.jsp')

    def load_jst(self) -> Dict[str, Any]:
        return read_binary_file(self.root / 'jetto.jst')

    def get_eqdsk_times(self) -> List[float]:
        results = []

        for path in self.root.glob('jetto_*.eqdsk'):
            m = re.match(r'^jetto_([0-9]+\.[0-9]+)\.eqdsk$', path.name, re.IGNORECASE)
            if m:
                results.append(float(m.group(1)))

        results.sort()

        return results

    def load_eqdsk(self, time: Optional[float] = None) -> EqdskFile:
        if time is None:
            path = self.root / 'jetto.eqdsk_out'
        else:
            path = self.root / f'jetto_{time:.6f}.eqdsk_out'

        return EqdskFile.load(path)

    def load_graybeams(self) -> List[graydata.GrayBeamData]:
        return graydata.parse_graybeam_data(
            (self.root / 'graybeam.data').read_text(),
        )

    def load_gray_central_ray_coord(self) -> List[GrayFortFile]:
        return GrayFortFile.load_first((
            self.root / 'gray_central_ray_coord',
            self.root / 'fort.604',
        ))

    def load_gray_beam_CS(self) -> GrayFortFile:
        [section] = GrayFortFile.load_first((
            self.root / 'gray_beam_CS',
            self.root / 'fort.608',
        ))
        return section

    def load_gray_beam_transv(self) -> GrayFortFile:
        [section] = GrayFortFile.load_first((
            self.root / 'gray_beam_transv',
            self.root / 'fort.604',
        ))
        return section

    def load_grayfort(self, unit: int) -> GrayFortFile:
        [section] = GrayFortFile.load(
            self.root / f'fort.{unit}',
        )
        return section


class SignalSummary:
    """Defines the summary characteristics of a JST signal"""
    def __init__(self, name: str, signal: np.array):
        self._name = name
        self._value = signal[-1]

        l_80 = int(len(signal) * 0.8)
        self._convergence = np.std(signal[l_80:])

    @property
    def name(self) -> str:
        """"The name of the signal"""
        return self._name

    @property
    def value(self) -> float:
        """The final value of the signal"""
        return self._value

    @property
    def convergence(self) -> float:
        """The covergence of the signal

        Convergence is defined as the standard deviation of the final 20% of the signal timeseries
        """
        return self._convergence


class ResultsError(Exception):
    """Generic exception used for problems analysing results"""
    pass


@dataclasses.dataclass
class PointSummary:
    """Defines a summary of the results of a given JETTO run"""
    status: int = Status.UNKNOWN
    parameters: Dict = dataclasses.field(default_factory=dict)
    signals: Dict[str, SignalSummary] = dataclasses.field(default_factory=dict)


class SummaryError(Exception):
    """Generic exception used for all summary errors"""
    pass


@dataclasses.dataclass
class ScanSummary:
    params: List[str]
    param_values: Dict[str, np.ndarray]
    signals: List[str]
    signals_values: Dict[str, np.ndarray]
    signals_convergences: Dict[str, np.ndarray]


def retrieve_point_summary(rundir: str, signals: List = []) -> PointSummary:
    """Retrieve a summary for a given JETTO run

    Creates a PointSummary associated with the run contained in ``rundir``. The ``parameters`` in the returned
    ``PointSummary`` are those of the run's serialisation file; the ``signals`` are theose obtained by extracting the
    corresponding signals from the run's ``jetto.jst`` file. The status is that given by the ``jetto.status`` file in
    the run directory

    :param rundir: Path to the run directory
    :type rundir: str
    :param signals: Desired signals from the run's JST file
    :type signals: List[str]
    :return: Summary for the run
    :rtype: PointSummary
    :raise: SummaryError if the summary cannot be retrieved
    """
    try:
        job = Job(rundir)
    except JobError as err:
        raise SummaryError(f'Failed to create job from run directory {rundir} ({str(err)})')

    config = job.serialisation
    if config is None:
        raise SummaryError(f'Serialisation file for run directory {rundir} not found')

    try:
        params = config['parameters']
    except KeyError:
        raise SummaryError(f'"parameters" not found in f{config}')

    jst = os.path.join(rundir, 'jetto.jst')
    if not os.path.isfile(jst):
        raise SummaryError(f'JST file {jst} not found')

    jst_signals = read_binary_file(jst)
    try:
        summary_signals = {k: SignalSummary(k, jst_signals[k][0]) for k in signals}
    except KeyError as err:
        raise SummaryError(f'Expected signal not found in file {jst} ({str(err)})')

    return PointSummary(parameters=params, signals=summary_signals, status=job.status())


def _scan_index_from_point(parameters: List[Tuple[str]], scans: Dict[Tuple[str], Tuple[np.ndarray]], point: Dict) -> Tuple:
    """Extract a scan index of a scan point

    Based on the values of the parameters at the givne point the scan, work out the corresponding index. The index is
    tuple of integers representing the location of the point within the scan space

    An important point is that, for any point in a coupled scan, only the first parameter of the couple is used to
    determine the index for that parameter. So this function implicitly assumes that any subsequent parameters in the
    couple have values which are consistent with the first parameter in the couple.

    :param parameters: List of scan parameters. Indices are determined according to the ordering of the list
    :type parameters: List[Tuple[str]]
    :scans: The collection of scans
    :type scans: Dict[Tuple[str], Tuple[np.ndarray]]
    :param point: Point for which the index shoulds be determined
    :type point: Dict
    :return: Index of the point
    :rtype: Tuple[int]
    """
    parameters_flattened = [parameter[0] for parameter in parameters]
    scans_flattened = {couple[0]: values[0] for couple, values in scans.items()}

    return tuple([np.where(scans_flattened[parameter] == point[parameter])[0][0]
                  for parameter in parameters_flattened])


def _aggregate_scans(scans: Dict[str, np.ndarray]) -> Dict[Tuple(str), Tuple(np.ndarray)]:
    """Aggregate raw scans into groups

    Given a collection of scans, converts both keys and values into tuples. Non-coupled scans are the only elements of
    their respective tuples. Coupled scans are aggregated together into tuples

    :param scans: Raw collection of scans
    :type scans: Dict[str, np.ndarray]
    :return: Aggregated scans
    :rtype: Dict[Tuple[str], Tuple[np.ndarray]]
    """
    scans_new = {}

    for param, values in scans.items():
        if isinstance(values, _CoupledScan):
            index = tuple(sorted([param, *values.params()]))
            if index not in scans_new:
                scans_new[index] = tuple([scans[i] for i in index])
        else:
            scans_new[(param, )] = (values, )

    if not len(scans) == sum(len(k) for k in scans_new):
        raise SummaryError(f'Inconsistent set of scans: {scans}')

    return scans_new


def _point_summaries_to_scan_summary(signals: List[str], scans: Dict[str, np.ndarray],
                                     point_summaries: Dict[str, PointSummary]) -> ScanSummary:
    """Convert a collection of point summaries to a scan summary

    Keys of the input are assumed to be point directories of the form 'point_<abc>'. Values of the input are assumed
    to be the point summaries associated with the point. The values of a scan are assumed to be sorted in ascending
    order. The number of points in the point summaries is assumed to match the size of the scan.

    The returned ScanSummary aggregates the contents of the point summaries

    :signals: List of signals desired in the summary
    :type signals: List[str]
    :param scans: Scanned parameter values
    :type scans: Dict[str, np.ndarray]
    :param point_summaries: Collection of summaries for all of the scan points
    :type point_summaries: Dict[str, PointSummary]
    :return: Scan summary
    :rtype: ScanSummary
    """

    parameters = list(scans)

    shape = tuple(len(scans[scan][0]) for scan in parameters)

    signals_values = {
        signal: np.ma.zeros(shape) for signal in signals
    }
    for signal in signals_values:
        signals_values[signal].mask = True

    signals_convergences = {
        signal: np.ma.zeros(shape) for signal in signals
    }
    for signal in signals_convergences:
        signals_convergences[signal].mask = True

    for point in point_summaries:
        point_summary = point_summaries[point]

        point_indices = _scan_index_from_point(parameters, scans, point_summary.parameters)

        if point_summary.status == Status.SUCCESSFUL:
            for signal in signals:
                signals_values[signal][point_indices] = point_summary.signals[signal].value
                signals_convergences[signal][point_indices] = point_summary.signals[signal].convergence

    return ScanSummary(params=parameters, param_values=scans, signals=signals,
                       signals_values=signals_values, signals_convergences=signals_convergences)


DEFAULT_SUMMARY_SIGNALS = ['CUR', 'CUBS', 'CUEB', 'PFUS',
                           'PEBW', 'PAUX', 'QFUS', 'H98Z',
                           'T98Z', 'T98Y', 'WTOT', 'BNTT',
                           'QMIN', 'LI', 'LI3', 'EMAX', 'BLST',
                           'H98Y', 'NEBA', 'TEBA', 'TIBA']


def retrieve_scan_summary(run_root: str, signals: List = DEFAULT_SUMMARY_SIGNALS) -> ScanSummary:
    """Retrieve a summary for a given JETTO scan

    Loads the results of each point in the scan rooted at ``run_root``. Aggregates the results into an
    overall scan summary, which list the values and convergences for each desired signal.

    :param run_root: Path to the directory containing the point directories of the scan
    :type run_root: str
    :param signals: Signals to include in the summary
    :type signals: List[str]
    :return: Summary of the scan
    :rtype: ScanSummary
    """
    if not os.path.isdir(run_root):
        raise SummaryError(f'Run root {run_root} not found')

    serialisation = os.path.join(run_root, 'serialisation.json')
    if not os.path.isfile(serialisation):
        raise SummaryError(f'Scan serialisation {serialisation} not found')

    with open(serialisation) as f:
        serialisation_contents = json.loads(f.read(), object_hook=_CoupledScan.from_json)
        try:
            params = serialisation_contents['parameters']
        except KeyError:
            raise SummaryError(f'Parameters not found in serialisation {serialisation}')

    raw_scans = {k: v for k, v in params.items() if isinstance(v, Scan)}
    if not raw_scans:
        raise SummaryError(f'No scans found in {run_root}')

    aggregated_scans = _aggregate_scans(raw_scans)
    scans = {index: tuple(np.sort(list(v)) for v in values) for index, values in aggregated_scans.items()}

    pointdirs = glob.glob(os.path.join(run_root, 'point_*'))
    point_summaries = {}
    for pointdir in pointdirs:
        try:
            point_summary = retrieve_point_summary(pointdir, signals)
        except SummaryError:
            continue
        else:
            point_summaries[os.path.basename(pointdir)] = retrieve_point_summary(pointdir, signals)

    return _point_summaries_to_scan_summary(signals, scans, point_summaries)


def label_point(pointdir, scan_params: List = [], template: str = None, point_index: int = None,
                scan_label: str = None):
    """Label a point directory

    Generates a labels.yaml file in the point directory, describing the point

    :param pointdir: Path to the point directory
    :type pointdir: str
    :param scan_params: Parameters being scanned over
    :type scan_params: List[str]
    :param template: Catalogue identifier of the template (if applicable)
    :type template: str
    :param point_index: Index of the point within the scan (if applicable)
    :type point_index: int
    :param scan_label: Label of the scan (if applicable)
    :type scan_label: str
    """
    try:
        job = Job(pointdir)
    except JobError as err:
        raise ResultsError(f'Failed to create job from {pointdir} ({str(err)})')

    if job.serialisation is None:
        raise ResultsError(f'Serialisation file not found')

    config = job.serialisation

    try:
        labels = {f'scan-param-{param}': config['parameters'][param] for param in scan_params}
    except KeyError as err:
        raise ResultsError(f'Scan parameter not found ({str(err)})')

    labels['template'] = template
    labels['point-index'] = point_index
    labels['scan-label'] = scan_label
    labels['run-status'] = Status.to_string(job.status())

    labels_file = os.path.join(pointdir, 'labels.yaml')
    with open(labels_file, 'w') as f:
        yaml.dump(labels, f)


def label_scan(scandir, template: str = None, scan_label: str = None):
    """Label the contents of a scan

    Generates a labels.yaml file in each point directory of the scan, describing the point

    :param scandir: Path to the scan directory
    :type scandir: str
    :param template: Catalogue identifier of the template (if applicable)
    :type template: str
    :param scan_label: Label of the scan (if applicable)
    :type scan_label: str
    """
    if not os.path.isdir(scandir):
        raise ResultsError(f'Directory {scandir} not found')

    serialisation = os.path.join(scandir, 'serialisation.json')
    if not os.path.isfile(serialisation):
        raise ResultsError(f'Serialisation file {serialisation} not found')

    with open(serialisation) as f:
        config = json.loads(f.read(), object_hook=Scan.from_json)
    scan_params = [param for param, value in config['parameters'].items() if isinstance(value, Scan)]

    for pointdir in glob.glob(os.path.join(scandir, 'point_*')):
        point_index = int(pointdir[-3:])
        label_point(pointdir, template=template, point_index=point_index,
                    scan_params=scan_params, scan_label=scan_label)
