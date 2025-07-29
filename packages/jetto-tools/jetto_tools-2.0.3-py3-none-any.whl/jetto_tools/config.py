from __future__ import annotations

import shutil
from typing import Union, Iterable, Iterator, List, Dict, Optional, Any
from pathlib import Path
from shutil import copyfile
import dataclasses
from copy import deepcopy
from numpy import linspace
import json
import datetime
import os.path
import os
import itertools
import yaml
import subprocess
from functools import reduce
from operator import mul

import jetto_tools.template
import jetto_tools.lookup
import jetto_tools.namelist
import jetto_tools._utils as _utils
import jetto_tools.jset
import jetto_tools.common as common
from jetto_tools.common import Driver, IMASDB, CatalogueId

from jetto_tools import __version__


class ScanError(Exception):
    """Generic exception used for all scan"""
    pass


class Scan:
    """Class representing a parameter scan"""

    def __init__(self, points: Iterable):
        """Initialise a scan with points

        A scan be initialised by an iterable object that can be trivially transformed into a list (e.g. list, tuple,
        range, set etc.). An empty scan is not allowed: a scan must contain at least one point.

        :param points: Iterable object containing the points
        :type points: Iterable
        :raise: ScanError if points cannot be iterate over, or if points is empty
        """
        try:
            _ = iter(points)
        except TypeError:
            raise ScanError('Scan points must be initialised by an iterable object')

        if len(points) == 0:
            raise ScanError('Scan must have at least one point')

        for point in points:
            if isinstance(point, list):
                if not all(_utils.is_numeric(p) for p in point):
                    raise ScanError(f'Value {p} in scan point {point} is not numeric')
            else:
                if not _utils.is_numeric(point):
                    raise ScanError(f'Point {point} in scan is not numeric')

        self._points = points

    def __len__(self):
        """The number of points in the scan"""
        return len(self._points)

    def __iter__(self):
        """Iterate over the points in the scan"""
        return iter(self._points)

    def __getitem__(self, key):
        """Get the value of a point

        :param key: Index of the point
        :type key: int
        """
        return self._points[key]

    def __setitem__(self, key, value):
        """Prevent update of a scan point

        :raise: Always raises a ScanError
        """
        raise ScanError('Cannot update value in scan')

    def __repr__(self):
        """String representation of a scan

        :return: String with format 'Scan([p0, p1, p2,...])'
        """
        return 'Scan([{}])'.format(', '.join([str(p) for p in self._points]))

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        else:
            return all([a == b and type(a) == type(b) for a, b in zip(self, other)])

    def __ne__(self, other):
        return not self == other

    @classmethod
    def to_json(cls, scan: Scan):
        if isinstance(scan, Scan):
            return {'__class__': 'Scan',
                    '__value__': list(scan)}
        else:
            raise TypeError(repr(scan) + ' is not JSON serializable')

    @classmethod
    def from_json(cls, d: Dict):
        try:
            return Scan(d['__value__'])
        except KeyError:
            return d


class _CoupledScan(Scan):
    """Class representing a Coupled Scan over two or more parameters

    This class is for internal use only and should never be instantiated by a user
    """

    def __init__(self, points: Iterable, params: List[str]):
        self._coupled_params = params
        super().__init__(points)

    def params(self):
        return self._coupled_params

    def __repr__(self):
        """String representation of a Coupled Scan

        :return: String with format '_CoupledScan([p0, p1, p2, ...], [coupled0, coupled1, ...])
        """
        return f'_CoupledScan([{", ".join([str(p) for p in self._points])}], ' \
               f'[{", ".join([str(p) for p in self._coupled_params])}])'

    @classmethod
    def to_json(cls, scan: _CoupledScan):
        if isinstance(scan, _CoupledScan):
            return {'__class__': '_CoupledScan',
                    '__value__': list(scan),
                    '__coupled_with__': scan._coupled_params
                    }
        else:
            return Scan.to_json(scan)

    @classmethod
    def from_json(cls, d: Dict):
        try:
            return _CoupledScan(d['__value__'], d['__coupled_with__'])
        except KeyError:
            return Scan.from_json(d)


class RunConfigError(Exception):
    """Generic exception used for all configuration errors"""
    pass


def _is_gray_parameter(param: str) -> bool:
    return param.startswith('GRAY:')


def _split_gray_parameter(param: str) -> Optional[str]:
    if _is_gray_parameter(param):
        return param[5:]


class RunConfig:
    """Class representing a JETTO run configuration"""
    _SCAN_DIMENSION_MAX_LENGTH = 100
    _SCAN_MAX_DIMENSIONS = 3
    _SCAN_MAX_POINTS = 500

    @dataclasses.dataclass(frozen=True)
    class _Point:
        name: str
        index: int
        files: Dict[str, Union[str, os.PathLike]]
        loadmodule: Dict[str, Any]
        parameters: Dict[str, Any]
        processors: int
        walltime: float
        time_config: common.TimeConfig

        def serialise(self) -> str:
            return json.dumps({
                'name': self.name,
                'index': self.index,
                'files': {str(name): str(path) for name, path in self.files.items()},
                'loadmodule': self.loadmodule,
                'parameters': self.parameters,
                'processors': self.processors,
                'walltime': self.walltime,
                'start_time': self.time_config.start_time,
                'end_time': self.time_config.end_time,
                'esco_timesteps': self.time_config.n_esco_times,
                'profile_timesteps': self.time_config.n_output_profile_times
            }, indent=4)

        @property
        def exfile(self):
            return self.files[Path('jetto.ex')]

        def get_private_graybeam_filename(self, now: datetime.datetime) -> Path:
            root = Path.home() / 'cmg/jams/data/ecrh'

            parent = root / f'{self.name}_{now:%Y-%m-%d}'
            if parent.exists():
                # this should be unique enough for now
                parent = root / f'{self.name}_{now:%Y-%m-%d}_{now:%H%M%S}'

            path = parent / f'graybeam_{self.index:03}.data'
            return path.absolute()

    def __init__(self, template: jetto_tools.template.Template):
        """Initialise a JETTO run configuration

        Initialises the run configuration based on the template provided. Each parameter in the lookup is assigned an
        initial value, based on the value of the parameter in the template JSET. The initial value of the ex-file path,
        the load module, and the number of processors are also extracted from the JSET.

        :param template: JETTO run template
        :type template: jetto_tools.template.Template
        """
        self._files = RunConfig._initial_template_files(template)
        self._processors = template.jset.processors
        self._loadmodule = {
            'binary': template.jset.binary,
            'userid': template.jset.userid
        }
        self._walltime = template.jset.walltime
        self._parameters = {name: RunConfig._initial_template_value(param, template.jset)
                            for name, param in template.lookup.items()}
        self._template = template
        self._exfile_updated = False
        self._graybeamfile_updated = False
        self._time_config = self._template.jset.get_time_config()

        self._read_from_ids = template.jset.read_ids
        self._create_output_ids = template.jset.write_ids
        self._input_ids_source = template.jset.input_ids_source
        self._input_ids_source_updated = False

    @property
    def exfile(self) -> str:
        """Get the JETTO exfile path

        :return: The path
        :rtype: str
        """
        return str(self._files[Path('jetto.ex')])

    @exfile.setter
    def exfile(self, value: Union[str, os.PathLike]):
        """Set the JETTO exfile path

        Path is expanded to an absolute path before being set. Note that setting the path to a diffferent value from
        that found in the template will cause the exfile to be listed as 'Private' rather than 'Cataloged' when the
        JSET is exported.

        :param value: The path to the exfile
        :type value: Union[str, os.PathLike]
        """
        self._files[Path('jetto.ex')] = Path(value).resolve()
        self._exfile_updated = True

    @property
    def binary(self) -> str:
        """Get the JETTO binary version

        :return: The binary version
        :rtype: str
        """
        return self._loadmodule['binary']

    @binary.setter
    def binary(self, value: str):
        """Set the JETTO binary version

        :param value: The binary version
        :type value: str
        """
        self._loadmodule['binary'] = value

    @property
    def userid(self) -> str:
        """Get the JETTO userid

        :return: The userid
        :rtype: str
        """
        return self._loadmodule['userid']

    @userid.setter
    def userid(self, value: str):
        """Set the JETTO userid

        :param value: The userid
        :type value: str
        """
        self._loadmodule['userid'] = value

    @property
    def processors(self) -> int:
        """Get the number of processors

        Returns the number of processors configured for running a JETTO job (corresponds to the 'Number Of Processors'
        field in the JAMS 'Job Process' panel).

        :return: Number of processors
        :rtype: int
        """
        return self._processors

    @processors.setter
    def processors(self, value: int):
        """Set the number of processors

        Sets the number of processors configured for running a JETTO job (corresponds to the 'Number Of Processors'
        field in the JAMS 'Job Process' panel).

        :param value: Number of processors
        :type value: int
        :raise: RunConfigError if the supplied value is invalid
        """
        if not isinstance(value, int):
            raise RunConfigError(f'Invalid processors value {value}')
        if value < 1:
            raise RunConfigError(f'Invalid processor count {value}')

        self._processors = value

    @property
    def walltime(self):
        """Get the JETTO walltime

        Gets the walltime configured for the JETTO run (corresponds to the 'walltime' field in the JAMS
        'Job Process' panel).

        :return: The walltime
        :rtype: int
        """
        return self._walltime

    @walltime.setter
    def walltime(self, value: Union[int, float]):
        """Set the JETTO walltime

        Sets the walltime configured for the JETTO run (corresponds to the 'walltime' field in the JAMS
        'Job Process' panel).

        :param value: The walltime, in hours
        :type value: int or float
        :raise: RunConfigError if the value is invalid
        """
        if not _utils.is_numeric(value):
            raise RunConfigError(f"Invalid type of {value} for walltime")
        if value <= 0:
            raise RunConfigError(f"Invalid value of {value} for walltime")

        self._walltime = value

    @property
    def start_time(self):
        """Get the value of the start time

        :return: The start time
        :rtype: float
        """
        return self._time_config.start_time

    @start_time.setter
    def start_time(self, value):
        """Set the value of the start time

         :param value: The start time
         :type value: float
         :raise: RunConfigError if the value is not a float, or if it is negative
         """
        if not _utils.is_numeric(value):
            raise RunConfigError(f'Invalid value {value} for start time')
        if value < 0:
            raise RunConfigError(f'Invalid value {value} for start time')

        self._time_config.start_time = float(value)

    @property
    def end_time(self):
        """Get the value of the end time

        :return: The end time
        :rtype: float
        """
        return self._time_config.end_time

    @end_time.setter
    def end_time(self, value):
        """Set the value of the end time

         :param value: The end time
         :type value: float
         :raise: RunConfigError if the value is not a float, or if it is negative
         """
        if not _utils.is_numeric(value):
            raise RunConfigError(f'Invalid value {value} for end time')
        if value < 0:
            raise RunConfigError(f'Invalid value {value} for end time')

        self._time_config.end_time = float(value)

    @property
    def esco_timesteps(self):
        """Get the number of timesteps for ESCO

        :return: The number of timesteps
        :rtype: int
        """
        return self._time_config.n_esco_times

    @esco_timesteps.setter
    def esco_timesteps(self, value: int):
        """Set the number of ESCO timesteps

         :param value: The number of timesteps
         :type value: int
         :raise: RunConfigError if the value is not an integer, or if it is less than 2
         """
        if not isinstance(value, int) or value < 1:
            raise RunConfigError(f'Invalid value {value} for ESCO timesteps')

        self._time_config.n_esco_times = value

    @property
    def profile_timesteps(self):
        """Get the number of timesteps for the output profile

        :return: The number of timesteps
        :rtype: int
        """
        return self._time_config.n_output_profile_times

    @profile_timesteps.setter
    def profile_timesteps(self, value: int):
        """Set the number of output profile timesteps

         :param value: The number of timesteps
         :type value: int
         :raise: RunConfigError if the value is not an integer, or if it is negative
         """
        if not isinstance(value, int) or value < 0:
            raise RunConfigError(f'Invalid value {value} for output profile timesteps')

        self._time_config.n_output_profile_times = value

    @property
    def read_from_ids(self) -> bool:
        """Get the read from IDS status

        Returns true if the configuration is set to read input data from IMAS IDS files. Corresponds to the
        value of the ``Read from IDS`` tick-box in the JETTO Setup Panel in JAMS.

        :return: The read from IDS status
        :rtype: bool
        """
        return self._read_from_ids

    @read_from_ids.setter
    def read_from_ids(self, value: bool):
        """Set the read from IDS status

        Sets the configuration to read/not read input data from IMAS IDS files. Corresponds to setting the value of
        the ``Read from IDS`` tick-box in the JETTO Setup Panel in JAMS.

        :param value: The read from IDS status
        :type value: bool
        :raise: RunConfigError if the template is a standard case
        """
        if self.driver == Driver.Std:
            raise RunConfigError('Cannot set read from IDS status for standard case')

        self._read_from_ids = value

    @property
    def create_output_ids(self) -> bool:
        """Get the create output IDS status

        Returns true if the configuration is set to write output data to IMAS IDS files. Corresponds to the
        value of the ``Create output IDS`` tick-box in the JETTO Job Process Panel in JAMS.

        :return: The create output IDS status
        :rtype: bool
        """
        return self._create_output_ids

    @create_output_ids.setter
    def create_output_ids(self, value: bool):
        """Set the create output IDS status

        Sets the configuration to write/not write output data to IMAS IDS files. Corresponds to setting the value of
        the ``Create output IDS`` tick-box in the JETTO Job Process in JAMS.

        :param value: The create output IDS status
        :type value: bool
        :raise: RunConfigError if the template is a standard case
        """
        if self.driver == Driver.Std:
            raise RunConfigError('Cannot set create output IDS status for standard case')

        self._create_output_ids = value

    @property
    def input_ids_source(self):
        """Get the source of the input IDS data

        Gets the source (catalogued or private) of the input IDS data. Corresponds to the ``IDS Source`` drop-downs in
        the JETTO Setup Panel in JAMS.

        :return: The source of the input IDS data
        :rtype: Union[IMASDB, CatalogueId]
        """
        return self._input_ids_source

    @input_ids_source.setter
    def input_ids_source(self, value: IMASDB):
        """Set the source of the input IDS data

        Sets the source of the input IDS data. Only supports setting a private source: attempting to set a catalogued
        source will fail. Corresponds to setting the the ``IDS Source`` drop-downs in the JETTO Setup Panel in JAMS.

        :param value: The source of the input IDS data
        :type value: IMASDB
        :raise: RunConfigError if the new source is catalgued rather than private
        """
        if self.driver == Driver.Std:
            raise RunConfigError('Cannot set input IDS source for standard case')

        if self.read_from_ids is False:
            raise RunConfigError('Cannot set input IDS source for case which does not read from IDS')

        if isinstance(value, CatalogueId):
            raise RunConfigError('Cannot set input IDS source from catalogued case')

        self._input_ids_source = value
        self._input_ids_source_updated = True

    @property
    def ids_in(self) -> IMASDB:
        """Get the path to the runtime input IDS files

        Returns an IMASDB object indicating the path to the input IDS data (if any), with respect to the run directory.
        If IDS input is disabled, the IMASDB is filled with placeholder values.

        :return: The input IMASDB
        :rtype: IMASDB
        """
        if self.read_from_ids:
            return IMASDB(user='imasdb', machine=self._template.jset.machine, shot=self._template.jset.shot, run=1)

        return IMASDB(user=None, machine='dummy', shot=0, run=0)

    @property
    def ids_out(self) -> IMASDB:
        """Get the path to the runtime output IDS files

        Returns an IMASDB object indicating the path to the output IDS data (if any), with respect to the run directory.
        The IMASDB object contains the same values regardless of whether the IDS output is enabled or not (matching
        the behaviour of JAMS).

        :return: Enabled flag and output IMASDB
        :rtype: IMASDB
        """
        return IMASDB(user='imasdb', machine=self._template.jset.machine, shot=self._template.jset.shot, run=2)

    @property
    def driver(self) -> Driver:
        """Get the driver used for JETTO

        Defaults to the standard driver if the setting is missing from the template JSET

        :return: The driver used (Standard or IMAS)
        :rtype: Driver
        """
        if self._template.jset.driver is None:
            return Driver.Std

        return self._template.jset.driver

    def serialise(self) -> str:
        """Serialise the configuration

        Serialisation produces a JSON string representing the configuration. The keys in the JSON string are:

        * 'files': The absolute paths to the extra files
        * 'loadmodule': The JETTO executable to use, consisting of two keys:

          * 'binary': The JETTO version number
          * 'userid': The user ID of the JETTO executable

        * 'parameters': The values of each parameter in the template lookup. Fixed parameter values are given directly;
          parameters being scanned over have a custom serialisation
        * 'processors': The number of processors configured for the JETTO run
        * 'walltime': The configured walltime for a PROMINENCE run
        * 'start_time': The JETTO simulation start time
        * 'end_time': The JETTO simulation end time
        * 'esco_timesteps': The number of time steps for the ESCO equilibrium
        * 'profile_timesteps': The number of timesteps for the output profile

        :return: The serialisation
        :rtype: str
        """
        return json.dumps({
            "files": {str(name): str(path) for name, path in self._files.items()},
            "loadmodule": self._loadmodule,
            "parameters": self._parameters,
            "processors": self._processors,
            "walltime": self.walltime,
            "start_time": self._time_config.start_time,
            "end_time": self._time_config.end_time,
            'esco_timesteps': self._time_config.n_esco_times,
            'profile_timesteps': self._time_config.n_output_profile_times
        }, default=_CoupledScan.to_json, indent=4)

    def export(self, path: Union[str, os.PathLike], rundir: str = '') -> List[str]:
        """Export the configuration

        Creates and writes the set of files associated with the JETTO run configuration. The template files on which the
        configuration was based are written to a directory '_template' within the export directory. For each point in
        the configuration, a separate 'point_nnn' directory is created, where 'nnn' is an incrementing counter. Each
        point directory contains the updated template files, batchfile and serialisation for that point.

        If there is only a single point in the configuration (i.e. no scans are being performed) then the point
        directory is omitted and the configuration files are written directly into the export directory. If there are
        scans, a separate scan serialisation file is written in the export directory, in addition to the serialisations
        for the individual points within the point directories.

        The function returns a list of absolute paths to each of the point run directories.

        :param path: Path to the export directory. If it doesn't exist, it will be created.
        :type path: Union[str, os.PathLike]
        :param rundir: Relative path to the run directory from the run root
        :type rundir: str
        :return: List of run directories
        :rtype: List[str]
        """
        export_dir = Path(path).expanduser().resolve()
        export_dir.mkdir(parents=True, exist_ok=True)
        rundir_path = Path(rundir)

        self._export_template(export_dir)

        points = self._points(export_dir.name)
        point_paths = []

        if len(points) > 1:
            self._export_serialisation(export_dir)
            self._export_labels(export_dir, name=rundir, catalogue_id=self._template.catalogue_id)

            for i, point in enumerate(points):
                point_dir_name = 'point_{:03d}'.format(i)
                point_path = export_dir.joinpath(point_dir_name)
                if not point_path.is_dir():
                    point_path.mkdir()

                self._export_point(point_path, point, rundir_path.joinpath(point_dir_name),
                                   scan_params=[param for param, value in self._parameters.items()
                                                if isinstance(value, Scan)])

                point_paths.append(point_path)
        else:
            [point] = points
            self._export_point(export_dir, point, rundir_path)
            point_paths.append(export_dir)

        return [str(path.absolute()) for path in point_paths]

    def _export_template(self, export_dir: Path):
        """Export the configuration's template files

        Creates a directory '_template' within the export directory (if it doesn't already exist), and writes the
        configuration's template jset, namelist and lookup files to the _template directory. If the template also
        contains a SANCO namelist file, it is also written to the template directory.

        :param export_dir: Path to the export directory
        :type export_dir: pathlib.Path
        """
        template_path = export_dir.joinpath('_template')
        if not template_path.exists():
            template_path.mkdir()

        jset_path = template_path.joinpath('jetto.jset')
        with open(jset_path, 'w') as f:
            f.write(str(self._template.jset))

        namelist_path = template_path.joinpath('jetto.in')
        with open(namelist_path, 'w') as f:
            f.write(str(self._template.namelist))

        lookup_path = template_path.joinpath('lookup.json')
        with open(lookup_path, 'w') as f:
            f.write(jetto_tools.lookup.to_json(self._template.lookup))

        if self._sanco_enabled():
            sanco_namelist_path = template_path.joinpath('jetto.sin')
            jetto_tools.namelist.write(self._template.sanco_namelist, sanco_namelist_path)

        self._export_extra_files(template_path, self._template.extra_files, symlink_to_template=None)

    def _export_serialisation(self, export_dir: Path):
        """Export the configuration's serialisation

        Writes the configuration's serialisation to a file 'serialisation.json', within the export directory.

        :param export_dir: Path to the export directory
        :type export_dir: pathlib.Path
        """
        serialisation_path = export_dir.joinpath('serialisation.json')
        with open(serialisation_path, 'w') as f:
            f.write(self.serialise())

    def _export_point(self, point_path: Path, point: _Point, rundir=Path(''), scan_params=None):
        """Export a configuration point

        Applies the contents of the point to the template, and writes the updated jset and namelist to the point's
        export directory. Also copies the configured exfile to the export directory. If SANCO is enabled, the SANCO
        namelist will also be exported, again with its parameters updated. Any extra files will be copied verbatim to
        the export directory.

        A ``_template`` directory is created in the point directory (unless there is only a single point in the scan)
        which symlinks to the top-level ``_template`` directory in the export directory. If there is only one point
        in the scan, then the export directory and the point directory are the same, and so no symlink is needed.

        :param point_path: Path to the export directory for the point
        :type point_path: pathlib.Path
        :param rundir: Relative path to the point run directory, from the run root
        :type rundir: Path
        :point: Point to export
        :type point: _Point
        """
        now = datetime.datetime.now()

        point_template_dir = point_path.joinpath('_template')
        # If we're not doing scans, the template directory will already exist in the export directory
        if not point_template_dir.exists():
            upper_template_dir = point_path.parents[0].joinpath('_template')
            os.symlink(upper_template_dir, point_template_dir)

        self._export_jset(point_path, point, now, rundir)
        self._export_namelist(point_path, point, now, restart=self._template.jset.restart, namelist_type='jetto')
        if self._sanco_enabled():
            self._export_namelist(point_path, point, now, namelist_type='sanco')
        self._export_extra_files(point_path, point.files, symlink_to_template=None)
        self._export_labels(point_path, point.name, index=point.index,
                            catalogue_id=self._template.catalogue_id, scan_params=scan_params, point=point)

        # doing this after _export_extra_files(...) will cause the
        # file to be replaced, which isn't very nice, but hopefully
        # does the right thing!
        if self._graybeamfile_updated:
            self._export_gray_files(point_path, point, now)

        if self.driver == Driver.IMAS and self.read_from_ids and self._input_ids_source_updated:
            self._export_input_ids_files(point_path)

        serialisation_path = point_path.joinpath('serialisation.json')
        with open(serialisation_path, 'w') as f:
            f.write(point.serialise())

    def _export_jset(self, point_dir: Path, point: _Point, now: datetime.datetime, rundir: Path):
        """Export a point's JSET

        Makes a copy of the original template JSET, and applies the configuration point updates to it. Also sets the
        creation name, date, time and version in the JSET header. Once the JSET has been updated, it is written to the
        file 'jetto.jset' within the exported point directory.

        :param path: Point export directory
        :type path: pathlib.Path
        :param point: Point to export
        :type point: _Point
        :param now: Current datetime
        :type now: datetime.datetime
        :param rundir: Relative path to the point run directory, from the run root
        :type rundir: Path
        """
        jset = deepcopy(self._template.jset)
        jset.collapse_all_arrays()

        jset_path = point_dir.joinpath('jetto.jset')

        jset.cname = str(jset_path)
        jset.cdate = now.date()
        jset.ctime = now.time()
        jset.version = self._combined_version()

        jset.binary = point.loadmodule['binary']
        jset.userid = point.loadmodule['userid']
        jset.processors = point.processors
        jset.walltime = point.walltime
        jset.rundir = str(rundir)

        jset.read_ids = self._read_from_ids
        jset.write_ids = self._create_output_ids
        if self._input_ids_source_updated:
            jset.input_ids_source = self._input_ids_source

        original_time_config = jset.get_time_config()
        if original_time_config != point.time_config:
            jset.set_time_config(point.time_config)
            if point.time_config.start_time != original_time_config.start_time or \
                    point.time_config.end_time != original_time_config.end_time:
                jset.reset_fixed_output_profiles_times()

        if self._exfile_updated:
            jset.exfile = point.exfile
        if self._graybeamfile_updated:
            jset.make_graybeamfile_private(point.get_private_graybeam_filename(now))

        for param, value in point.parameters.items():
            if _is_gray_parameter(param):
                continue

            jset_ids = jetto_tools.template.Template.extract_jset_ids(self._template.lookup[param])
            for jset_id in jset_ids:
                if jset_id is not None:
                    jset[jset_id] = value
            jset_id = self._template.lookup[param]['jset_id']
            if jset_id is None:
                field = self._template.lookup[param]['nml_id']['field']
                if field in jset.extras:
                    extras = jset.extras
                else:
                    extras = jset.sanco_extras

                active = extras[field].active
                if self._template.lookup[param]['dimension'] == 'scalar':
                    extras[field] = jetto_tools.jset.ExtraNamelistItem(value, None, active=active)
                else:
                    extras[field] = jetto_tools.jset.ExtraNamelistItem(value, 1, active=active)

        jset.expand_all_arrays()
        with open(jset_path, 'w') as f:
            f.write(str(jset))

    def _export_namelist(self, path: Path, point: _Point, now: datetime.datetime, restart=False, namelist_type='jetto'):
        """Export a point's JETTO or SANCO namelist

        Makes a copy of the original template namelist, and applies the configuration point updates to it. Also sets the
        date and time and jetto-pythontools version in the namelist header. Other header fields associated with JAMS
        git repository information are set to 'n/a'. Once the namelist has been updated, it is written to the file
        'jetto.in' or 'jetto.sin' within the exported point directory.

        :param path: Point export directory
        :type path: pathlib.Path
        :param point: Point to export
        :type point: _Point
        :param now: Current datetime
        :type now: datetime.datetime
        :param restart: Flag indicating if this is a restart case
        :type restart: bool
        :param namelist_type: Namelist to export ('jetto' or 'sanco')
        :type namelist_type: str
        """
        if namelist_type == 'jetto':
            namelist = deepcopy(self._template.namelist)
            namelist_path = path.joinpath('jetto.in')
        else:
            namelist = deepcopy(self._template.sanco_namelist)
            namelist_path = path.joinpath('jetto.sin')

        namelist.date = now.date()
        namelist.time = now.time()
        namelist.version = __version__

        for prop in ('repo', 'tag', 'branch', 'sha', 'status'):
            setattr(namelist, prop, 'n/a')

        for param, value in point.parameters.items():
            if _is_gray_parameter(param):
                continue

            if 'nml_id' not in self._template.lookup[param]:
                continue

            namelist_id, field = self._template.lookup[param]['nml_id']['namelist'], \
                                 self._template.lookup[param]['nml_id']['field']

            if field in self._template.jset.extras:
                active = self._template.jset.extras[field].active
            elif field in self._template.jset.sanco_extras:
                active = self._template.jset.sanco_extras[field].active
            else:
                active = True

            if active in (None, True) and namelist.exists(namelist_id, field):
                if self._template.lookup[param]['dimension'] == 'vector':
                    namelist.set_array(namelist_id, field, value)
                else:
                    namelist.set_field(namelist_id, field, value, distribute=True)

        if namelist_type == 'jetto':
            namelist.set_field('NLIST1', 'IRESTR', {True: 1, False: 0}[restart])
            RunConfig._apply_namelist_time_ranges(namelist, point, self._template.jset)

        with open(namelist_path, 'w') as f:
            f.write(str(namelist))

    @classmethod
    def _apply_namelist_time_ranges(cls, namelist, point, jset):
        """Set time ranges in the namelist

        Sets the ``TBEG``, ``TMAX``, ``TIMEQU``, ``TPRINT`` and ``NTPR`` fields, based on the configured start and end
        times and number of ESCO/profile timesteps.

        Only supports ESCO Interval time values, not Discrete. An exception will be raised if the template is configured
        for Discrete ESCO time values.

        :param namelist: Namelist
        :type namelist: jetto_tools.namelist.Namelist
        :param point: Point to export
        :type point: _Point
        :param jset: Template JSET
        :type jset: jetto_tools.jset.JSET
        :raise: RunConfigError if ESCO time values in the JSET are not set to 'Interval'
        """
        tc = point.time_config
        original_tc = jset.get_time_config()

        namelist.set_field('NLIST1', 'TBEG', tc.start_time)
        namelist.set_field('NLIST1', 'TMAX', tc.end_time)

        # Set the ESCO equilibrium times
        if tc != original_tc and jset['EquilibriumPanel.source'] == 'ESCO':
            if jset['EquilEscoRefPanel.tvalueOption'] == 'Interval':
                # Set the timestep interval to a magic number if there is only one timestep
                # (Reproduces JAMS behaviour: see EquilEscoRefPanel.java & TimeIntervalSetDialog.java)
                if tc.n_esco_times == 1:
                    interval = float(1.0e30)
                else:
                    interval = (tc.end_time - tc.start_time) / (tc.n_esco_times - 1)
                namelist.set_array('INESCO', 'TIMEQU', [tc.start_time, tc.end_time, interval])
            else:
                raise RunConfigError('Only templates where the ESCO time value option is "Interval" are supported. '
                                     'This template uses "Discrete"')

        # Set the output profile times
        if jset['OutputStdPanel.selectProfiles'] is True:
            if tc.start_time != original_tc.start_time or tc.end_time != original_tc.end_time:
                times = list(linspace(start=tc.start_time, stop=tc.end_time, num=tc.n_output_profile_times))[1:-1]
                namelist.set_array('NLIST2', 'TPRINT', times)
                namelist.set_field('NLIST2', 'NTPR', len(times))
        else:
            namelist.set_field('NLIST2', 'NTPR', 0)

    def _export_input_ids_files(self, path: os.PathLike):
        """Export the point's input IDS files

        :param path: Point export directory
        :type path: os.PathLike
        :raise: RunConfigError if the configuration doesn't use the IMAS driver; has no input IDS files; or the input
                IDS source has not been modified with respect to the template
        """
        if self.driver == Driver.Std:
            raise RunConfigError('Cannot export input IDS files for cases using the standard driver')

        if self.read_from_ids is False:
            raise RunConfigError('Cannot export input IDS files for cases not configured for IDS input')

        if self._input_ids_source_updated is False:
            raise RunConfigError('Cannot export input IDS files: none have been provided')

        if shutil.which('ids_copy') is None:
            raise RunConfigError('Cannot export input IDS file: ids_cp command not found on PATH')

        imasdb_target = self.ids_in
        imasdb = self._input_ids_source
        args = [
            'ids_copy',
            f'-m{imasdb_target.machine}',
            f'-s{imasdb_target.shot}',
            f'-r{imasdb_target.run}',
            imasdb.user,
            imasdb.machine,
            f'{imasdb.shot}',
            f'{imasdb.run}',
            str(path)
        ]
        completed_process = subprocess.run(args)
        if completed_process.returncode != 0:
            raise RunConfigError(f'Failed to export IDS input files: the call to ids_copy command '
                                 f'({" ".join(args)}) failed with returncode {completed_process.returncode}')

    def _export_extra_files(self, path: os.PathLike, extra_files: Dict[str, os.PathLike], symlink_to_template: Optional[os.PathLike] = None):
        """Export the point's extra files

        For each extra file in the configuration, copy that file to the given directory. If the extra file belongs in
        the root of the directory, then just copy it. If it is contained inside one or more other directories under the
        root, and a template directory is provided, symlink the file's parent directory to the coresponding directory
        in the template.

        Input IDS files are only exported if no modification has been made to the input IDS source in the configuration.

        :param path: Point export directory
        :type path: os.PathLike
        :param extra_files: Extra files to export
        :type extra_files: Dict[str,os.PathLike]
        :param symlink_to_template: If not None, symlink any exttra files which live in directories back to the template
        :type  symlink_to_template: Optional[os.PathLike]
        :raise: RunConfigError if any of the extra files does not exist
        """
        extra_files = {Path(k): Path(v) for k, v in extra_files.items()}

        if self._input_ids_source_updated:
            extra_files = {k: v for k, v in extra_files.items() if not str(k).startswith('imasdb')}

        for rel_path, src_path in extra_files.items():
            if rel_path.parent != Path('.') and symlink_to_template is not None:
                dest_path = path / rel_path.parent
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                if not dest_path.is_symlink():
                    rel_link = os.path.relpath(symlink_to_template / rel_path.parent, dest_path.parent)
                    dest_path.symlink_to(rel_link)
            else:
                dest_path = path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                if src_path.is_file():
                    if not dest_path.is_file():
                        copyfile(src_path, dest_path)
                    elif not src_path.samefile(dest_path):
                        copyfile(src_path, dest_path)
                else:
                    raise RunConfigError(f"Cannot find run input file at '{src_path}'")

    def _export_gray_files(self, path: Path, point: _Point, now: datetime.datetime) -> None:
        params: Dict[str, float] = {}
        for param, value in point.parameters.items():
            gray_param = _split_gray_parameter(param)
            if gray_param:
                params[gray_param] = value

        contents = self._template.gray.with_params(
            params
        ).serialise_graybeam_data()

        private_path = point.get_private_graybeam_filename(now)
        # ensure these exist
        private_path.parent.mkdir(parents=True, exist_ok=True)

        for name in (path / 'graybeam.data', private_path):
            with open(name, 'w') as fd:
                fd.write(contents)

    def _export_labels(self, path: Path, name: str, catalogue_id: str = None, index: int = None, point: _Point = None, scan_params: List = None):
        """Export a labels file to disk

        Creates a file named ``labels.yaml`` in the point directory

        :param path: Path to the point directory
        :type path: pathlib.Path
        :param name: Label to apply to the point
        :type name: str
        :param index: Index of the scan point
        :type index: int
        """
        labels = {
            'scan-label': name,
            'template': catalogue_id
        }

        if index is not None:
            labels['point-index'] = index

        if scan_params is not None:
            for param in scan_params:
                labels[f'scan-param-{param}'] = point.parameters[param]

        with open(path / 'labels.yaml', 'w') as f:
            yaml.dump(labels, f)

    def _sanco_enabled(self) -> bool:
        """Check if use of SANCO is enabled in the template

        SANCO is enabled if impurities are enabled and SANCO is set as the source, in the template JSET

        :return: SANCO enabled status
        :rtype: bool
        """
        jset = self._template.jset

        return jset.impurities and jset.sanco

    def _points(self, name: str) -> List[_Point]:
        """Generate the points in the configuration

        If the configuration contains one or more scanned parameters, this function generates a point for each element
        of the cartesian product of the scans. Otherwise, it generates only a single point. If the configuration
        contains coupled scans as well as regular scans, this function generates a point for each element of the
        cartesian product of the regular scans and cartesian product of the permutations of coupled scans.

        :return: List of points in the configuration
        :rtype: List[_Point]
        """
        scans = {k: v for k, v in self._scans().items() if not isinstance(v, _CoupledScan)}
        scan_parameters = scans.keys()
        scan_values = scans.values()

        coupled_scans = self._coupled_scans()

        parameter_updates = []

        if coupled_scans:
            c_scan_points = []

            seen = []
            for param, c_scan in coupled_scans.items():
                if param in seen:
                    continue
                current = [param]
                current.extend(c_scan.params())
                seen.extend(current)
                d = {k: v for k, v in zip(current, [coupled_scans[p] for p in current])}
                pivot_d = [dict(zip(d.keys(), _)) for _ in zip(*d.values())]
                c_scan_points.append(pivot_d)

            if scan_parameters:
                for scan_point in itertools.product(*scan_values):
                    scan_points = dict(zip(scan_parameters, scan_point))

                    for couple_point in itertools.product(*c_scan_points):
                        for d in couple_point:
                            scan_points.update(d)

                        parameter_updates.append(dict(scan_points))
            else:
                for couple_point in itertools.product(*c_scan_points):
                    scan_points = dict(zip(coupled_scans.keys(), couple_point))

                    for d in couple_point:
                        scan_points.update(d)

                    parameter_updates.append(scan_points)
        else:
            if scan_parameters:
                for point in itertools.product(*scan_values):
                    parameter_updates.append(dict(zip(scan_parameters, point)))

        # make sure we generate at least one vacuous change
        if not parameter_updates:
            parameter_updates.append({})

        points = []
        for i, updates in enumerate(parameter_updates):
            parameters = dict(self._parameters)
            parameters.update(updates)
            points.append(self._Point(
                name=name, index=i,
                files=self._files, loadmodule=self._loadmodule,
                parameters=parameters, processors=self._processors,
                walltime=self.walltime,
                time_config=dataclasses.replace(self._time_config)
            ))

        return points

    def create_coupled_scan(self, couple: Dict[str, Scan]):
        """Create a coupled scan of two or more parameters

        A coupled scan consists of Scans over two or more parameters being coupled together. A coupled scan must be
        initialised with a dictionary, where the keys are the parameters being scanned over, and the values are Scan
        objects containing the values for each scan. Each of the scans must be of the same length.

        Trying to create a coupled scan with a parameter which is in an existing coupled scan will raise an exception.

        Example:
            create_coupled_scan({"param_a": Scan([p0, p1, p2]), "param_b": Scan([p0, p1, p2])})

        :param couple: Mapping of parameter names to Scans
        :type couple: Dictionary
        :raise: ScanError if any of the individual Scan objects are invalid
        :raise: RunConfigError if any of the parameters do not exist in the lookup, or if any of the scans contains a
        incompatible with the parameter's value specified in the lookup
        """
        if len(couple) <= 1:
            raise ScanError('Coupled scans must have at least two parameters')

        first_param, first_scan = next(iter(couple.items()))
        scan_length = len(first_scan)

        for param in couple:
            if param not in self:
                raise RunConfigError(f'Parameter {param} not found in template lookup')

            value = couple[param]
            if not isinstance(value, Scan):
                raise RunConfigError(f'Parameter {param} has value which is not a Scan object')
            if len(value) != scan_length:
                raise ScanError(f"Parameter {param}'s scan is a different length to other scans coupled to it")

        # Since all scans are the same length, validating the first is equivalent to validating all
        self._validate_scan(first_param, first_scan)

        current_coupled_params = self._coupled_scans()
        for param in couple:
            if param in current_coupled_params:
                raise RunConfigError(f'Parameter {param} is already a member of a coupled scan')

        for param in couple:
            self._parameters[param] = _CoupledScan(list(iter(self._convert_parameter(param, couple[param]))),
                                                   [p for p in couple if p != param])

    def __getitem__(self, param: str) -> Union[None, int, float, Scan]:
        """Get the value of a configuration parameter

        Checks to see if the parameter is editable by searching the lookup table, and then returns its value

        :param param: Parameter name
        :type param: str
        :return: Value of the parameter
        :rtype: Union[None, int, float, Scan]
        :raise: RunConfigError if the parameter does not exist in the lookup
        """
        if param not in self:
            raise RunConfigError("Parameter {} not found in template lookup".format(param))

        return self._parameters[param]

    def __setitem__(self, param: str, value: Union[int, float, Scan, List]):
        """Set the value of a configuration parameter

        Configuration parameters can be set if they are present in the lookup table. Parameters can be set to values
        compatible with the type given in the lookup mapping. Where possible, type conversions are performed e.g. if an
        integer is set to a floating point value, the conversion to int is performed if it can be.

        :param param: Parameter name
        :type param: str
        :param value: New value of the parameter
        :type value: Union[int, float, Scan, List]
        :raise: RunConfigError if the parameter does not exist in the lookup, or if the supplied type cannot be
                converted to the correct type
        """
        if param not in self:
            raise RunConfigError("Parameter {} not found in template lookup".format(param))

        if isinstance(self._parameters.get(param), _CoupledScan):
            raise RunConfigError(f'Parameter {param} is a member of a coupled scan')

        if isinstance(value, Scan):
            self._validate_scan(param, value)

        self._parameters[param] = self._convert_parameter(param, value)

        # done at the end in case some exception is thrown above
        if _is_gray_parameter(param):
            self._graybeamfile_updated = True

    def __iter__(self) -> Iterator:
        """Iterate over the configuration

        Iterates over the identifiers of the configuration's parameters

        :return: Parameter iterator
        :rtype: Iterator
        """
        return iter(self._parameters)

    def __contains__(self, param: str) -> bool:
        """Check if a parameter exists in the configuration

        :param param: Parameter name
        :type param: str
        :return: True if the parameter exists in the configuration; otherwise False
        :rtype: bool
        """
        gray_param = _split_gray_parameter(param)
        if gray_param:
            return gray_param in self._template.gray

        return param in self._parameters

    def _npoints(self) -> int:
        """Get the number of points in the configuration

        The call to ``_points`` requires a name (since changes brought in with adding support for scanning GRAY
        parameters), so an empty string is provided. Since this function only gets the number of points from a
        temporarily constructed list of points, the blank name has no effect.

        :return: Number of points in the configuration
        :rtype: int
        """
        return len(self._points(''))

    def _coupled_scans(self) -> Dict[str, _CoupledScan]:
        """Get the CoupledScans in the configuration

        Extracts the configuration parameters which are Scans coupled to other parameters

        :return: Coupled Scans
        :rtype: Dict[str, _CoupledScan]
        """
        return {k: v for k, v in self._parameters.items() if isinstance(v, _CoupledScan)}

    def _scans(self) -> Dict[str, Scan]:
        """Get the scans in the configuration

        Extracts the configuration parameters which are being scanned over

        :return: Scanned parameters
        :rtype: Dict[str, Scan]
        """
        return {k: v for k, v in self._parameters.items() if isinstance(v, Scan)}

    def _current_scan_dimensions(self) -> int:
        """Get the number of scan dimensions in the configuration

        Return a count of the scan dimensions, counting each coupled scan as a single dimension

        :return: Count of scan dimensions
        :rtype: int
        """
        return len(self._group_scans(self._scans()))

    @classmethod
    def _group_scans(cls, scans: List[Scan]) -> List[Tuple[Scan]]:
        """Group scans by coupling

        Non-coupled scans are returned as a tuple of one element; coupled scans are returned in the same tuple

        :param scans: Scans
        :type scans: List[Scan]
        :return: Grouped scans
        :rtype: List[Tuple[Scan]]
        """
        coupled_scans = {k: v for k, v in scans.items() if isinstance(v, _CoupledScan)}
        non_coupled_scans = {k: scans[k] for k in set(scans) - set(coupled_scans)}

        groups = [(scan, ) for scan in non_coupled_scans]
        for scan in coupled_scans:
            if not any(scan in group for group in groups):
                groups.append((scan, *coupled_scans[scan].params()))

        return groups

    def _validate_scan(self, param: str, scan: Scan):
        """Check if a scan is valid

        Performs the following checks on the scan:
         - That the scan is not longer than the maximum permitted scan length
         - That the addition of the scan would not exceed the maximum number of scan dimensions in the configuration
         - That the addition of the scan would not exceed the maximum number of points in the configuration

         :param param: Parameter name
         :type param: str
         :param scan: Scan to validate
         :type scan: Scan
         :raise: RunConfigError if any of the checks fail
         """
        if len(scan) > self._SCAN_DIMENSION_MAX_LENGTH:
            raise RunConfigError(f'Scan length cannot be longer than {self._SCAN_DIMENSION_MAX_LENGTH} points')

        if self._current_scan_dimensions() == self._SCAN_MAX_DIMENSIONS:
            raise RunConfigError(f'Cannot perform scans over more than {self._SCAN_MAX_DIMENSIONS} dimensions')

        if self._peek_scan_points(param, scan) > self._SCAN_MAX_POINTS:
            raise RunConfigError(f'Total number of scan points cannot exceed {self._SCAN_MAX_POINTS}')

    def _peek_scan_points(self, param: str, scan: Scan) -> int:
        """Compute the potential number of scan points

        Works out how many points would be in the configuration if the given scan were added

        :param param: Parameter name
        :type param: str
        :param scan: The scan we are proposing to add
        :type scan: Scan
        :return: The number of points
        :rtype: int
        """
        scans = self._scans()
        scans.update({param: scan})

        groups = self._group_scans(scans)
        lengths = [len(scans[group[0]]) for group in groups]

        return reduce(mul, lengths, 1)

    def _convert_parameter(self, param: str, value):
        """Check and convert a parameter to the appropriate type

        Given the parameter name, this function looks up the destination type ('int' or 'float') in the configuration
        lookup. It also looks up the destination dimension ('scalar' or 'vector'). It then checks to see if the
        parameter is of the correct type (or is a Scan containing the correct types), or if it can be safely converted
        (e.g. from an int to a float). If so, the converted parameter is returned.

        :param param: Parameter name
        :type param: str
        :param value: Parameter value
        :return: The converted value
        """
        gray_param = _split_gray_parameter(param)
        if gray_param:
            # GRAY parameters are all floats at the moment
            destination_type, destination_dimension = (
                self._template.gray.get_param_type_dimension(gray_param)
            )
        else:
            destination_type = self._template.lookup[param]['type']
            destination_dimension = self._template.lookup[param]['dimension']

        if isinstance(value, Scan):
            return Scan([RunConfig._convert_value(p, destination_type, destination_dimension) for p in value])
        else:
            return RunConfig._convert_value(value, destination_type, destination_dimension)

    @classmethod
    def _initial_template_files(cls, template: jetto_tools.template.Template) -> Dict[str, str]:
        """Get the initial set of extra files from the template

        Takes the ``template.extra_files``. If the extra files don't contain the ex-file, uses the one from the
        template JSET

        :param template: Template
        :type template: jetto_tools.template.Template
        :return: Initial set of files
        :rtype: Dict[str, str]
        """
        files = template.extra_files.copy()
        if Path('jetto.ex') not in files:
            files[Path('jetto.ex')] = template.jset.exfile

        return files

    @classmethod
    def _initial_template_value(cls, param: Dict, jset: jetto_tools.template.Template):
        """Get the initial value of a parameter from a template

        If the parameter is regular (i.e. not an extra namelist parameter), then the value is taken directly from the
        corresponding setting in the template JSET. If it is in one of the extra namelists, the value is taken from
        the extra namelist in the template JSET. If necessary, the value from the JSET is modified to adhere to the
        type specified in the lookup file (e.g. if the ``type`` in the lookup file is specified as ``real``, but the
        value in the template JSET is an integer, the JSET value is converted to a float). This type sanitisation does
        not apply to the extra namelist parameters, which are already strongly typed.

        :param param: Parameter specification from lookup
        :type param: Dict
        :param jset: Template JSET
        :type jset: jetto_tools.jset.JSET
        :return: The value
        :rtype: int, float, or list
        """
        jset_id = param['jset_id']
        dimension = param['dimension']
        type_ = param['type']

        if jset_id is not None:
            value = jset[jset_id]
        else:
            field = param['nml_id']['field']
            if field in jset.extras:
                extras = jset.extras
            else:
                extras = jset.sanco_extras

            if dimension == 'scalar' and extras[field].is_scalar():
                value = extras[field][None]
            elif dimension == 'vector' and not extras[field].is_scalar():
                value = extras[field].as_list()
            else:
                raise RunConfigError(f'Extra namelist item {field} not of expected dimension')
        return cls._convert_value(value, type_, dimension)

    @classmethod
    def _convert_value(cls, value, destination_type: str, destination_dimension='scalar') -> Union[int, float, List[int], List[float], str]:
        """Convert a value to the destination type

        Destination type is one of the values supported by the run configuration i.e. ints or floats, or lists of ints
        or floats

        :param value: Value to convert
        :type value: int, float or list thereof
        :param destination_type: Destination type ('int' or 'float')
        :type destination_type: str
        :param destination_dimension: Destination dimension ('scalar' or 'vector')
        :return: Converted value
        :rtype: int, float, or list
        :raise: RunConfigError if the value is not of numeric type, or it cannot be converted successfully
        """
        if destination_dimension == 'vector':
            if destination_type == 'int':
                return [cls._convert_value_to_int(v) for v in value]
            else:
                return [cls._convert_value_to_float(v) for v in value]
        else:
            if destination_type == 'int':
                return cls._convert_value_to_int(value)
            elif destination_type == 'str':
                return value
            else:
                return cls._convert_value_to_float(value)

    @classmethod
    def _convert_value_to_int(cls, value: Union[int, float]):
        """Convert a value to an integer

        Converts a numeric value to integer, if it is possible. Ints convert trivially, floats convert if the float
        contains a whole number.

        :param value: Value to convert
        :type value: Union[int, float]
        :return: Converted value
        :rtype: int
        :raise: RunConfigError if value is a non-whole number float
        """
        if isinstance(value, float) and value.is_integer():
            return int(value)
        elif isinstance(value, int):
            return value
        else:
            raise RunConfigError(f'Unable to convert value {value} to integer')

    @classmethod
    def _convert_value_to_float(cls, value: Union[int, float]):
        """Convert a value to a float

        Converts the numeric value to a float

        :param value: Value to convert
        :type value: Union[int, float]
        :return: Converted value
        :rtype: float
        :raise: RunConfigError if the value cannot be converted to a float
        """
        if not _utils.is_numeric(value):
            raise RunConfigError(f'Unable to convert value {value} to float')

        return float(value)

    def _combined_version(self) -> str:
        """Get a combined JAMS/Python version string

        Appends Python API to the JAMS version string

        :return: Combined version
        :rtype: str
        """
        return ' + '.join([self._template.jset.version, 'Python API', __version__])
