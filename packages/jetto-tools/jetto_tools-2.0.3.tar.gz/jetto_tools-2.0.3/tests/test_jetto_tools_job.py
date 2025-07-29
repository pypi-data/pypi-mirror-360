import json
import dataclasses
import numpy as np
import pytest
import unittest.mock as mock
import os.path
import stat
import sys
import re
import tarfile
import filecmp
from pathlib import Path
import random
import warnings
import shlex

import docker
import prominence
import yaml
from prominence.exceptions import ConnectionError, AuthenticationError, FileUploadError, WorkflowCreationError

import jetto_tools.job as job
import jetto_tools.config
from jetto_tools.common import Driver, IMASDB


@pytest.fixture()
def manager():
    return job.JobManager()


@pytest.fixture()
def jintrac_source_dir(tmp_path):
    dir = tmp_path / 'jintrac'
    dir.mkdir(exist_ok=True)

    return dir


@pytest.fixture()
def jetto_source_dir(jintrac_source_dir):
    dir = jintrac_source_dir / 'jetto'
    dir.mkdir(exist_ok=True)

    return dir


@pytest.fixture()
def jetto_scripts_dir(jetto_source_dir):
    dir = jetto_source_dir / 'sh'
    dir.mkdir(exist_ok=True)

    return dir


@pytest.fixture()
def jetto_run_script(jetto_scripts_dir):
    script_path = jetto_scripts_dir / 'rjettov'
    script_path.write_text('foo')
    mode = script_path.stat().st_mode
    script_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return script_path


@pytest.fixture()
def jetto_utils_script(jetto_scripts_dir):
    script_path = jetto_scripts_dir / 'utils'
    script_path.write_text('bar')
    mode = script_path.stat().st_mode
    script_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return script_path


@pytest.fixture()
def jetto_sources(jetto_run_script, jetto_utils_script):
    return jetto_run_script, jetto_utils_script


@pytest.fixture()
def users_home(tmp_path):
    dir = tmp_path / 'home'
    dir.mkdir()

    return dir


@pytest.fixture()
def runs_home(users_home):
    dir = users_home / 'user'
    dir.mkdir(exist_ok=True)

    return dir


@pytest.fixture()
def run_root(runs_home):
    dir = runs_home / 'jetto/runs'
    dir.mkdir(parents=True)

    return dir


@pytest.fixture()
def rundir(run_root):
    return 'runtestdata'


@pytest.fixture()
def rundir_path(rundir):
    return Path(rundir)


@pytest.fixture()
def run_path(run_root, rundir_path):
    d = run_root / rundir_path

    return d


@pytest.fixture()
def tar_extract_dir(tmp_path):
    return tmp_path / 'extract'


@pytest.fixture
def mock_files(run_root):
    """Create three dummy files in the run directory"""
    def _fixture(_self, run_dir):
        run_path = run_root / run_dir
        if not run_path.is_dir():
            run_path.mkdir(parents=True)

        for file in ('jetto.jset', 'jetto.in', 'serialisation.json'):
            (run_path / file).write_text(file)

        return mock.DEFAULT

    return _fixture


@pytest.fixture()
def mock_config(run_root, rundir, mock_files):
    """Pre-built config in which userid = 'user' and binary = 'v060619'"""
    m = mock.MagicMock(spec=jetto_tools.config.RunConfig)
    m.userid = 'user'
    m.binary = 'v060619'
    m.processors = 2
    m.walltime = 2
    m.diver = Driver.Std
    m.start_time = 0.0
    m.end_time = 10.0
    m.ids_in = IMASDB(0,0,0,0)
    m.read_from_ids = False
    m.ids_out = IMASDB(0,0,0,0)
    m.create_output_ids = False
    m.export.side_effect = mock_files
    m.export.return_value = [str(run_root / rundir)]
    m._npoints.return_value = 1

    return m


@pytest.fixture()
def jetto_exe(users_home):
    jetto_exe_dir = users_home / 'user/jetto/bin/linux'
    jetto_exe_dir.mkdir(parents=True, exist_ok=True)
    jetto_exe_path = jetto_exe_dir / 'v060619_mpi_64'
    jetto_exe_path.write_text('')

    return jetto_exe_path


@pytest.fixture()
def jintrac_env(monkeypatch, users_home, runs_home, jetto_exe):
    monkeypatch.setenv('USERS_HOME', str(users_home))
    monkeypatch.setenv('RUNS_HOME', str(runs_home))

    return monkeypatch


@pytest.fixture()
def jetto_exe_serial(users_home):
    jetto_exe_dir = users_home / 'user/jetto/bin/linux'
    jetto_exe_dir.mkdir(parents=True, exist_ok=True)
    jetto_exe_path = jetto_exe_dir / 'v060619_64'
    jetto_exe_path.write_text('')

    return jetto_exe_path


@pytest.fixture()
def jintrac_env_serial(monkeypatch, users_home, runs_home, jetto_exe_serial):
    monkeypatch.setenv('USERS_HOME', str(users_home))
    monkeypatch.setenv('RUNS_HOME', str(runs_home))

    return monkeypatch


@pytest.fixture(autouse=True)
def mock_semver():
    semver = type(sys)('semver')

    semver.higher = mock.MagicMock()
    semver.higher.return_value = ''

    semver.is_valid = mock.MagicMock()
    semver.is_valid.return_value = True

    semver.Version = mock.MagicMock()
    semver.Version.compare = mock.MagicMock()
    semver.Version.compare.return_value = 0

    sys.modules['semver'] = semver

    yield semver


class TestGetProvenance:
    @pytest.fixture
    def customise_fake_jetto_process(self, jetto_source_dir, jetto_exe, fake_process):
        def _customise_fake_jetto_process(jetto_exe_path=str(jetto_exe),
                                         jetto_source_path=str(jetto_source_dir),
                                         jetto_returncode=0,
                                         jetto_stdout=None,
                                         jetto_version=None):
            if jetto_stdout is None:
                stdout = (f' JETTO  GIT repository : {jetto_source_path}\n'
                           ' JETTO  SHA1-key       : f425ed9c4cb8b20c6698e3bcb5a8faf8bf61dc55\n')
                if jetto_version is not None:
                    stdout = stdout + f' JETTO  Version       : {jetto_version}\n'
            else:
                stdout = jetto_stdout

            fake_process.register_subprocess([jetto_exe_path, fake_process.any()],
                                             stdout=[stdout],
                                             returncode=jetto_returncode)

            return fake_process

        return _customise_fake_jetto_process

    @pytest.fixture
    def fake_jetto_process(self, customise_fake_jetto_process):
        return customise_fake_jetto_process()

    def test_raises_if_jetto_executable_does_not_exist(self, mock_config, fake_jetto_process, jintrac_env, jetto_exe):
        jetto_exe.unlink()

        with pytest.raises(job.JobManagerError):
            _ = job.JobManager.get_jetto_provenance(mock_config)

    def test_raises_if_USERS_HOME_missing_from_env(self, mock_config, fake_jetto_process, jintrac_env, jetto_exe, monkeypatch):
        monkeypatch.delenv('USERS_HOME')

        with pytest.raises(job.JobManagerError):
            _ = job.JobManager.get_jetto_provenance(mock_config)

    def test_calls_mpi_jetto_exe_with_version_flag(self, mock_config, fake_jetto_process, jintrac_env, jetto_exe):
        _ = job.JobManager.get_jetto_provenance(mock_config)

        assert [f'{jetto_exe}', '-v'] in fake_jetto_process.calls

    def test_calls_serial_jetto_exe_with_version_flag(self, mock_config, customise_fake_jetto_process, jintrac_env,
                                                      jetto_exe_serial):
        process = customise_fake_jetto_process(jetto_exe_path=str(jetto_exe_serial))
        mock_config.processors = 1

        _ = job.JobManager.get_jetto_provenance(mock_config)

        assert [f'{jetto_exe_serial}', '-v'] in process.calls

    def test_raises_if_call_to_jetto_exe_fails(self, mock_config, customise_fake_jetto_process, jintrac_env, jetto_exe):
        _ = customise_fake_jetto_process(jetto_returncode=1)

        with pytest.raises(job.JobManagerError):
            _ = job.JobManager.get_jetto_provenance(mock_config)

    @pytest.mark.parametrize('return_value', ['',
                                              'JETTO',
                                              'JETTO GIT',
                                              'JETTO GIT repository',
                                              'JETTO GIT repository: ',
                                              'JETTO GIT repository: jetto'])
    def test_raises_if_output_from_jetto_exe_cannot_be_parsed(self, mock_config, customise_fake_jetto_process,
                                                              jintrac_env, jetto_exe, return_value):
        _ = customise_fake_jetto_process(jetto_stdout=return_value)

        with pytest.raises(job.JobManagerError):
            _ = job.JobManager.get_jetto_provenance(mock_config)

    @pytest.mark.parametrize('path', ('/foo/bar/baz',
                                      '/home/user/jintrac/develop/jetto',
                                      '/opt/jintrac/30.0.1/jetto'))
    def test_returns_path_to_jetto_source_tree(self, mock_config, customise_fake_jetto_process,
                                               jintrac_env, jetto_exe, path):
        _ = customise_fake_jetto_process(jetto_stdout=f'JETTO GIT repository: {path}')

        actual_path, _ = job.JobManager.get_jetto_provenance(mock_config)

        assert actual_path == Path(path)

    @pytest.mark.parametrize('version', ('220922',
                                         '1.0.0',
                                         '19.9.9-rc1',
                                         '30.0.2',
                                         '31.0.0'))
    def test_returns_parsed_jetto_version(self, mock_config, customise_fake_jetto_process, jintrac_env, jetto_exe,
                                          version):
        _ = customise_fake_jetto_process(jetto_version=version)

        _, actual_version = job.JobManager.get_jetto_provenance(mock_config)

        assert actual_version == version

    @pytest.mark.parametrize('version_line', ('',
                                              'JETTO',
                                              'JETTO Version',
                                              'JETTO Version: '))
    def test_falls_back_to_config_load_module_for_jetto_version_if_it_cannot_be_parsed(self, mock_config,
                                                                                       customise_fake_jetto_process,
                                                                                       jintrac_env, jetto_exe,
                                                                                       version_line):
        _ = customise_fake_jetto_process(jetto_stdout=f'JETTO GIT repository: /home/sim/jintrac/develop/jetto\n{version_line}')

        _, version = job.JobManager.get_jetto_provenance(mock_config)

        assert version == mock_config.binary


class TestGetCommandLine:
    def test_rjettov_is_absolute_path_if_batch_case(self, mock_config, run_path, rundir_path, jetto_sources,
                                                    jetto_run_script):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job.JobType.BATCH, run_path)

        rjettov_path = Path(shlex.split(cmdline)[0])

        assert rjettov_path.is_absolute()

    @pytest.mark.parametrize('job_type', (job.JobType.DOCKER, job.JobType.PROMINENCE))
    def test_rjettov_is_not_absolute_path_if_not_batch_case(self, mock_config, run_path, rundir_path, jetto_sources,
                                                            jetto_run_script, job_type):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        rjettov_path = Path(shlex.split(cmdline)[0])

        assert rjettov_path == Path('rjettov')

    def test_rjettov_in_run_dir_in_batch_case(self, mock_config, run_path, rundir_path,
                                              jetto_sources, jetto_run_script):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job.JobType.BATCH, run_path)

        rjettov_path = Path(shlex.split(cmdline)[0])

        assert rjettov_path.parent == run_path

    @pytest.mark.parametrize('job_type', job.JobType)
    def test_command_runs_rjettov(self, mock_config, run_path, rundir_path, jetto_sources, jetto_run_script, job_type):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        rjettov_path = Path(shlex.split(cmdline)[0])

        assert rjettov_path.name == 'rjettov'

    @pytest.mark.parametrize('job_type', job.JobType)
    @pytest.mark.parametrize('flag', ('-S', '-p', '-x64'))
    def test_command_contains_minimum_flags(self, mock_config, run_path, rundir_path, jetto_sources,
                                            jetto_run_script, flag, job_type):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert flag in cmdline_split

    @pytest.mark.parametrize('job_type', job.JobType)
    def test_command_contains_mpi_flag_if_multiple_processors(self, mock_config, run_path, rundir_path, jetto_sources,
                                                              jetto_run_script, job_type):
        mock_config.processors = 2
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert '-xmpi' in cmdline_split

    @pytest.mark.parametrize('job_type', job.JobType)
    def test_command_mpi_flag_precedes_64_flag(self, mock_config, run_path, rundir_path, jetto_sources,
                                               jetto_run_script, job_type):
        mock_config.processors = 2
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert cmdline_split.index('-xmpi') < cmdline_split.index('-x64')

    @pytest.mark.parametrize('job_type', job.JobType)
    def test_command_no_mpi_flag_if_single_processor(self, mock_config, run_path, rundir_path, jetto_sources,
                                                     jetto_run_script, job_type):
        mock_config.processors = 1
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert '-xmpi' not in cmdline_split

    @pytest.mark.parametrize('job_type', job.JobType)
    def test_command_contains_imas_flag_if_imas_driver(self, mock_config, run_path, rundir_path, jetto_sources,
                                                       jetto_run_script, job_type):
        mock_config.driver = Driver.IMAS
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert '-I0' in cmdline_split

    @pytest.mark.parametrize('job_type', job.JobType)
    def test_command_does_not_contain_imas_flag_if_standard_driver(self, mock_config, run_path, rundir_path, jetto_sources,
                                                                   jetto_run_script, job_type):
        mock_config.driver = Driver.Std
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert '-I0' not in cmdline_split

    @pytest.mark.parametrize('job_type', job.JobType)
    def test_command_contains_expected_number_of_positional_arguments(self, mock_config, run_path, rundir_path,
                                                                      jetto_sources, job_type):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert len([s for s in cmdline_split if not s.startswith('-')]) == 4

    @pytest.mark.parametrize('job_type', job.JobType)
    @pytest.mark.parametrize('rundir_path', ('prom', 'foo', 'foo/bar', 'foo/bar/baz'))
    def test_command_contains_relative_rundir_path(self, mock_config, run_root, jetto_sources,
                                                   rundir_path, job_type):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type, run_root / rundir_path)

        cmdline_split = list(shlex.split(cmdline))

        assert cmdline_split[-3] == str(rundir_path)

    @pytest.mark.parametrize('job_type', job.JobType)
    @pytest.mark.parametrize('rundir_path', ('foo', 'foo/bar', 'foo/bar/baz'))
    def test_command_handles_rundir_path_as_string(self, mock_config, run_root, jetto_sources,
                                                   run_path, rundir_path, job_type):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, str(rundir_path), job_type, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert cmdline_split[-3] == str(rundir_path)

    def test_command_handles_runpath_as_string(self, mock_config, run_root, jetto_sources,
                                               run_path, rundir_path):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job.JobType.BATCH, str(run_path))

        rjettov_path = Path(shlex.split(cmdline)[0])

        assert rjettov_path.parent == run_path

    @pytest.mark.parametrize('job_type', (job.JobType.DOCKER, job.JobType.PROMINENCE))
    def test_can_omit_run_path_if_not_batch_job(self, mock_config, run_root, jetto_sources,
                                                rundir_path, job_type, run_path):
        _ = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type)

    def test_cannot_omit_run_path_if_batch_job(self, mock_config, run_root, jetto_sources,
                                               rundir_path, run_path):
        with pytest.raises(job.JobManagerError):
            _ = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job.JobType.BATCH)

    @pytest.mark.parametrize('userid', ('foo', 'bar', 'baz'))
    def test_command_contains_config_userid_if_batch_job(self, mock_config, run_root, jetto_sources,
                                                         rundir_path, run_path, userid):
        mock_config.userid = userid
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job.JobType.BATCH, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert cmdline_split[-1] == userid

    @pytest.mark.parametrize('binary', ('foo', 'bar', 'baz'))
    def test_command_contains_config_binary_if_batch_job(self, mock_config, run_root, jetto_sources,
                                                         rundir_path, run_path, binary):
        mock_config.binary = binary
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job.JobType.BATCH, run_path)

        cmdline_split = list(shlex.split(cmdline))

        assert cmdline_split[-2] == binary

    @pytest.mark.parametrize('job_type', (job.JobType.DOCKER, job.JobType.PROMINENCE))
    def test_command_userid_fixed_if_not_batch_job(self, mock_config, run_root, jetto_sources,
                                                   rundir_path, job_type):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type)

        cmdline_split = list(shlex.split(cmdline))

        assert cmdline_split[-1] == 'docker'

    @pytest.mark.parametrize('job_type', (job.JobType.DOCKER, job.JobType.PROMINENCE))
    def test_command_binary_fixed_if_not_batch_job(self, mock_config, run_root, jetto_sources,
                                                   rundir_path, job_type):
        cmdline = job.JobManager.get_jetto_cmdline(mock_config, rundir_path, job_type)

        cmdline_split = list(shlex.split(cmdline))

        assert cmdline_split[-2] == 'build'


class TestExportLaunchFile:
    @pytest.fixture
    def cmdline(self):
        return 'rjettov -I0 -xmpi -x64 -S -p foo bar baz'

    @pytest.fixture
    def run_path(self, run_path):
        run_path.mkdir(exist_ok=True, parents=True)

        return run_path

    def test_creates_launch_file_in_run_directory(self, run_path, mock_config, cmdline):
        run_path.mkdir(parents=True, exist_ok=True)

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)

        assert (run_path / 'jintrac.launch').is_file()

    def test_jetto_is_the_only_model(self, run_path, mock_config, cmdline):
        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert len(launch_config['models']) == 1

    def test_jetto_executable(self, run_path, mock_config, cmdline):
        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['models']['jetto']['executable'] == 'rjettov'

    def test_jetto_arguments(self, run_path, mock_config, cmdline):
        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['models']['jetto']['args'] == '-I0 -xmpi -x64 -S -p foo bar baz'

    def test_io_is_native(self, run_path, mock_config, cmdline):
        mock_config.driver = Driver.Std

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['io'] == 'native'

    def test_io_is_imas(self, run_path, mock_config, cmdline):
        mock_config.driver = Driver.IMAS

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['io'] == 'imas'

    def test_imas_settings_present_if_imas_driver(self, run_path, mock_config, cmdline):
        mock_config.driver = Driver.IMAS

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert 'imas' in launch_config

    def test_imas_settings_not_present_if_not_imas_driver(self, run_path, mock_config, cmdline):
        mock_config.driver = Driver.Std

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert 'imas' not in launch_config

    @pytest.mark.parametrize('tstart', (0.0, 1.0, 10.0, 100.0))
    def test_imas_start_time(self, run_path, mock_config, cmdline, tstart):
        mock_config.driver = Driver.IMAS
        mock_config.start_time = tstart

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['imas']['tstart'] == tstart

    @pytest.mark.parametrize('tend', (0.0, 1.0, 10.0, 100.0))
    def test_imas_end_time(self, run_path, mock_config, cmdline, tend):
        mock_config.driver = Driver.IMAS
        mock_config.end_time = tend

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['imas']['tend'] == tend

    def test_imas_replace_is_disabled(self, run_path, mock_config, cmdline):
        mock_config.driver = Driver.IMAS

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['imas']['replace'] is False

    def test_triggers_is_empty(self, run_path, mock_config, cmdline):
        mock_config.driver = Driver.IMAS

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['imas']['triggers'] == {}

    def test_intervals_is_empty(self, run_path, mock_config, cmdline):
        mock_config.driver = Driver.IMAS

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['imas']['intervals'] == {}

    def test_jetto_in_components(self, run_path, mock_config, cmdline):
        mock_config.driver = Driver.IMAS

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert 'JETTO' in launch_config['imas']['components']

    @pytest.fixture
    def imasdb_in(self):
        return IMASDB(user='imasdb', machine='jet', shot=12345, run=1)

    @pytest.fixture
    def imasdb_out(self):
        return IMASDB(user='imasdb', machine='jet', shot=12345, run=2)

    def test_idsin_first_component_if_enabled(self, run_path, mock_config, cmdline, imasdb_in):
        mock_config.driver = Driver.IMAS
        mock_config.read_from_ids = True
        mock_config.ids_in = imasdb_in

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['imas']['components'][:2] == ['IDSIN', 'JETTO']

    def test_idsin_not_in_components_if_disabled(self, run_path, mock_config, cmdline, imasdb_in):
        mock_config.driver = Driver.IMAS
        mock_config.read_from_ids = False
        mock_config.ids_in = imasdb_in

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert 'IDSIN' not in launch_config['imas']['components']

    @pytest.mark.parametrize('idsin_enabled', (True, False))
    def test_imasdb_in_fields_included_regardless_of_idsin_status(self, run_path, mock_config, cmdline, idsin_enabled,
                                                                  imasdb_in):
        mock_config.driver = Driver.IMAS
        mock_config.read_from_ids = idsin_enabled
        mock_config.ids_in = imasdb_in

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert all(launch_config['imas'][f'{f.name}_in'] ==
                   getattr(imasdb_in, f.name) for f in dataclasses.fields(imasdb_in))

    def test_idsout_last_component_if_enabled(self, run_path, mock_config, cmdline, imasdb_out):
        mock_config.driver = Driver.IMAS
        mock_config.create_output_ids = True
        mock_config.ids_out = imasdb_out

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert launch_config['imas']['components'][-2:] == ['JETTO', 'IDSOUT']

    def test_idsout_not_in_components_if_disabled(self, run_path, mock_config, cmdline, imasdb_out):
        mock_config.driver = Driver.IMAS
        mock_config.create_ids_output = False
        mock_config.ids_out = imasdb_out

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert 'IDSOUT' not in launch_config['imas']['components']

    @pytest.mark.parametrize('idsout_enabled', (True, False))
    def test_imasdb_out_fields_included_regardless_of_idsout_status(self, run_path, mock_config, cmdline,
                                                                    idsout_enabled, imasdb_out):
        mock_config.driver = Driver.IMAS
        mock_config.create_ids_output = idsout_enabled
        mock_config.ids_out = imasdb_out

        job.JobManager.export_launch_file(run_path, mock_config, cmdline)
        with open(run_path / 'jintrac.launch') as f:
            launch_config = yaml.safe_load(f)

        assert all(launch_config['imas'][f'{f.name}_out'] ==
                   getattr(imasdb_out, f.name) for f in dataclasses.fields(imasdb_out))


class TestGetJobEntrypoint:
    @pytest.mark.parametrize('driver', Driver)
    @pytest.mark.parametrize('jetto_version', ('', '1.0.0', '32.1.2'))
    def test_checks_if_jetto_version_is_valid(self, mock_config, driver, jetto_version, mock_semver):
        mock_config.driver = driver

        job.JobManager.get_job_entrypoint(mock_config, jetto_version)

        mock_semver.is_valid.assert_called_once_with(jetto_version)

    @pytest.mark.parametrize('jetto_version', ('', 'latest', '30-1-1', 'v220722'))
    def test_warning_if_jetto_version_is_not_a_semver(self, mock_config, jetto_version, mock_semver):
        mock_semver.is_valid.return_value = False

        with pytest.warns(job.JobWarning):
            job.JobManager.get_job_entrypoint(mock_config, jetto_version)

    @pytest.mark.parametrize('jetto_version', ('', 'latest', '30-1-1', 'v220722'))
    def test_returns_jetto_entrypoint_if_std_driver_and_not_semver(self, mock_config, jetto_version, mock_semver):
        mock_config.driver = Driver.Std
        mock_semver.is_valid.return_value = False

        entrypoint = job.JobManager.get_job_entrypoint(mock_config, jetto_version)

        assert entrypoint == job.JobEntrypoint.JETTO

    @pytest.mark.parametrize('jetto_version', ('', 'latest', '30-1-1', 'v220722'))
    def test_returns_jintrac_entrypoint_if_imas_driver_and_not_semver(self, mock_config, jetto_version, mock_semver):
        mock_config.driver = Driver.IMAS
        mock_semver.is_valid.return_value = False

        entrypoint = job.JobManager.get_job_entrypoint(mock_config, jetto_version)

        assert entrypoint == job.JobEntrypoint.JINTRAC

    @pytest.mark.parametrize('driver', Driver)
    @pytest.mark.parametrize('jetto_version', (job.JobManager._JINTRAC_M3_VERSION, '31.1.1-rc2', '32.0.0', '40.0.0'))
    def test_no_warning_if_jetto_version_follows_semver(self, mock_config, driver, jetto_version, mock_semver):
        mock_config.driver = driver
        mock_semver.is_valid.return_value = True

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            _ = job.JobManager.get_job_entrypoint(mock_config, jetto_version)

    @pytest.mark.parametrize('driver', Driver)
    @pytest.mark.parametrize('jetto_version', ('1.0.0', '29.1.2', '30.1.3-rc1'))
    def test_jetto_entrypoint_if_version_requires_it(self, mock_config, driver, jetto_version, mock_semver):
        mock_config.driver = driver
        mock_semver.is_valid.return_value = True
        mock_semver.higher.return_value = job.JobManager._JINTRAC_M3_VERSION

        entrypoint = job.JobManager.get_job_entrypoint(mock_config, jetto_version)

        assert entrypoint == job.JobEntrypoint.JETTO

    @pytest.mark.parametrize('driver', Driver)
    @pytest.mark.parametrize('jetto_version', (job.JobManager._JINTRAC_M3_VERSION, '31.1.1-rc2', '32.0.0', '40.0.0'))
    def test_jintrac_entrypoint_if_version_requires_it(self, mock_config, driver, jetto_version, mock_semver):
        mock_config.driver = driver
        mock_semver.is_valid.return_value = True
        mock_semver.higher.return_value = jetto_version

        entrypoint = job.JobManager.get_job_entrypoint(mock_config, jetto_version)

        assert entrypoint == job.JobEntrypoint.JINTRAC


class TestExportRunFiles:
    @pytest.fixture(autouse=True)
    def mock_export_launch_file(self):
        with mock.patch('jetto_tools.job.JobManager.export_launch_file') as _fixture:
            yield _fixture

    @pytest.fixture
    def cmdline(self):
        return 'rjettov -I0 -xmpi -x64 -S -p foo bar baz'

    @pytest.fixture
    def run_path(self, run_path):
        run_path.mkdir(exist_ok=True, parents=True)

        return run_path

    @pytest.fixture(autouse=True)
    def mock_get_cmdline(self, cmdline):
        with mock.patch('jetto_tools.job.JobManager.get_jetto_cmdline') as _fixture:
            _fixture.return_value = cmdline
            yield _fixture

    @pytest.fixture(autouse=True)
    def mock_batchscript_write(self):
        batchscript = type(sys)('batchscript')
        batchscript.write = mock.MagicMock()
        sys.modules['batchscript'] = batchscript

        yield batchscript.write

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    @pytest.mark.parametrize('job_type', job.JobType)
    def test_calls_get_jetto_cmdline_with_expected_args(self, run_path, rundir, mock_config, jetto_source_dir,
                                                        jetto_sources, job_type, mock_get_cmdline, entrypoint):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job_type, entrypoint, jetto_source_dir)

        mock_get_cmdline.assert_called_once_with(mock_config, rundir, job_type, run_path)

    def test_does_not_export_launchfile_if_not_supported(self, run_path, rundir, mock_config, jetto_source_dir,
                                                         jetto_sources, mock_export_launch_file,
                                                         mock_semver):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, job.JobEntrypoint.JETTO,
                                        jetto_source_dir)

        mock_export_launch_file.assert_not_called()

    def test_creates_launchfile_if_supported(self, run_path, rundir, mock_config, jetto_source_dir, jetto_sources,
                                             mock_export_launch_file, cmdline, mock_semver):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, job.JobEntrypoint.JINTRAC,
                                        jetto_source_dir)

        mock_export_launch_file.assert_called_once_with(run_path, mock_config, cmdline)

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_raises_if_jetto_run_script_does_not_exist_and_batch_job(self, run_path, rundir, mock_config,
                                                                     jetto_source_dir, jetto_run_script, jetto_sources,
                                                                     entrypoint):
        jetto_run_script.unlink()

        with pytest.raises(job.JobManagerError):
            job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint,
                                            jetto_source_dir)

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    @pytest.mark.parametrize('job_type', (job.JobType.DOCKER, job.JobType.PROMINENCE))
    def test_does_not_raise_if_jetto_run_script_does_not_exist_and_not_batch_job(self, run_path, rundir, mock_config,
                                                                                 jetto_source_dir, jetto_run_script,
                                                                                 jetto_sources, entrypoint,
                                                                                 job_type):
        jetto_run_script.unlink()

        job.JobManager.export_run_files(run_path, rundir, mock_config, job_type, entrypoint, jetto_source_dir)

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_copies_jetto_run_script_to_run_directory_if_batch_job(self, run_path, rundir, mock_config,
                                                                   jetto_source_dir, jetto_run_script, jetto_sources,
                                                                   entrypoint):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

        assert (run_path / 'rjettov').read_text() == jetto_run_script.read_text()

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_copies_jetto_run_script_permissions_if_batch_job(self, run_path, rundir, mock_config, jetto_source_dir,
                                                              jetto_run_script, jetto_sources, entrypoint):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

        new_stat = os.stat(run_path / 'rjettov')
        original_stat = os.stat(jetto_run_script)

        assert original_stat.st_mode == new_stat.st_mode

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    @pytest.mark.parametrize('job_type', (job.JobType.DOCKER, job.JobType.PROMINENCE))
    def test_does_not_copy_jetto_run_script_to_run_directory_if_not_batch_job(self, run_path, rundir, mock_config,
                                                                              jetto_source_dir, jetto_sources,
                                                                              entrypoint, job_type):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job_type, entrypoint, jetto_source_dir)

        assert not (run_path / 'rjettov').is_file()

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_does_not_raise_if_jetto_utils_script_does_not_exist_and_batch_job(self, run_path, rundir, mock_config,
                                                                               jetto_source_dir,
                                                                               jetto_utils_script, jetto_sources,
                                                                               entrypoint):
        jetto_utils_script.unlink()

        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_copies_jetto_utils_script_to_run_directory_if_batch_job(self, run_path, rundir, mock_config,
                                                                     jetto_source_dir, jetto_utils_script,
                                                                     jetto_sources, entrypoint):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

        assert (run_path / 'utils').read_text() == jetto_utils_script.read_text()

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_copies_jetto_utils_script_permissions_if_batch_job(self, run_path, rundir, mock_config, jetto_source_dir,
                                                                jetto_utils_script, jetto_sources, entrypoint):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

        new_stat = os.stat(run_path / 'utils')
        original_stat = os.stat(jetto_utils_script)

        assert original_stat.st_mode == new_stat.st_mode

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    @pytest.mark.parametrize('job_type', (job.JobType.DOCKER, job.JobType.PROMINENCE))
    def test_does_not_copy_jetto_utils_script_to_run_directory_if_not_batch_job(self, run_path, rundir, mock_config,
                                                                                jetto_source_dir,
                                                                                jetto_sources, entrypoint, job_type):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job_type, entrypoint, jetto_source_dir)

        assert not (run_path / 'utils').is_file()

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_creates_batchfile_if_batch_job(self, run_path, rundir, mock_config, jetto_source_dir, jetto_sources,
                                            entrypoint, mock_batchscript_write):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

        mock_batchscript_write.assert_called_once()

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    @pytest.mark.parametrize('job_type', (job.JobType.DOCKER, job.JobType.PROMINENCE))
    def test_does_not_create_batchfile_if_not_batch_job(self, run_path, rundir, mock_config, jetto_source_dir,
                                                        jetto_sources, entrypoint, job_type, mock_batchscript_write):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job_type, entrypoint, jetto_source_dir)

        mock_batchscript_write.assert_not_called()

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_passes_batchfile_path_to_writer(self, run_path, rundir, mock_config, jetto_source_dir, jetto_sources,
                                             entrypoint, mock_batchscript_write):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

        assert mock_batchscript_write.call_args[1]['filename'] == f'{run_path}/.llcmd'

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    @pytest.mark.parametrize('walltime, s', ((1.5, '01:30:00'),
                                             (2, '02:00:00'),
                                             (4.7, '04:42:00'),
                                             (6, '06:00:00'),
                                             (10.3, '10:18:00')))
    def test_passes_requested_walltime_to_writer(self, run_path, rundir, mock_config, jetto_source_dir, jetto_sources,
                                                 entrypoint, mock_batchscript_write, walltime, s):
        mock_config.walltime = walltime

        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

        assert mock_batchscript_write.call_args[1]['walltime'] == s

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_passes_default_walltime_if_not_set_in_config(self, run_path, rundir, mock_config, jetto_source_dir,
                                                          entrypoint, mock_batchscript_write, jetto_sources):
        mock_config.walltime = None

        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, entrypoint, jetto_source_dir)

        assert mock_batchscript_write.call_args[1]['walltime'] == '01:00:00'

    def test_writes_rjettov_exe_to_batchfile_if_version_requires_it(self, run_path, rundir, mock_config,
                                                                    jetto_source_dir, jetto_sources,
                                                                    mock_batchscript_write, cmdline, mock_semver):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, job.JobEntrypoint.JETTO,
                                        jetto_source_dir)

        assert mock_batchscript_write.call_args[1]['executable'] == shlex.split(cmdline)[0]

    def test_writes_rjettov_args_to_batchfile_if_version_requires_it(self, run_path, rundir, mock_config,
                                                                     jetto_source_dir, jetto_sources,
                                                                     mock_batchscript_write, cmdline, mock_semver):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, job.JobEntrypoint.JETTO,
                                        jetto_source_dir)

        assert mock_batchscript_write.call_args[1]['arguments'] == shlex.split(cmdline)[1:]

    def test_writes_jintrac_exec_to_batchfile_if_version_requires_it(self, run_path, rundir, mock_config,
                                                                     jetto_source_dir, jetto_sources,
                                                                     jintrac_source_dir,
                                                                     mock_batchscript_write, cmdline, mock_semver):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, job.JobEntrypoint.JINTRAC,
                                        jetto_source_dir)

        assert mock_batchscript_write.call_args[1]['executable'] == str(jintrac_source_dir / 'python/bin/jintrac')

    def test_writes_jintrac_args_to_batchfile_if_version_requires_it(self, run_path, rundir, mock_config,
                                                                     jetto_source_dir, jetto_sources,
                                                                     jintrac_source_dir,
                                                                     mock_batchscript_write, cmdline, mock_semver):
        job.JobManager.export_run_files(run_path, rundir, mock_config, job.JobType.BATCH, job.JobEntrypoint.JINTRAC,
                                        jetto_source_dir)

        assert mock_batchscript_write.call_args[1]['arguments'] == ['run']


class TestSubmitToBatch:
    @pytest.fixture
    def customise_fake_batch_submit(self):
        def _customise_fake_batch_submit(fake_process, returncode=0, stdout='llsubmit'):
            fake_process.register_subprocess(['batch_submit'],
                                             stdout=stdout,
                                             returncode=returncode,
                                             occurrences=100)
            
            return fake_process
        
        return _customise_fake_batch_submit
    
    @pytest.fixture
    def customise_fake_llsubmit(self):
        def _customise_fake_llsubmit(fake_process, returncode=0, stdout=''):
            fake_process.register_subprocess(['llsubmit', fake_process.any()],
                                    stdout='',
                                    returncode=returncode,
                                    occurrences=100)
            
            return fake_process
        
        return _customise_fake_llsubmit

    @pytest.fixture
    def customise_fake_sbatch(self):
        def _customise_fake_sbatch(fake_process, returncode=0, stdout=''):
            fake_process.register_subprocess(['sbatch', fake_process.any()],
                                    stdout='',
                                    returncode=returncode,
                                    occurrences=100)
            
            return fake_process
        
        return _customise_fake_sbatch
      
    @pytest.fixture
    def fake_processes(self, fake_process, customise_fake_batch_submit, customise_fake_llsubmit):
        
        fake_process = customise_fake_batch_submit(fake_process)
        fake_process = customise_fake_llsubmit(fake_process)
        
        return fake_process

    @pytest.fixture
    def jetto_version(self):
        return '32.0.0'

    @pytest.fixture(autouse=True)
    def mock_get_jetto_provenance(self, jetto_source_dir, jetto_version):
        with mock.patch('jetto_tools.job.JobManager.get_jetto_provenance') as _fixture:
            _fixture.return_value = jetto_source_dir, jetto_version

            yield _fixture

    @pytest.fixture(autouse=True)
    def mock_get_job_entrypoint(self):
        with mock.patch('jetto_tools.job.JobManager.get_job_entrypoint') as _fixture:
            _fixture.return_value = job.JobEntrypoint.JETTO

            yield _fixture

    @pytest.fixture(autouse=True)
    def mock_export_run_files(self):
        with mock.patch('jetto_tools.job.JobManager.export_run_files') as _fixture:

            yield _fixture

    @pytest.fixture(autouse=True)
    def mock_job(self, mocker):
        return mocker.patch('jetto_tools.job.Job')

    def test_raises_if_run_directory_already_exists(self, manager, mock_config, mock_get_jetto_provenance, jintrac_env,
                                                    rundir, fake_processes, run_root):
        (run_root / rundir).mkdir(parents=True)

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_batch(mock_config, rundir, exist_ok=False)

    def test_calls_get_jetto_provenance(self, manager, mock_config, mock_get_jetto_provenance, jintrac_env, rundir,
                                        fake_processes):
        manager.submit_job_to_batch(mock_config, rundir)

        mock_get_jetto_provenance.assert_called_once_with(mock_config)

    def test_exports_configuration_to_run_directory(self, manager, mock_config, jintrac_env, run_path, rundir,
                                                    fake_processes):
        manager.submit_job_to_batch(mock_config, rundir)

        mock_config.export.assert_called_once_with(str(run_path), rundir)

    def test_calls_get_job_entrypoint(self, manager, mock_config, mock_get_job_entrypoint, mock_get_jetto_provenance,
                                      jintrac_env, run_path, rundir, fake_processes, jetto_source_dir):
        mock_get_jetto_provenance.return_value = jetto_source_dir, 'foo'

        manager.submit_job_to_batch(mock_config, rundir)

        mock_get_job_entrypoint.assert_called_once_with(mock_config, 'foo')

    def test_converts_rundir_from_path_object_if_necessary(self, manager, mock_config, jintrac_env, run_path, rundir,
                                                           fake_processes):
        manager.submit_job_to_batch(mock_config, Path(rundir))

        mock_config.export.assert_called_once_with(str(run_path), rundir)

    @pytest.fixture()
    def pointdirs(self, run_root):
        dirs = [run_root / f'point_00{i}' for i in range(1, 4)]
        _ = [d.mkdir() for d in dirs]

        return [str(d) for d in dirs]

    @pytest.mark.parametrize('entrypoint', job.JobEntrypoint)
    def test_exports_run_files_in_point_run_directories(self, manager, mock_config, jintrac_env, pointdirs,
                                                        rundir, mock_export_run_files, jetto_source_dir, jetto_version,
                                                        fake_processes, run_root, mock_get_job_entrypoint, entrypoint):
        mock_get_job_entrypoint.return_value = entrypoint
        mock_config.export.return_value = pointdirs

        manager.submit_job_to_batch(mock_config, rundir)

        assert all(mock.call(Path(p), Path(p).relative_to(run_root), mock_config, job.JobType.BATCH, entrypoint,
                             jetto_source_dir)
                   in mock_export_run_files.mock_calls for p in pointdirs)

    def test_does_not_submit_run_if_not_required(self, manager, mock_config, jintrac_env, run_path, rundir,
                                                 fake_processes):
        llcmd = run_path / '.llcmd'
        manager.submit_job_to_batch(mock_config, rundir, run=False)

        assert [f'llsubmit', f'{llcmd}'] not in fake_processes.calls

    def test_submits_run_if_required(self, manager, mock_config, jintrac_env, run_path, rundir, fake_processes):
        llcmd = run_path / '.llcmd'
        manager.submit_job_to_batch(mock_config, rundir, run=True)

        assert [f'llsubmit', f'{llcmd}'] in fake_processes.calls

    def test_submits_for_multiple_directories_if_required(self, manager, mock_config, jintrac_env, run_path, rundir,
                                                          fake_processes, pointdirs):
        mock_config.export.return_value = pointdirs
        llcmds = [os.path.join(pointdir, '.llcmd') for pointdir in pointdirs]

        manager.submit_job_to_batch(mock_config, rundir, run=True)

        assert all(['llsubmit', f'{llcmd}'] in fake_processes.calls for llcmd in llcmds)

    def test_raises_if_batch_submit_command_fails(self, manager, mock_config, jintrac_env,
                                                  rundir, fake_process, customise_fake_batch_submit, run_root, jetto_sources):
        _ = customise_fake_batch_submit(fake_process, returncode=1)

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_batch(mock_config, rundir, run=True)

    def test_raises_if_llsubmit_fails(self, manager, mock_config, jintrac_env,
                                      fake_process, customise_fake_batch_submit, 
                                      customise_fake_llsubmit, rundir, run_root, jetto_sources):
        fake_process = customise_fake_batch_submit(fake_process)
        _ = customise_fake_llsubmit(fake_process, returncode=1)

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_batch(mock_config, rundir, run=True)

    def test_handles_batch_submit_with_args(self, manager, mock_config, jintrac_env,
                                            rundir, fake_process, customise_fake_sbatch, customise_fake_batch_submit, run_root, jetto_sources):
        fake_process = customise_fake_sbatch(fake_process)
        fake_process = customise_fake_batch_submit(fake_process, stdout='sbatch --no-requeue')

        manager.submit_job_to_batch(mock_config, rundir, run=True)

        assert fake_process.call_count(['sbatch', '--no-requeue', f'{run_root / rundir / ".llcmd"}']) == 1

    def test_creates_job_corresponding_to_rundir(self, manager, mock_config, jintrac_env, fake_processes,
                                                 rundir, run_root, jetto_sources, mock_job):
        _ = manager.submit_job_to_batch(mock_config, rundir)

        mock_job.assert_called_once_with(str(run_root / rundir))

    def test_creates_multiple_jobs_corresponding_to_rundirs(self, manager, mock_config, jintrac_env, rundir,
                                                            fake_processes, run_root, pointdirs, jetto_sources,
                                                            mock_job, mocker):
        mock_config.export.return_value = pointdirs

        _ = manager.submit_job_to_batch(mock_config, rundir)

        assert all(mocker.call(p) in mock_job.mock_calls for p in pointdirs)

    def test_returns_job_associated_with_single_point(self, manager, mock_config, jintrac_env, fake_processes,
                                                      rundir, run_root, jetto_sources, mock_job):
        mock_job.return_value = 1

        jobs = manager.submit_job_to_batch(mock_config, rundir)

        assert jobs == [1]

    def test_returns_job_associated_with_multiple_points(self, manager, mock_config, jintrac_env, rundir,
                                                         fake_processes, run_root, pointdirs, jetto_sources, mock_job,
                                                         mocker):
        mock_config.export.return_value = pointdirs
        mock_job.side_effect = [1, 2, 3]

        jobs = manager.submit_job_to_batch(mock_config, rundir)

        assert jobs == [1, 2, 3]


@pytest.fixture()
def mock_prominence_client():
    return mock.Mock(spec=prominence.client.ProminenceClient)


@pytest.fixture()
def mock_prominence(mock_prominence_client):
    with mock.patch('jetto_tools.job.prominence.client.ProminenceClient',
                    autospec=prominence.client.ProminenceClient) as _fixture:
        _fixture.return_value = mock_prominence_client

        yield _fixture


class TestSubmitSingleRunToProminence:
    """Test that we can submit a JETTO job to the PROMINENCE system"""
    @pytest.fixture()
    def export(self):
        """Create three job files in the export directory"""
        def _fixture(path):
            for i in range(3):
                (path / f'file{i}.txt').write_text('')

        return _fixture

    def compare_dirs(self, original, tarball):
        result = True
        cmp = filecmp.dircmp(original, tarball)

        if cmp.common == cmp.right_list:
            for file in cmp.common:
                first_file = os.path.join(original, file)
                second_file = os.path.join(tarball, file)
                if not filecmp.cmp(first_file, second_file, shallow=False):
                    result = False
        else:
            result = False
        return result

    @pytest.fixture
    def cmdline(self):
        return 'rjettov -I0 -xmpi -x64 -S prom build docker'

    @pytest.fixture(autouse=True)
    def mock_get_cmdline(self, cmdline):
        with mock.patch('jetto_tools.job.JobManager.get_jetto_cmdline') as _fixture:
            _fixture.return_value = cmdline
            yield _fixture

    @pytest.fixture(autouse=True)
    def mock_get_job_entrypoint(self):
        with mock.patch('jetto_tools.job.JobManager.get_job_entrypoint') as _fixture:
            _fixture.return_value = job.JobEntrypoint.JETTO

            yield _fixture

    @pytest.fixture(autouse=True)
    def mock_export_run_files(self):
        def _side_effect(*args, **kwargs):
            args[0].mkdir(parents=True, exist_ok=True)
            (args[0] / 'jintrac.launch').write_text('')

        with mock.patch('jetto_tools.job.JobManager.export_run_files') as _fixture:
            _fixture.side_effect = _side_effect
            yield _fixture

    def test_exports_configuration_to_run_directory(self, mock_prominence, manager, mock_config, jintrac_env,
                                                    rundir, run_path):
        manager.submit_job_to_prominence(mock_config, rundir)

        mock_config.export.assert_called_once_with(str(run_path), rundir)

    def test_exports_run_files_to_run_directory(self, mock_prominence, manager, mock_config, jintrac_env,
                                                rundir, run_path, mock_export_run_files, mock_get_job_entrypoint):
        manager.submit_job_to_prominence(mock_config, rundir)

        mock_export_run_files.assert_called_once_with(run_path, Path('prom'), mock_config, job.JobType.PROMINENCE,
                                                      mock_get_job_entrypoint.return_value)

    def test_exports_run_files_with_nested_run_directory(self, mock_prominence, manager, mock_config, jintrac_env,
                                                run_root, mock_export_run_files, mock_get_job_entrypoint):
        rundir = Path('foo/bar/baz')
        run_path = run_root / rundir
        mock_config.export.return_value = [str(run_path)]
        
        manager.submit_job_to_prominence(mock_config, rundir)

        mock_export_run_files.assert_called_once_with(run_path, Path('prom/bar/baz'), mock_config, job.JobType.PROMINENCE,
                                                      mock_get_job_entrypoint.return_value)

    def test_converts_rundir_from_path_object_if_necessary(self, mock_prominence, manager, mock_config, jintrac_env,
                                                           rundir, run_path, mock_export_run_files):
        manager.submit_job_to_prominence(mock_config, Path(rundir))

        mock_config.export.assert_called_once_with(str(run_path), rundir)

    def test_calls_get_job_entrypoint(self, mock_prominence, manager, mock_config, jintrac_env, rundir, run_path,
                                      mock_export_run_files, mock_get_job_entrypoint):
        manager.submit_job_to_prominence(mock_config, rundir)

        mock_get_job_entrypoint.assert_called_with(mock_config, mock_config.binary)

    def test_prominence_authenticated_client_created(self, mock_prominence, manager, mock_config, jintrac_env,
                                                     rundir, run_root):
        manager.submit_job_to_prominence(mock_config, rundir)

        mock_prominence.assert_called_once_with(authenticated=True)

    def test_prominence_upload_called(self, mock_prominence, manager, mock_config, jintrac_env,
                                      rundir, run_root, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        mock_prominence_client.upload.assert_called_once()

    @pytest.mark.parametrize('run_dir, expected_tarball_pattern',
                             [('foo', r'foo-[0-9a-fA-F\-]+\.tgz'),
                              ('foo/bar', r'foo\-bar[0-9a-fA-F\-]+\.tgz')],
                             ids=['Single directory', 'Nested directory'])
    def test_tarball_name_format(self, mock_prominence, manager, mock_config, jintrac_env,
                                 run_root, run_dir, expected_tarball_pattern, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, run_dir)

        actual_tarball_name = mock_prominence_client.upload.call_args[0][0]

        assert re.fullmatch(expected_tarball_pattern, actual_tarball_name)

    def test_tarball_files_are_subset_of_rundir(self, mock_prominence, manager, mock_config, jintrac_env,
                                                run_root, rundir, tar_extract_dir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        tarball_path = mock_prominence_client.upload.call_args[0][1]
        with tarfile.open(tarball_path) as tarball:
            tarball.extractall(path=tar_extract_dir)

        assert self.compare_dirs(str(run_root / rundir), str(tar_extract_dir / rundir))

    def test_jset_not_excluded_from_tarball(self, mock_prominence, manager, mock_config, jintrac_env,
                                            run_root, rundir, tar_extract_dir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        tarball_path = mock_prominence_client.upload.call_args[0][1]
        with tarfile.open(tarball_path) as tarball:
            tarball.extractall(path=tar_extract_dir)

        assert any('jetto.jset' in files for _1, _2, files in
                   os.walk(tar_extract_dir / rundir))

    @pytest.mark.parametrize('side_effect', [ConnectionError,
                                             AuthenticationError,
                                             FileUploadError])
    def test_raises_if_upload_fails(self, mock_prominence, manager, mock_config, jintrac_env,
                                    run_root, rundir, side_effect, mock_prominence_client):
        mock_prominence_client.upload.side_effect = side_effect

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_prominence(mock_config, rundir)

    def test_raises_if_walltime_is_empty(self, mock_prominence, manager, mock_config, jintrac_env,
                                         run_root, rundir, mock_prominence_client):
        mock_config.walltime = None

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_prominence(mock_config, rundir)

    def test_prominence_create_job_called(self, mock_prominence, manager, mock_config, jintrac_env,
                                          run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        mock_prominence_client.create_job.assert_called_once()

    @pytest.mark.parametrize('side_effect', [ConnectionError,
                                             AuthenticationError,
                                             FileUploadError])
    def test_raises_if_create_job_fails(self, mock_prominence, manager, mock_config, jintrac_env,
                                        run_root, rundir, mock_prominence_client, side_effect):
        mock_prominence_client.create_job.side_effect = side_effect

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_prominence(mock_config, rundir)

    @pytest.mark.parametrize('run_dir, expected_name',
                             [('foo', 'foo'),
                              ('foo/bar', 'foo-bar')],
                             ids=['Single directory', 'Nested directory'])
    def test_job_name_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                         run_root, mock_prominence_client, run_dir, expected_name):
        manager.submit_job_to_prominence(mock_config, run_dir)

        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['name'] == expected_name

    def test_job_task_has_single_dict(self, mock_prominence, manager, mock_config, jintrac_env,
                                      run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert len(job_['tasks']) == 1 and isinstance(job_['tasks'][0], dict)

    def test_job_task_cmd_contains_jetto_cmdline_if_required_by_version(self, mock_prominence, manager, mock_config,
                                                                        jintrac_env, run_root, rundir,
                                                                        mock_prominence_client, cmdline,
                                                                        mock_get_job_entrypoint):
        mock_get_job_entrypoint.return_value = job.JobEntrypoint.JETTO

        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['tasks'][0]['cmd'] == cmdline

    def test_job_task_cmd_contains_jintrac_cmdline_if_required_by_version(self, mock_prominence, manager, mock_config,
                                                                          jintrac_env, run_root, rundir,
                                                                          mock_prominence_client, mock_get_job_entrypoint):
        mock_get_job_entrypoint.return_value = job.JobEntrypoint.JINTRAC
        mock_config.driver = Driver.Std

        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['tasks'][0]['cmd'] == 'jintrac run -r /jetto/runs/prom'
    
    def test_job_task_cmd_contains_container_entrypoint_in_IMAS_case(self, mock_prominence, manager, mock_config,
                                                                          jintrac_env, run_root, rundir,
                                                                          mock_prominence_client, mock_get_job_entrypoint):
        mock_get_job_entrypoint.return_value = job.JobEntrypoint.JINTRAC
        mock_config.driver = Driver.IMAS

        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['tasks'][0]['cmd'] == '/docker-entrypoint.sh jintrac run -r /jetto/runs/prom'

    @pytest.mark.parametrize('userid, binary, image', [('sim', 'v060619', 'CCFE/JINTRAC/sim:v060619.sif'),
                                                       ('foo', 'bar', 'CCFE/JINTRAC/foo:bar.sif'),
                                                       ('user', 'baz-imas', 'CCFE/JINTRAC/user:baz.sif')])
    def test_job_task_image_has_expected_values_in_Std_case(self, mock_prominence, manager, mock_config, jintrac_env,
                                                           run_root, rundir, mock_prominence_client, userid, binary, image):
        mock_config.driver = Driver.Std
        mock_config.userid = userid
        mock_config.binary = binary

        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['tasks'][0]['image'] == image

    @pytest.mark.parametrize('userid, binary, image', [('sim', 'v060619', 'CCFE/JINTRAC/sim:v060619-imas.sif'),
                                                       ('foo', 'bar', 'CCFE/JINTRAC/foo:bar-imas.sif'),
                                                       ('user', 'baz-imas', 'CCFE/JINTRAC/user:baz-imas.sif')])
    def test_job_task_image_has_expected_values_in_IMAS_case(self, mock_prominence, manager, mock_config, jintrac_env,
                                                             run_root, rundir, mock_prominence_client, userid, binary, image):
        mock_config.driver = Driver.IMAS
        mock_config.userid = userid
        mock_config.binary = binary

        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['tasks'][0]['image'] == image

    def test_job_task_runtime_is_singularity(self, mock_prominence, manager, mock_config, jintrac_env,
                                             run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['tasks'][0]['runtime'] == 'singularity'

    @pytest.mark.parametrize('cpus', [1, 2], ids=['Serial', 'Parallel'])
    def test_job_resources_cpus_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                                   run_root, rundir, mock_prominence_client, cpus):
        mock_config.processors = cpus

        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['resources']['cpus'] == cpus

    @pytest.mark.parametrize('cpus, memory', [(1, 6),
                                              (2, 6),
                                              (3, 6),
                                              (4, 8)])
    def test_job_resources_memory_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                                     run_root, rundir, mock_prominence_client, cpus, memory):
        mock_config.processors = cpus

        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['resources']['memory'] == memory

    def test_job_resources_disk_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                                   run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['resources']['disk'] == 10 and job_['resources']['nodes'] == 1

    @pytest.mark.parametrize('in_walltime, out_walltime', [(0, 0), (1, 60), (1.5, 90)])
    def test_job_resources_walltime_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                                       run_root, rundir, mock_prominence_client, in_walltime,
                                                       out_walltime):
        mock_config.walltime = in_walltime

        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['resources']['walltime'] == out_walltime

    def test_job_raises_if_walltime_is_empty(self, mock_prominence, manager, mock_config, jintrac_env,
                                             run_root, rundir, mock_prominence_client):
        mock_config.walltime = None

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_prominence(mock_config, rundir)

    def test_job_artifacts_has_single_dict(self, mock_prominence, manager, mock_config, jintrac_env,
                                           run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert len(job_['artifacts']) == 1 and isinstance(job_['artifacts'][0], dict)

    def test_job_artifacts_url_is_set_to_tarball(self, mock_prominence, manager, mock_config, jintrac_env,
                                                 run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        tarball_path = mock_prominence_client.upload.call_args[0][1]
        tarball = os.path.basename(tarball_path)
        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['artifacts'][0]['url'] == tarball

    def test_job_artifact_mountpoint_contains_rundir(self, mock_prominence, manager, mock_config, jintrac_env,
                                                     run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['artifacts'][0]['mountpoint'] == f'{rundir}:/jetto/runs/prom'

    def test_job_labels_app_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                               run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['labels']['app'] == 'jintrac'

    def test_job_labels_fullpath_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                                    run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['labels']['fullpath'] == str(run_root / rundir)

    def test_job_labels_codeid_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                                  run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['labels']['codeid'] == 'jetto'

    def test_job_output_dirs_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                                run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['outputDirs'] == [rundir]

    def test_job_policies_has_expected_value(self, mock_prominence, manager, mock_config, jintrac_env,
                                             run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_config, rundir)

        job_ = mock_prominence_client.create_job.call_args[0][0]

        assert job_['policies'] == {'maximumTimeInQueue': 7 * 24 * 60, 'leaveInQueue': True, 'autoScalingType': None}

    def test_prominence_job_id_is_returned(self, mock_prominence, manager, mock_config, jintrac_env,
                                           run_root, rundir, mock_prominence_client):
        mock_prominence_client.create_job.return_value = 1234

        id = manager.submit_job_to_prominence(mock_config, rundir)

        assert id == 1234

    def test_creates_file_recording_job_id(self, mock_prominence, manager, mock_config, jintrac_env,
                                           run_root, rundir, mock_prominence_client):
        mock_prominence_client.create_job.return_value = 1234

        _ = manager.submit_job_to_prominence(mock_config, rundir)

        assert (run_root / rundir / 'remote.jobid').read_text() == 'Job submitted with id 1234\n'


class TestSubmitScanToProminence:
    """Test that we can submit a JETTO scan workflow to the PROMINENCE system"""

    @pytest.fixture()
    def mock_export(self, run_root):
        """Create three dummy files in three point directories"""

        def _export(_self, run_dir):
            pointdirs = []
            for point in range(3):
                run_path = run_root / run_dir / f'point_00{point}'
                run_path.mkdir(parents=True, exist_ok=True)

                for file in ('jetto.jset', 'jetto.in', 'serialisation.json'):
                    with open(os.path.join(run_path, file), 'wt') as f:
                        f.write(file)

                pointdirs.append(run_path)

            return pointdirs

        return _export

    @pytest.fixture()
    def mock_scan_config(self, run_root, mock_export):
        m = mock.MagicMock(spec=jetto_tools.config.RunConfig)
        m.userid = 'user'
        m.binary = 'v060619'
        m.processors = 2
        m.walltime = 2
        m._npoints.return_value = 3
        m.export.side_effect = mock_export

        return m

    def compare_dir_trees(self, original, new, ignore):
        """Recursively compare the original and tarballed directory tree

        Adapted from https://stackoverflow.com/a/6681395
        """
        dirs_cmp = filecmp.dircmp(original, new, ignore=ignore)
        if len(dirs_cmp.left_only) > 0 or len(dirs_cmp.right_only) > 0 or \
                len(dirs_cmp.funny_files) > 0:
            return False
        (_, mismatch, errors) = filecmp.cmpfiles(
            original, new, dirs_cmp.common_files, shallow=False)
        if len(mismatch) > 0 or len(errors) > 0:
            return False
        for common_dir in dirs_cmp.common_dirs:
            new_dir1 = os.path.join(original, common_dir)
            new_dir2 = os.path.join(new, common_dir)
            if not self.compare_dir_trees(new_dir1, new_dir2, ignore=ignore):
                return False

        return True

    @pytest.fixture
    def cmdline(self):
        return 'rjettov -I0 -xmpi -x64 -S prom build docker'

    @pytest.fixture(autouse=True)
    def mock_get_cmdline(self, cmdline):
        with mock.patch('jetto_tools.job.JobManager.get_jetto_cmdline') as _fixture:
            _fixture.return_value = cmdline
            yield _fixture

    @pytest.fixture(autouse=True)
    def mock_get_job_entrypoint(self):
        with mock.patch('jetto_tools.job.JobManager.get_job_entrypoint') as _fixture:
            _fixture.return_value = job.JobEntrypoint.JETTO

            yield _fixture

    @pytest.fixture(autouse=True)
    def mock_export_run_files(self):
        def _side_effect(*args, **kwargs):
            (args[0] / 'jintrac.launch').write_text('')

        with mock.patch('jetto_tools.job.JobManager.export_run_files') as _fixture:
            _fixture.side_effect = _side_effect
            yield _fixture

    def test_exports_configuration_to_run_directory(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                    rundir, run_root):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        mock_scan_config.export.assert_called_once_with(str(run_root / rundir), rundir)

    def test_converts_rundir_from_path_object_if_necessary(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                           rundir, run_root):
        manager.submit_job_to_prominence(mock_scan_config, Path(rundir))

        mock_scan_config.export.assert_called_once_with(str(run_root / rundir), rundir)

    def test_calls_get_job_entrypoint(self, mock_prominence, manager, mock_scan_config, jintrac_env, rundir, run_root,
                                      mock_get_job_entrypoint):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        mock_get_job_entrypoint.assert_called_with(mock_scan_config, mock_scan_config.binary)

    def test_exports_run_files_to_point_directories(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                    rundir, run_path, mock_export_run_files, mock_get_job_entrypoint):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        mock_export_run_files.assert_has_calls([mock.call(run_path / p, Path('prom') / p, mock_scan_config,
                                                          job.JobType.PROMINENCE, mock_get_job_entrypoint.return_value)
                                                for p in ('point_000', 'point_001', 'point_002')])

    def test_exports_run_files_to_nested_point_directories(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                           run_root, mock_export_run_files, mock_get_job_entrypoint):
        rundir = Path('foo/bar/baz')
        run_path = run_root / rundir
        mock_scan_config.export.return_value = [str(run_path / p) for p in ('point_000', 'point_001', 'point_002')]
    
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        mock_export_run_files.assert_has_calls([mock.call(run_path / p, Path('prom/bar/baz') / p, mock_scan_config,
                                                          job.JobType.PROMINENCE, mock_get_job_entrypoint.return_value)
                                                for p in ('point_000', 'point_001', 'point_002')])
        
    def test_prominence_authenticated_client_created(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                     rundir, run_root):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        mock_prominence.assert_called_once_with(authenticated=True)

    def test_prominence_upload_called(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                      rundir, run_root, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        mock_prominence_client.upload.assert_called_once()

    @pytest.mark.parametrize('run_dir, expected_tarball_pattern',
                             [('foo', r'foo-[0-9a-fA-F\-]+\.tgz'),
                              ('foo/bar', r'foo\-bar[0-9a-fA-F\-]+\.tgz')],
                             ids=['Single directory', 'Nested directory'])
    def test_tarball_name_format(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                 run_root, run_dir, expected_tarball_pattern, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, run_dir)

        actual_tarball_name = mock_prominence_client.upload.call_args[0][0]

        assert re.fullmatch(expected_tarball_pattern, actual_tarball_name)

    def test_tarball_files_match_rundir_contents(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                 run_root, rundir, tar_extract_dir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        tarball_path = mock_prominence_client.upload.call_args[0][1]
        with tarfile.open(tarball_path) as tarball:
            tarball.extractall(path=tar_extract_dir)

        assert self.compare_dir_trees(str(run_root / rundir),
                                      str(tar_extract_dir / rundir),
                                      ignore=['remote.jobid', 'jetto.jset'])

    def test_tarball_files_match_nested_rundir_contents(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                        run_root, tar_extract_dir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, 'foo/bar')

        tarball_path = mock_prominence_client.upload.call_args[0][1]
        with tarfile.open(tarball_path) as tarball:
            tarball.extractall(path=tar_extract_dir)

        assert self.compare_dir_trees(str(run_root / 'foo/bar'),
                                      str(tar_extract_dir / 'bar'),
                                      ignore=['remote.jobid', 'jetto.jset'])

    # No longer a useful test as JSET files are only excluded if the scan is larger than a certain limit
    @pytest.mark.skip
    def test_jset_files_excluded_from_tarball(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                              run_root, rundir, tar_extract_dir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        tarball_path = mock_prominence_client.upload.call_args[0][1]
        with tarfile.open(tarball_path) as tarball:
            tarball.extractall(path=tar_extract_dir.strpath)

        assert all('jetto.jset' not in files for _1, _2, files in
                   os.walk(os.path.join(tar_extract_dir.strpath, rundir)))

    @pytest.mark.parametrize('side_effect', [ConnectionError,
                                             AuthenticationError,
                                             FileUploadError])
    def test_raises_if_upload_fails(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                    run_root, rundir, side_effect, mock_prominence_client):
        mock_prominence_client.upload.side_effect = side_effect

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_prominence(mock_scan_config, rundir)

    def test_prominence_create_workflow(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                        run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        mock_prominence_client.create_workflow.assert_called_once()

    @pytest.mark.parametrize('side_effect', [ConnectionError,
                                             AuthenticationError,
                                             WorkflowCreationError])
    def test_raises_if_create_workflow_fails(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                             run_root, rundir, mock_prominence_client, side_effect):
        mock_prominence_client.create_workflow.side_effect = side_effect

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_prominence(mock_scan_config, rundir)

    @pytest.mark.parametrize('run_dir, expected_name',
                             [('foo', 'foo'),
                              ('foo/bar', 'foo-bar')],
                             ids=['Single directory', 'Nested directory'])
    def test_workflow_name_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                              run_root, mock_prominence_client, run_dir, expected_name):
        manager.submit_job_to_prominence(mock_scan_config, run_dir)

        workflow = mock_prominence_client.create_workflow.call_args[0][0]

        assert workflow['name'] == expected_name

    def test_workflow_has_single_job(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                     run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)
        jobs = mock_prominence_client.create_workflow.call_args[0][0]['jobs']

        assert len(jobs) == 1

    def test_workflow_job_tasks_has_single_task(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)
        job_ = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]

        assert len(job_['tasks']) == 1

    def test_workflow_task_cmd_contains_jetto_cmdline_if_required_by_version(self, mock_prominence, manager,
                                                                             mock_scan_config, jintrac_env, run_root,
                                                                             rundir, mock_prominence_client, cmdline,
                                                                             mock_get_job_entrypoint):
        mock_get_job_entrypoint.return_value = job.JobEntrypoint.JETTO

        manager.submit_job_to_prominence(mock_scan_config, rundir)
        task = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['tasks'][0]

        assert task['cmd'] == cmdline

    def test_workflow_task_cmd_contains_jintrac_cmdline_if_required_by_version(self, mock_prominence, manager,
                                                                               mock_scan_config, jintrac_env, run_root,
                                                                               rundir, mock_prominence_client,
                                                                               mock_get_job_entrypoint):
        mock_get_job_entrypoint.return_value = job.JobEntrypoint.JINTRAC

        manager.submit_job_to_prominence(mock_scan_config, rundir)
        task = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['tasks'][0]

        assert task['cmd'] == 'jintrac run -r /jetto/runs/$workdir'

    @pytest.mark.parametrize('userid, binary, image', [('sim', 'v060619', 'CCFE/JINTRAC/sim:v060619.sif'),
                                                       ('foo', 'bar', 'CCFE/JINTRAC/foo:bar.sif'),
                                                       ('user', 'baz-imas', 'CCFE/JINTRAC/user:baz.sif')])
    def test_workflow_task_image_has_expected_values_in_Std_case(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                     run_root, rundir, mock_prominence_client, userid, binary, image):
        mock_scan_config.driver = Driver.Std
        mock_scan_config.userid = userid
        mock_scan_config.binary = binary

        manager.submit_job_to_prominence(mock_scan_config, rundir)
        task = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['tasks'][0]

        assert task['image'] == image

    @pytest.mark.parametrize('userid, binary, image', [('sim', 'v060619', 'CCFE/JINTRAC/sim:v060619-imas.sif'),
                                                       ('foo', 'bar', 'CCFE/JINTRAC/foo:bar-imas.sif'),
                                                       ('user', 'baz-imas', 'CCFE/JINTRAC/user:baz-imas.sif')])
    def test_workflow_task_image_has_expected_values_in_IMAS_case(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                     run_root, rundir, mock_prominence_client, userid, binary, image):
        mock_scan_config.driver = Driver.IMAS
        mock_scan_config.userid = userid
        mock_scan_config.binary = binary

        manager.submit_job_to_prominence(mock_scan_config, rundir)
        task = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['tasks'][0]

        assert task['image'] == image

    def test_workflow_task_runtime_is_singularity(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                              run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)
        task = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['tasks'][0]

        assert task['runtime'] == 'singularity'

    @pytest.mark.parametrize('cpus', [1, 2], ids=['Serial', 'Parallel'])
    def test_workflow_resources_cpus_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                        run_root, rundir, mock_prominence_client, cpus):
        mock_scan_config.processors = cpus

        manager.submit_job_to_prominence(mock_scan_config, rundir)
        resources = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['resources']

        assert resources['cpus'] == cpus

    @pytest.mark.parametrize('cpus, memory', [(1, 6),
                                              (2, 6),
                                              (3, 6),
                                              (4, 8)])
    def test_job_resources_memory_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                     run_root, rundir, mock_prominence_client, cpus, memory):
        mock_scan_config.processors = cpus

        manager.submit_job_to_prominence(mock_scan_config, rundir)
        resources = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['resources']

        assert resources['memory'] == memory

    def test_job_resources_disk_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                   run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)
        resources = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['resources']

        assert resources['disk'] == 10 and resources['nodes'] == 1

    @pytest.mark.parametrize('in_walltime, out_walltime', [(0, 0), (1, 60), (1.5, 90)])
    def test_job_resources_walltime_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                       run_root, rundir, mock_prominence_client, in_walltime,
                                                       out_walltime):
        mock_scan_config.walltime = in_walltime

        manager.submit_job_to_prominence(mock_scan_config, rundir)
        resources = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['resources']

        assert resources['walltime'] == out_walltime

    def test_job_raises_if_walltime_is_empty(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                             run_root, rundir, mock_prominence_client):
        mock_scan_config.walltime = None

        with pytest.raises(job.JobManagerError):
            manager.submit_job_to_prominence(mock_scan_config, rundir)

    def test_job_artifacts_has_single_dict(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                           run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)
        artifacts = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['artifacts']

        assert len(artifacts) == 1

    def test_job_artifacts_url_is_set_to_tarball(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                 run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        tarball_path = mock_prominence_client.upload.call_args[0][1]
        tarball = os.path.basename(tarball_path)
        artifacts = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['artifacts'][0]

        assert artifacts['url'] == tarball

    def test_job_artifact_mountpoint_contains_rundir(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                     run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        artifacts = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['artifacts'][0]

        assert artifacts['mountpoint'] == f'{rundir}:/jetto/runs/prom'

    def test_job_artifact_mountpoint_is_basename_of_nested_rundir(self, mock_prominence, manager, mock_scan_config,
                                                                  jintrac_env, run_root, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, 'foo/bar')

        artifacts = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['artifacts'][0]

        assert artifacts['mountpoint'] == 'bar:/jetto/runs/prom'

    def test_job_labels_app_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                               run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        labels = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['labels']

        assert labels['app'] == 'jintrac'

    def test_job_labels_fullpath_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                    run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        labels = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['labels']

        assert labels['fullpath'] == str(run_root / rundir)

    def test_job_labels_codeid_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                  run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        labels = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['labels']

        assert labels['codeid'] == 'jetto'

    def test_job_output_dirs_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        job_ = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]

        assert job_['outputDirs'] == [rundir + '/$pointdir']

    def test_job_output_dirs_for_nested_rundir(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                               run_root, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, 'foo/bar')

        job_ = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]

        assert job_['outputDirs'] == ['bar' + '/$pointdir']

    def test_job_policies_has_expected_value(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                             run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        job_ = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]

        assert job_['policies'] == {'maximumTimeInQueue': 7 * 24 * 60, 'leaveInQueue': True, 'autoScalingType': None}

    def test_workflow_includes_factory(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                       run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        workflow = mock_prominence_client.create_workflow.call_args[0][0]

        assert 'factories' in workflow

    def test_workflow_contains_single_factory(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                              run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        workflow = mock_prominence_client.create_workflow.call_args[0][0]

        assert isinstance(workflow['factories'], list) and len(workflow['factories']) == 1

    def test_workflow_factory_type_is_zip(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                          run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        factory = mock_prominence_client.create_workflow.call_args[0][0]['factories'][0]

        assert factory['type'] == 'zip'

    def test_workflow_factory_has_two_parameters(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                   run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        parameters = mock_prominence_client.create_workflow.call_args[0][0]['factories'][0]['parameters']

        assert len(parameters) == 2

    def test_workflow_factory_name_is_same_as_workflow(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                       run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        workflow = mock_prominence_client.create_workflow.call_args[0][0]
        factory = workflow['factories'][0]

        assert factory['name'] == workflow['name']

    def test_workflow_factory_job_name_is_same_as_workflow(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                           run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        workflow = mock_prominence_client.create_workflow.call_args[0][0]
        factory = workflow['factories'][0]

        assert factory['jobs'] == [workflow['jobs'][0]['name']]

    def test_workflow_factory_workdir_parameter_name(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                     run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        parameter = mock_prominence_client.create_workflow.call_args[0][0]['factories'][0]['parameters'][0]

        assert parameter['name'] == 'workdir'

    def test_workflow_factory_workdir_parameter_values(self, mock_prominence, manager, mock_scan_config,
                                                       jintrac_env, run_root, rundir, mock_prominence_client,
                                                       mock_export):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        expected_values = [os.path.join('prom', os.path.basename(path)) for path in mock_export(None, rundir)]
        parameter = mock_prominence_client.create_workflow.call_args[0][0]['factories'][0]['parameters'][0]

        assert parameter['values'] == expected_values

    def test_workflow_factory_pointdir_parameter_name(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                      run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        parameter = mock_prominence_client.create_workflow.call_args[0][0]['factories'][0]['parameters'][1]

        assert parameter['name'] == 'pointdir'

    def test_workflow_factory_pointdir_parameter_values(self, mock_prominence, manager, mock_scan_config,
                                                        jintrac_env, run_root, rundir, mock_prominence_client,
                                                        mock_export):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        expected_values = [os.path.basename(path) for path in mock_export(None, rundir)]
        parameter = mock_prominence_client.create_workflow.call_args[0][0]['factories'][0]['parameters'][1]

        assert parameter['values'] == expected_values

    def test_workflow_factory_notifications_have_expected_value(self, mock_prominence, manager, mock_scan_config,
                                                                jintrac_env, run_root, rundir, mock_prominence_client,
                                                                mock_export):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        notifications = mock_prominence_client.create_workflow.call_args[0][0]['factories'][0]['notifications']

        assert notifications == [{'event': 'jobFinished', 'type': 'email'}]

    def test_prominence_workflow_id_is_returned(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                run_root, rundir, mock_prominence_client):
        mock_prominence_client.create_workflow.return_value = 1234

        id = manager.submit_job_to_prominence(mock_scan_config, rundir)

        assert id == 1234

    def test_creates_file_recording_workflow_id(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                                run_root, rundir, mock_prominence_client):
        mock_prominence_client.create_workflow.return_value = 1234

        _ = manager.submit_job_to_prominence(mock_scan_config, rundir)

        assert (run_root / rundir / 'remote.jobid').read_text() == 'Job submitted with id 1234\n'

    def test_workflow_name_same_as_job_name(self, mock_prominence, manager, mock_scan_config, jintrac_env,
                                            run_root, rundir, mock_prominence_client):
        manager.submit_job_to_prominence(mock_scan_config, rundir)

        workflow_name = mock_prominence_client.create_workflow.call_args[0][0]['name']
        job_name = mock_prominence_client.create_workflow.call_args[0][0]['jobs'][0]['name']

        assert workflow_name == job_name


@pytest.fixture()
def mock_docker_client():
    return mock.Mock(spec=docker.client.DockerClient)


@pytest.fixture()
def mock_docker(mock_docker_client):
    with mock.patch('docker.from_env',
                    autospec=docker.from_env) as _fixture:
        _fixture.return_value = mock_docker_client
        yield _fixture

class TestSubmitSingleRunToDocker:
    """Test that we can submit a JETTO job to a local Docker system"""
    @pytest.fixture()
    def export(self):
        """Create three job files in the export directory"""
        def _fixture(path):
            for i in range(3):
                with open(os.path.join(path, f'file{i}.txt'), 'w') as f:
                    pass

        return _fixture

    def compare_dirs(self, original, tarball):
        result = True
        cmp = filecmp.dircmp(original, tarball)

        if cmp.common == cmp.right_list:
            for file in cmp.common:
                first_file = os.path.join(original, file)
                second_file = os.path.join(tarball, file)
                if not filecmp.cmp(first_file, second_file, shallow=False):
                    result = False
        else:
            result = False
        return result

    def test_docker_client_created(self, mock_docker, mock_docker_client, manager, mock_config, jintrac_env,
                                         rundir, rundir_path, run_root):
        manager.submit_job_to_docker(mock_config, rundir_path)

        mock_docker.assert_called_once()

    def test_docker_container_run_called(self, mock_docker, mock_docker_client, manager, mock_config, jintrac_env,
                                      rundir, rundir_path, run_root):
        manager.submit_job_to_docker(mock_config, rundir_path)

        mock_docker_client.containers.run.assert_called_once()


class TestJob:
    @pytest.fixture
    def rundir(self, tmpdir):
        return tmpdir.mkdir('point_000')

    @pytest.fixture(autouse=True)
    def serialisation(self, rundir):
        f = rundir.join('serialisation.json')
        f.write(json.dumps({'foo': 'bar'}))

        return f

    @pytest.fixture(autouse=True)
    def llcmddbg(self, rundir, id):
        f = rundir.join('.llcmd.dbg')
        f.write(f'Your job {id} ("jetto.point00000") has been submitted')

        return f

    def test_raises_if_rundir_does_not_exist(self, rundir):
        rundir.remove()

        with pytest.raises(jetto_tools.job.JobError):
            _ = job.Job(rundir.strpath)

    def test_rundir_property(self, rundir):
        job_under_test = job.Job(rundir.strpath)

        assert job_under_test.rundir == rundir.strpath

    @pytest.fixture
    def id(self):
        return 12345

    def test_job_id_is_none_if_llcmd_dbg_not_found(self, rundir, llcmddbg):
        llcmddbg.remove()

        job_under_test = job.Job(rundir.strpath)

        assert job_under_test.id is None

    def test_job_id_is_retrieved_from_lldbg_file(self, rundir, id):
        job_under_test = job.Job(rundir.strpath)

        assert job_under_test.id == id

    def test_job_raises_if_llcmd_dbg_does_not_contain_id(self, rundir, llcmddbg):
        llcmddbg.write('foo')

        with pytest.raises(job.JobError):
            _ = job.Job(rundir.strpath)

    @pytest.fixture
    def jetto_out(self, rundir):
        f = rundir.join('jetto.out')
        f.write('\n'
                ' ... Terminating successfully\n'
                '\n')

        return f

    def test_job_status_unknown(self, rundir, llcmddbg, jetto_out):
        jetto_out.remove()

        job_under_test = job.Job(rundir.strpath)

        assert job_under_test.status() == job.Status.UNKNOWN

    def test_job_status_failed(self, rundir, jetto_out):
        jetto_out.write('')

        job_under_test = job.Job(rundir.strpath)

        assert job_under_test.status() == job.Status.FAILED

    def test_job_status_successful(self, rundir, jetto_out):
        job_under_test = job.Job(rundir.strpath)

        assert job_under_test.status() == job.Status.SUCCESSFUL

    def test_serialisation_property(self, rundir, serialisation):
        with open(serialisation) as f:
            d = json.loads(f.read())
        job_under_test = job.Job(rundir.strpath)

        assert job_under_test.serialisation == d

    def test_serialisation_is_none_if_not_found(self, rundir, serialisation):
        serialisation.remove()
        job_under_test = job.Job(rundir.strpath)

        assert job_under_test.serialisation is None

    def test_raises_if_serialisation_not_loaded(self, rundir, serialisation):
        serialisation.write('foo')

        with pytest.raises(job.JobError):
            _ = job.Job(rundir.strpath)


class TestRetrieveJobs:
    @pytest.fixture()
    def pointdirs(self, run_root):
        dirs = [run_root / f'point_00{i}' for i in range(1, 4)]
        _ = [d.mkdir() for d in dirs]

        return [str(d) for d in dirs]

    def test_returns_jobs_from_point_dirs(self, run_root, pointdirs):
        jobs = job.retrieve_jobs(str(run_root))

        assert [j.rundir for j in jobs] == pointdirs

    def test_raises_if_no_point_directories_found(self, run_root):
        with pytest.raises(job.JobError):
            _ = job.retrieve_jobs(run_root)

    def test_raises_if_any_job_creation_fails(self, run_root, pointdirs, mocker):
        mock = mocker.patch('jetto_tools.job.retrieve_jobs')
        mock.side_effect = jetto_tools.job.JobError

        with pytest.raises(jetto_tools.job.JobError):
            _ = job.retrieve_jobs(run_root)
