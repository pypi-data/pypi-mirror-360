from jetto_tools.jset import JSET, JSETError, _DEFAULT_DATE, _DEFAULT_TIME, ExtraNamelistsError,\
    ExtraNamelistItem, ExtraNamelists, Driver
from collections import namedtuple
from unittest import mock
import pytest
import datetime
import copy
import os.path
import numpy as np

import jetto_tools.common as common
from jetto_tools.common import IMASDB, CatalogueId


_JSET_SETTING_FMT = '{:60}: {}'

_HEADER = """!===============================================================================
!                              JETTO SETTINGS FILE
!==============================================================================="""

_DETAILS_SECTION = """*
*File Details"""

_SETTINGS_SECTION = """*
*Settings"""

_EOF_SECTION = """*
*EOF"""

_NAME = '/path/to/file.jset'
_DATE = '06/06/2020'
_TIME = '11:22:33'
_VERSION = 'v101219'

_STRING = 'foo'
_INT = 1729
_FLOAT = 3.14159
_TRUE = 'true'
_FALSE = 'false'
_MISSING = ''
_EXFILE_PATH = '/u/fcasson/cmg/jams/data/exfile/testdata4.ex'

_test_string = f"""{_HEADER}
{_DETAILS_SECTION}
Creation Name                                               : {_NAME}
Creation Date                                               : {_DATE}
Creation Time                                               : {_TIME}
Version                                                     : {_VERSION}
{_SETTINGS_SECTION}
AdvancedPanel.selReadContinue                               : false
AdvancedPanel.selReadRepeat                                 : false
AdvancedPanel.selReadRestart                                : false
EquilEscoRefPanel.tvalue.tinterval.endRange                 : 10.0
EquilEscoRefPanel.tvalue.tinterval.numRange                 : 0
EquilEscoRefPanel.tvalue.tinterval.startRange               : 0.0
ImpOptionPanel.select                                       : true
ImpOptionPanel.source                                       : Sanco
JobProcessingPanel.driver                                   : Standard, native I/O only
JobProcessingPanel.name                                     : v060619
JobProcessingPanel.numProcessors                            : 2
JobProcessingPanel.runDirNumber                             : testdata
JobProcessingPanel.selIdsRunid                              : false
JobProcessingPanel.userid                                   : sim
JobProcessingPanel.wallTime                                 : 2
OutputExtraNamelist.selItems.columns                        : 3
OutputExtraNamelist.selItems.rows                           : 0
OutputExtraNamelist.select                                  : false
OutputStdPanel.numOfProfileRangeTimes                       : 0
OutputStdPanel.profileFixedTimes[0]                         : 0
OutputStdPanel.profileFixedTimes[1]                         : 1
OutputStdPanel.profileFixedTimes[2]                         : 2
OutputStdPanel.profileFixedTimes[3]                         : 3
OutputStdPanel.profileFixedTimes[4]                         : 4
OutputStdPanel.profileFixedTimes[5]                         : 5
OutputStdPanel.profileFixedTimes[6]                         : 6
OutputStdPanel.profileFixedTimes[7]                         : 7
OutputStdPanel.profileFixedTimes[8]                         : 8
OutputStdPanel.profileFixedTimes[9]                         : 9
OutputStdPanel.profileRangeEnd                              : 10.0
OutputStdPanel.profileRangeStart                            : 0.0
OutputStdPanel.selectProfiles                               : true
SancoOutputExtraNamelist.selItems.columns                   : 3
SancoOutputExtraNamelist.selItems.rows                      : 0
SancoOutputExtraNamelist.select                             : false
SetUpPanel.endTime                                          : 10.0
SetUpPanel.exFileCatCodeID                                  : jetto
SetUpPanel.exFileCatDateID                                  : dec0417
SetUpPanel.exFileCatMachID                                  : jet
SetUpPanel.exFileCatOwner                                   : fcasson
SetUpPanel.exFileCatSeqNum                                  : 2
SetUpPanel.exFileCatShotID                                  : 92398
SetUpPanel.exFileName                                       : {_EXFILE_PATH}
SetUpPanel.exFileOldSource                                  : Private
SetUpPanel.exFilePathName                                   : 
SetUpPanel.exFilePrvDir                                     : /u/fcasson/cmg/jams/data/exfile
SetUpPanel.exFileSource                                     : Private
SetUpPanel.idsFileCatCodeID                                 : jetto
SetUpPanel.idsFileCatDateID                                 : jan0101
SetUpPanel.idsFileCatMachID                                 : jet
SetUpPanel.idsFileCatOwner                                  : sim
SetUpPanel.idsFileCatSeqNum                                 : 2
SetUpPanel.idsFileCatShotID                                 : 12345
SetUpPanel.idsFileName                                      : 
SetUpPanel.idsFilePrvDir                                    : 
SetUpPanel.idsFileSource                                    : Private
SetUpPanel.idsIMASDBMachine                                 : iter
SetUpPanel.idsIMASDBRunid                                   : 3
SetUpPanel.idsIMASDBShot                                    : 88888
SetUpPanel.idsIMASDBUser                                    : foo
SetUpPanel.machine                                          : west
SetUpPanel.selReadIds                                       : false
SetUpPanel.shotNum                                          : 0
SetUpPanel.startTime                                        : 0.0
panel1.false_param                                          : {_FALSE}
panel1.float_param                                          : {_FLOAT}
panel1.int_param                                            : {_INT}
panel1.missing_param                                        : {_MISSING}
panel1.string_param                                         : {_STRING}
panel1.true_param                                           : {_TRUE}
{_EOF_SECTION}
"""


def remove_jset_setting(prefix):
    return '\n'.join(
        s for s in _test_string.split('\n') if not s.startswith(prefix))


@pytest.fixture(scope='function')
def jset():
    return JSET(_test_string)


class TestJSETRetrieve:
    """Test that we can retrieve values from a parsed JSET"""

    def test_can_retrieve_creation_name(self, jset):
        assert jset.cname == _NAME

    def test_can_retrieve_version(self, jset):
        assert jset.version == _VERSION

    def test_can_retrieve_version_as_date(self, jset):
        assert jset.version_as_date == datetime.date(year=2019, month=12, day=10)

    def test_can_retrieve_non_standard_version_as_date(self, jset):
        jset.version = 'v191219_addons8'

        assert jset.version_as_date == datetime.date(year=2019, month=12, day=19)

    def test_version_as_date_fails_if_parse_failure(self, jset):
        jset.version = 'foo'

        assert jset.version_as_date is None

    def test_can_retrieve_string_setting(self, jset):
        assert jset['panel1.string_param'] == _STRING

    def test_can_retrieve_integer_setting(self, jset):
        assert jset['panel1.int_param'] == _INT

    def test_can_retrieve_float_setting(self, jset):
        assert jset['panel1.float_param'] == _FLOAT

    def test_can_retrieve_true_setting(self, jset):
        assert jset['panel1.true_param'] is True

    def test_can_retrieve_false_setting(self, jset):
        assert jset['panel1.false_param'] is False

    def test_can_retrieve_missing_setting(self, jset):
        assert jset['panel1.missing_param'] is None

    def test_can_check_if_setting_exists(self, jset):
        assert 'panel1.string_param' in jset

    def test_can_check_if_setting_does_not_exist(self, jset):
        assert 'panel1.nonexistent_param' not in jset

    def test_can_retrieve_creation_date(self, jset):
        assert jset.cdate == datetime.date(year=2020, month=6, day=6)

    def test_can_retrieve_creation_time(self, jset):
        assert jset.ctime == datetime.time(hour=11, minute=22, second=33)

    def test_can_retrieve_binary_version(self, jset):
        assert jset.binary == 'v060619'

    def test_can_retrieve_userid(self, jset):
        assert jset.userid == 'sim'

    def test_can_retrieve_processors(self, jset):
        assert jset.processors == 2

    def test_can_retrieve_impurities(self, jset):
        assert jset.impurities is True

    def test_can_retrieve_sanco_source(self, jset):
        assert jset.sanco is True

    def test_can_retrieve_run_dir(self, jset):
        assert jset.rundir == 'testdata'

    def test_can_retrieve_walltime(selfself, jset):
        assert jset.walltime == 2

    def test_walltime_returns_none_if_missing(self):
        jset_string = '\n'.join(s for s in _test_string.split('\n') if not s.startswith('JobProcessingPanel.wallTime'))
        jset = JSET(jset_string)

        assert jset.walltime is None

    def test_raises_if_nonexistent_setting_is_accessed(self, jset):
        with pytest.raises(JSETError):
            _ = jset['panel1.nonexistent_param']

    def test_cannot_delete_setting(self, jset):
        with pytest.raises(JSETError):
            del jset['panel1.string_param']

    @pytest.mark.parametrize('property', ['restart', 'continue_', 'repeat'])
    def test_can_retrieve_advanced_property(self, jset, property):
        assert getattr(jset, property) is False

    @pytest.mark.parametrize('name, property', [('selReadRestart', 'restart'),
                                                ('selReadContinue', 'continue_'),
                                                ('selReadRepeat', 'repeat')],
                             ids=['Restart', 'Continue', 'Repeat'])
    def test_advanced_property_returns_false_if_missing(self, name, property):
        jset_string = remove_jset_setting(f'AdvancedPanel.{name}')
        jset = JSET(jset_string)

        assert getattr(jset, property) is False


class TestJSETUpdate:
    """Test that we can make updates to a parsed JSET"""

    def test_can_update_existing_setting(self, jset):
        jset['panel1.string_param'] = 'bar'

        assert jset['panel1.string_param'] == 'bar'

    def test_cannot_update_nonexistent_setting(self, jset):
        with pytest.raises(JSETError):
            jset['panel1.nonexistent_param'] = 1

    def test_can_update_impurities(self, jset):
        jset.impurities = False

        assert jset.impurities is False

    def test_sanco_source_cannot_be_updated(self, jset):
        with pytest.raises(JSETError):
            jset.sanco = False

    def test_rundir_can_be_updated(self, jset):
        jset.rundir = 'foo/bar'

        assert jset.rundir == 'foo/bar'

    @pytest.mark.parametrize('property', ['restart', 'continue_', 'repeat'])
    def test_advanced_property_can_be_updated(self, jset, property):
        setattr(jset, property, True)

        assert getattr(jset, property) is True

    @pytest.mark.parametrize('property', ['restart', 'continue_', 'repeat'])
    def test_raises_if_advanced_property_is_not_boolean(self, jset, property):
        with pytest.raises(JSETError):
            setattr(jset, property, 'foo')

    @pytest.mark.parametrize('name, property', [('selReadRestart', 'restart'),
                                                ('selReadContinue', 'continue_'),
                                                ('selReadRepeat', 'repeat')],
                             ids=['Restart', 'Continue', 'Repeat'])
    def test_adds_advanced_panel_field_if_missing(self, jset, name, property):
        jset_string = remove_jset_setting(f'AdvancedPanel.{name}')
        jset = JSET(jset_string)

        setattr(jset, property, True)

        assert f'AdvancedPanel.{name}' in jset

    def test_walltime_can_be_updated(self, jset):
        jset.walltime = 3

        assert jset.walltime == 3

    def test_walltime_is_added_if_missing(self):
        jset_string = '\n'.join(s for s in _test_string.split('\n') if not s.startswith('JobProcessingPanel.wallTime'))
        jset = JSET(jset_string)

        jset.walltime = 1.0

        assert 'JobProcessingPanel.wallTime' in jset


class TestJSETWrite:
    """Test that the JSET has the expected content when written to a string"""
    @staticmethod
    def extract_jset_field(setting: str, s: str):
        """Utility function to extract settings from a formatted JSET string"""
        for line in s.split('\n'):
            if line.startswith(setting):
                return line.split(':', 1)[1].strip()
        return ''

    def test_unmodified_jset_has_identical_string(self, jset):
        assert str(jset) == _test_string

    def test_string_setting_is_updated(self, jset):
        jset['panel1.string_param'] = 'bar'

        assert self.extract_jset_field('panel1.string_param', str(jset)) == 'bar'

    def test_int_setting_is_updated(self, jset):
        jset['panel1.int_param'] = 2

        assert self.extract_jset_field('panel1.int_param', str(jset)) == '2'

    def test_float_setting_is_updated(self, jset):
        jset['panel1.float_param'] = 2.718

        assert self.extract_jset_field('panel1.float_param', str(jset)) == '2.718'

    def test_bool_setting_is_updated(self, jset):
        jset['panel1.true_param'] = False

        assert self.extract_jset_field('panel1.true_param', str(jset)) == 'false'

    def test_missing_setting_is_updated(self, jset):
        jset['panel1.int_param'] = None

        assert self.extract_jset_field('panel1.int_param', str(jset)) == ''

    def test_name_detail_is_updated(self, jset):
        jset.cname = '/path/to/other/file.jset'

        assert self.extract_jset_field('Creation Name', str(jset)) == '/path/to/other/file.jset'

    def test_date_detail_is_updated(self, jset):
        jset.cdate = datetime.date(year=2020, month=2, day=3)

        assert self.extract_jset_field('Creation Date', str(jset)) == '03/02/2020'

    def test_time_detail_is_updated(self, jset):
        jset.ctime = datetime.time(hour=4, minute=5, second=6)

        assert self.extract_jset_field('Creation Time', str(jset)) == '04:05:06'

    def test_version_detail_is_updated(self, jset):
        jset.version = 'vaabbcc'

        assert self.extract_jset_field('Version', str(jset)) == 'vaabbcc'

    def test_binary_is_updated(self, jset):
        jset.binary = 'v012345'

        assert self.extract_jset_field('JobProcessingPanel.name', str(jset)) == jset.binary

    def test_userid_is_updated(self, jset):
        jset.userid = 'foo'

        assert self.extract_jset_field('JobProcessingPanel.userid', str(jset)) == jset.userid

    def test_processors_is_updated(self, jset):
        jset.processors = 3

        assert self.extract_jset_field('JobProcessingPanel.numProcessors', str(jset)) == str(jset.processors)

    def test_impurities_select_is_updated(self, jset):
        jset.impurities = False

        assert self.extract_jset_field('ImpOptionPanel.select', str(jset)) == 'false'

    def test_rundir_is_updated(self, jset):
        jset.rundir = 'foo/bar'

        assert self.extract_jset_field('JobProcessingPanel.runDirNumber', str(jset)) == 'foo/bar'

    def test_restart_is_updated(self, jset):
        jset.restart = True

        assert self.extract_jset_field('AdvancedPanel.selReadRestart', str(jset)) == 'true'

    def test_walltime_is_updated(self, jset):
        jset.walltime = 3

        assert self.extract_jset_field('JobProcessingPanel.wallTime', str(jset)) == '3'


@pytest.fixture(scope='function')
def array_jset():
    len_eof = len(_EOF_SECTION) + 1
    extra_string = '\n'.join([
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[0].tpoly.select[0]', 'false'),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[0].tpoly.select[1]', 'false'),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[0].tpoly.time[0]', ''),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[0].tpoly.time[1]', ''),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[0].tpoly.value[0][0]', ''),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[0].tpoly.value[1][0]', ''),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[1].tpoly.select[0]', 'false'),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[1].tpoly.select[1]', 'false'),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[1].tpoly.time[0]', ''),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[1].tpoly.time[1]', ''),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[1].tpoly.value[0][0]', ''),
        _JSET_SETTING_FMT.format('BoundCondPanel.ionDens[1].tpoly.value[1][0]', ''),
        _JSET_SETTING_FMT.format('EquationsPanel.ionDens[0].fraction', '1.0'),
        _JSET_SETTING_FMT.format('EquationsPanel.ionDens[0].mass', '2.0'),
        _JSET_SETTING_FMT.format('EquationsPanel.ionDens[0].select', 'false'),
        _JSET_SETTING_FMT.format('EquationsPanel.ionDens[0].usage', 'Interpretive'),
        _JSET_SETTING_FMT.format('EquationsPanel.ionDens[1].fraction', '0.0'),
        _JSET_SETTING_FMT.format('EquationsPanel.ionDens[1].mass', '3.0'),
        _JSET_SETTING_FMT.format('EquationsPanel.ionDens[1].select', 'false'),
        _JSET_SETTING_FMT.format('EquationsPanel.ionDens[1].usage', 'Off'),
        _JSET_SETTING_FMT.format('ImpOptionPanel.impuritySelect[0]', 'true'),
        _JSET_SETTING_FMT.format('ImpOptionPanel.impuritySelect[1]', 'true'),
        _JSET_SETTING_FMT.format('SancoICZRefPanel.Species1Abundance', '1.0'),
        _JSET_SETTING_FMT.format('SancoICZRefPanel.Species1SOLDecayLength', '1.0'),
        _JSET_SETTING_FMT.format('SancoICZRefPanel.Species2Abundance', '0.01'),
        _JSET_SETTING_FMT.format('SancoICZRefPanel.Species2SOLDecayLength', '1.0')
    ])
    _modified_string = _test_string[:-len_eof] + extra_string + '\n' + _EOF_SECTION
    return JSET(_modified_string)


class TestJSETArrayCollapse:
    """Test the function and recovery of collapsing JSET internal arrays"""

    @pytest.mark.parametrize('label, ndim', [
        ('BoundCondPanel.ionDens.tpoly.select', 2),
        ('BoundCondPanel.ionDens.tpoly.value', 3),
        ('EquationsPanel.ionDens.mass', 1),
        ('SancoICZRefPanel.Species#Abundance', 1)
    ])
    def test_correct_labelling_and_dimension(self, array_jset, label, ndim):
        array_jset.collapse_all_arrays()
        
        assert np.array(array_jset[label]).ndim == ndim

    def test_equivalence_of_cyclic_operations(self, array_jset):
        new_jset = copy.deepcopy(array_jset)

        new_jset.collapse_all_arrays()
        new_jset.expand_all_arrays()

        assert all(new_jset[k] == array_jset[k] for k in array_jset._settings)

    def test_changes_to_collapsed_array_retained_when_expanding(self, array_jset):
        new_values = [1.5, 0.02]

        array_jset.collapse_all_arrays()
        array_jset['SancoICZRefPanel.Species#Abundance'] = new_values
        array_jset.expand_all_arrays()

        assert all(array_jset[f'SancoICZRefPanel.Species{i}Abundance'] == new_values[i-1] for i in (1, 2))

    def test_copy_last_entry_if_vector_has_too_few_elements(self, array_jset):
        new_values = [1.0]

        array_jset.collapse_all_arrays()
        array_jset['EquationsPanel.ionDens.mass'] = new_values
        array_jset.expand_all_arrays()

        assert all(array_jset[f'EquationsPanel.ionDens[{i}].mass'] == new_values[0] for i in (0, 1))

    def test_ignore_extra_entries_if_vector_has_too_many_elements(self, array_jset):
        new_values = [3.0, 2.0, 1.0]

        array_jset.collapse_all_arrays()
        array_jset['EquationsPanel.ionDens.mass'] = new_values
        array_jset.expand_all_arrays()

        assert all(array_jset[f'EquationsPanel.ionDens[{i}].mass'] == new_values[i] for i in (0, 1))

    def test_copy_into_elements_if_assigned_scalar_value(self, array_jset):
        new_values = None

        array_jset.collapse_all_arrays()
        array_jset['BoundCondPanel.ionDens.tpoly.select'] = new_values
        array_jset.expand_all_arrays()

        assert all(array_jset[f'BoundCondPanel.ionDens[{i}].tpoly.select[{j}]'] is None for i, j in ((0,0), (0,1), (1,0), (1,1)))

    def test_raises_if_assigned_empty_vector(self, array_jset):
        new_values = []

        array_jset.collapse_all_arrays()
        array_jset['BoundCondPanel.ionDens.tpoly.select'] = new_values

        with pytest.raises(IndexError):
            array_jset.expand_all_arrays()

    def test_reset_profile_output_times(self, array_jset):
        array_jset.collapse_all_arrays()
        array_jset.reset_fixed_output_profiles_times()

        assert all(t is None for t in array_jset['OutputStdPanel.profileFixedTimes'])

    @pytest.fixture
    def jset_with_1d_param(self):
        len_eof = len(_EOF_SECTION) + 1
        extra_string = '\n'.join([
            _JSET_SETTING_FMT.format('ECRHPanel.norm.value[0]', '0.0'),
            _JSET_SETTING_FMT.format('ECRHPanel.norm.value[1]', '1.0'),
            _JSET_SETTING_FMT.format('ECRHPanel.norm.value[2]', '2.0'),
        ])
        _modified_string = _test_string[:-len_eof] + extra_string + '\n' + _EOF_SECTION
        _jset = JSET(_modified_string)

        return _jset

    @pytest.fixture
    def jset_with_1d_param_collapsed(self, jset_with_1d_param):
        new_jset = copy.deepcopy(jset_with_1d_param)
        new_jset.collapse_all_arrays()

        return new_jset

    @pytest.mark.parametrize('index', range(3))
    def test_can_access_collapsed_1d_array_with_indexed_label(self, jset_with_1d_param, jset_with_1d_param_collapsed, index):
        assert jset_with_1d_param[f'ECRHPanel.norm.value[{index}]'] == \
               jset_with_1d_param_collapsed['ECRHPanel.norm.value'][index]

    @pytest.mark.parametrize('index', range(3))
    def test_can_modify_collapsed_1d_array_with_indexed_label(self, jset_with_1d_param, jset_with_1d_param_collapsed,
                                                              index):
        old = jset_with_1d_param[f'ECRHPanel.norm.value[{index}]']

        jset_with_1d_param_collapsed[f'ECRHPanel.norm.value[{index}]'] = old * 2

        assert jset_with_1d_param_collapsed[f'ECRHPanel.norm.value[{index}]'] == old * 2 and \
               jset_with_1d_param_collapsed[f'ECRHPanel.norm.value'][index] == old * 2

    @pytest.mark.parametrize('index', range(3))
    def test_in_range_collapsed_1d_array_index_is_in_jset(self, jset_with_1d_param_collapsed, index):
        assert f'ECRHPanel.norm.value[{index}]' in jset_with_1d_param_collapsed

    def test_out_of_range_collapsed_array_index_is_not_in_jset(self, jset_with_1d_param_collapsed):
        assert 'ECRHPanel.norm.value[3]' not in jset_with_1d_param_collapsed

    def test_cannot_access_parameter_which_is_not_collapsed_array(self, jset):
        with pytest.raises(JSETError):
            _ = jset['OutputStdPanel.profileRangeStart[0]']

    def test_cannot_modify_parameter_which_is_not_collapsed_array(self, jset):
        with pytest.raises(JSETError):
            jset['OutputStdPanel.profileRangeStart[0]'] = 0

    def test_cannot_access_collapsed_1d_array_with_invalid_index(self, jset_with_1d_param_collapsed):
        with pytest.raises(JSETError):
            _ = jset_with_1d_param_collapsed['ECRHPanel.norm.value[3]']

    def test_cannot_modify_collapsed_1d_array_with_invalid_index(self, jset_with_1d_param_collapsed):
        with pytest.raises(JSETError):
            jset_with_1d_param_collapsed['ECRHPanel.norm.value[3]'] = 0.0

    @pytest.fixture
    def jset_with_2d_param_collapsed(self, jset_with_1d_param):
        new_jset = copy.deepcopy(jset_with_1d_param)
        new_jset.collapse_all_arrays()

        return new_jset

    @pytest.fixture
    def jset_with_2d_param(self):
        len_eof = len(_EOF_SECTION) + 1
        extra_string = '\n'.join([
            _JSET_SETTING_FMT.format('FooPanel.Bar[0][0]', '0.0'),
            _JSET_SETTING_FMT.format('FooPanel.Bar[0][1]', '1.0'),
            _JSET_SETTING_FMT.format('FooPanel.Bar[1][0]', '2.0'),
            _JSET_SETTING_FMT.format('FooPanel.Bar[1][1]', '2.0'),
        ])
        _modified_string = _test_string[:-len_eof] + extra_string + '\n' + _EOF_SECTION
        _jset = JSET(_modified_string)

        return _jset

    @pytest.fixture
    def jset_with_2d_param_collapsed(self, jset_with_2d_param):
        new_jset = copy.deepcopy(jset_with_2d_param)
        new_jset.collapse_all_arrays()

        return new_jset

    @pytest.mark.parametrize('index_a, index_b', ((0, 0), (0, 1), (1, 0), (1, 1)))
    def test_can_access_collapsed_2d_array_with_indexed_label(self, jset_with_2d_param, jset_with_2d_param_collapsed, index_a, index_b):
        assert jset_with_2d_param[f'FooPanel.Bar[{index_a}][{index_b}]'] == \
               jset_with_2d_param_collapsed['FooPanel.Bar'][index_a][index_b]

    @pytest.mark.parametrize('index_a, index_b', ((0, 0), (0, 1), (1, 0), (1, 1)))
    def test_can_modify_collapsed_2d_array_with_indexed_label(self, jset_with_2d_param, jset_with_2d_param_collapsed,
                                                              index_a, index_b):
        old = jset_with_2d_param[f'FooPanel.Bar[{index_a}][{index_b}]']

        jset_with_2d_param_collapsed[f'FooPanel.Bar[{index_a}][{index_b}]'] = old * 2

        assert jset_with_2d_param_collapsed[f'FooPanel.Bar[{index_a}][{index_b}]'] == old * 2 and \
               jset_with_2d_param_collapsed[f'FooPanel.Bar'][index_a][index_b] == old * 2

    @pytest.mark.parametrize('index_a, index_b', ((0, 0), (0, 1), (1, 0), (1, 1)))
    def test_in_range_collapsed_2d_array_index_is_in_jset(self, jset_with_2d_param_collapsed, index_a, index_b):
        assert f'FooPanel.Bar[{index_a}][{index_b}]' in jset_with_2d_param_collapsed

    @pytest.fixture
    def jset_with_3d_param(self):
        len_eof = len(_EOF_SECTION) + 1
        extra_string = '\n'.join([
            _JSET_SETTING_FMT.format('FooPanel.Bar[0][0][0]', '0.0'),
            _JSET_SETTING_FMT.format('FooPanel.Bar[0][0][1]', '1.0'),
        ])
        _modified_string = _test_string[:-len_eof] + extra_string + '\n' + _EOF_SECTION
        _jset = JSET(_modified_string)

        return _jset

    @pytest.fixture
    def jset_with_3d_param_collapsed(self, jset_with_3d_param):
        new_jset = copy.deepcopy(jset_with_3d_param)
        new_jset.collapse_all_arrays()

        return new_jset

    def test_disallow_access_to_collapsed_3d_array_with_indexed_label(self, jset_with_3d_param_collapsed):
        with pytest.raises(JSETError):
            _ = jset_with_3d_param_collapsed['FooPanel.Bar[0][0][0]']

# The following convenience which are used in the subsequent tests to easily manipulate portions of a JSET file string,
# via the magic of namedtuples. This allows us to exercise the exception-handling aspects of the JSET module


JSETDetailsTuple = namedtuple('JSETDetailsTuple', ['name', 'date', 'time', 'version', 'extra'])
JSETDetailsTuple.__new__.__defaults__ = (
    _JSET_SETTING_FMT.format('Creation Name', _NAME),
    _JSET_SETTING_FMT.format('Creation Date', _DATE),
    _JSET_SETTING_FMT.format('Creation Time', _TIME),
    _JSET_SETTING_FMT.format('Version', _VERSION),
    '')


class JSETDetails(JSETDetailsTuple):
    def as_string(self):
        """Concatenate the details into the details section"""
        return '\n'.join([self._asdict()[f] for f in self._fields if f])


JSETSettingsTuple = namedtuple('JSETSettingsTuple', ['panel_string', 'panel_int', 'panel_float', 'panel_true',
                               'panel_false', 'panel_missing'])
JSETSettingsTuple.__new__.__defaults__ = (_STRING, _INT, _FLOAT, _TRUE, _FALSE, _MISSING)


class JSETSettings(JSETSettingsTuple):
    def as_string(self):
        """Concatenate the settings into the settings section"""
        s = '\n'.join([_JSET_SETTING_FMT.format(f, str(self._asdict()[f]).lower()) for f in self._fields])
        return s


JSETExtraNamelistsFilterTuple = namedtuple('JSETExtraNamelistsFilterTuple', ['active', 'model', 'namelist'])
JSETExtraNamelistsFilterTuple.__new__.__defaults__ = ('All', 'All', 'All')

JSETExtraNamelistsTuple = namedtuple('JSETExtraNamelistsTuple', ['enable', 'select', 'rows', 'columns', 'filter'])
JSETExtraNamelistsTuple.__new__.__defaults__ = (True, 'true', 0, 3, None)


class JSETJettoExtraNamelists(JSETExtraNamelistsTuple):
    def as_string(self):
        if self.enable:
            s = '\n'.join([_JSET_SETTING_FMT.format('OutputExtraNamelist.select', self.select),
                           _JSET_SETTING_FMT.format('OutputExtraNamelist.selItems.rows', self.rows),
                           _JSET_SETTING_FMT.format('OutputExtraNamelist.selItems.columns', self.columns)])
            if self.filter is not None:
                s += '\n' + '\n'.join(
                    [_JSET_SETTING_FMT.format('OutputExtraNamelist.filter.active', self.filter.active),
                     _JSET_SETTING_FMT.format('OutputExtraNamelist.filter.model', self.filter.model),
                     _JSET_SETTING_FMT.format('OutputExtraNamelist.filter.namelist', self.filter.namelist)])
            
            return s
    
        return ''


class JSETSancoExtraNamelists(JSETExtraNamelistsTuple):
    def as_string(self):
        if self.enable:
            s = '\n'.join([_JSET_SETTING_FMT.format('SancoOutputExtraNamelist.select', self.select),
                           _JSET_SETTING_FMT.format('SancoOutputExtraNamelist.selItems.rows', self.rows),
                           _JSET_SETTING_FMT.format('SancoOutputExtraNamelist.selItems.columns', self.columns)])
            if self.filter is not None:
                s += '\n' + '\n'.join([_JSET_SETTING_FMT.format('SancoOutputExtraNamelist.filter.active', self.filter.active),
                                       _JSET_SETTING_FMT.format('SancoOutputExtraNamelist.filter.model', self.filter.model),
                                       _JSET_SETTING_FMT.format('SancoOutputExtraNamelist.filter.namelist', self.filter.namelist)])

            return s
        
        return ''


JSETProcessorsTuple = namedtuple('JSETProcessorsTuple', ['processors'])
JSETProcessorsTuple.__new__.__defaults__ = (2, )


class JSETProcessors(JSETProcessorsTuple):
    def as_string(self):
        return _JSET_SETTING_FMT.format('JobProcessingPanel.numProcessors', self.processors)


JETTOFileTuple = namedtuple('JETTOFileTuple', ['panel', 'prefix', 'owner', 'code', 'machine', 'shot', 'date', 'seq',
                                               'source', 'name', 'prev_dir', 'file_flag'])
JETTOFileTuple.__new__.__defaults__ = ('', '', 'sim', 'jetto', 'jet', '92398', 'dec0417', '2',
                                       'Private', '/path/to/prev/dir/file.ext',
                                       '/path/to/prev/dir', True)


class JETTOFile(JETTOFileTuple):
    def as_string(self):
        # Hack to deal with JAMS inconsistency in file parameter naming
        if self.file_flag is True:
            file_name_postfix = 'File'
        else:
            file_name_postfix = ''

        s = '\n'.join([_JSET_SETTING_FMT.format('{}.{}CatCodeID'.format(self.panel, self.prefix), self.code),
                       _JSET_SETTING_FMT.format('{}.{}CatDateID'.format(self.panel, self.prefix), self.date),
                       _JSET_SETTING_FMT.format('{}.{}CatMachID'.format(self.panel, self.prefix), self.machine),
                       _JSET_SETTING_FMT.format('{}.{}CatOwner'.format(self.panel, self.prefix), self.owner),
                       _JSET_SETTING_FMT.format('{}.{}CatSeqNum'.format(self.panel, self.prefix), self.seq),
                       _JSET_SETTING_FMT.format('{}.{}CatShotID'.format(self.panel, self.prefix), self.shot),
                       _JSET_SETTING_FMT.format('{}.{}Source'.format(self.panel, self.prefix), self.source),
                       _JSET_SETTING_FMT.format('{}.{}{}Name'.format(self.panel, self.prefix, file_name_postfix), self.name),
                       _JSET_SETTING_FMT.format('{}.{}PrvDir'.format(self.panel, self.prefix), os.path.dirname(self.name))
                       ])
        return s


JSETExfileTuple = namedtuple('JSETExfileTuple', ['owner', 'code', 'machine', 'shot', 'date', 'seq',
                                                 'source', 'name', 'prev_dir'])
JSETExfileTuple.__new__.__defaults__ = ('fcasson', 'jetto', 'jet', '92398', 'dec0417', '2',
                                        'Private', '/u/fcasson/cmg/jams/data/exfile/testdata4.ex',
                                        '/path/to/prev/dir')


class JSETExfile(JSETExfileTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('SetUpPanel.exFileCatCodeID', self.code),
                       _JSET_SETTING_FMT.format('SetUpPanel.exFileCatDateID', self.date),
                       _JSET_SETTING_FMT.format('SetUpPanel.exFileCatMachID', self.machine),
                       _JSET_SETTING_FMT.format('SetUpPanel.exFileCatOwner', self.owner),
                       _JSET_SETTING_FMT.format('SetUpPanel.exFileCatSeqNum', self.seq),
                       _JSET_SETTING_FMT.format('SetUpPanel.exFileCatShotID', self.shot),
                       _JSET_SETTING_FMT.format('SetUpPanel.exFileSource', self.source),
                       _JSET_SETTING_FMT.format('SetUpPanel.exFileName', self.name),
                       _JSET_SETTING_FMT.format('SetUpPanel.exFilePrvDir', os.path.dirname(self.name))])
        return s

# class JSETExfile(JETTOFile):
#     def __new__(cls):
#         super().__new__(cls, panel='SetUpPanel', prefix='exFile')


JSETAdvancedTuple = namedtuple('JSETAdvancedTuple', ['owner', 'code', 'machine', 'shot', 'date', 'seq',
                                                     'owner_r', 'code_r', 'machine_r', 'shot_r', 'date_r', 'seq_r',
                                                     'continue_', 'repeat', 'restart'])
JSETAdvancedTuple.__new__.__defaults__ = ('fcasson', 'jetto', 'jet', '92398', 'dec0417', '2',
                                          'sim', 'edge2d', 'iter', '12345', 'dec1318', '3',
                                          'false', 'false', 'false')


class JSETAdvanced(JSETAdvancedTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('AdvancedPanel.catOwner', self.owner),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catCodeID', self.code),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catMachID', self.machine),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catShotID', self.shot),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catDateID', self.date),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catSeqNum', self.seq),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catOwner_R', self.owner_r),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catCodeID_R', self.code_r),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catMachID_R', self.machine_r),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catShotID_R', self.shot_r),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catDateID_R', self.date_r),
                       _JSET_SETTING_FMT.format('AdvancedPanel.catSeqNum_R', self.seq_r),
                       _JSET_SETTING_FMT.format('AdvancedPanel.selReadContinue', self.continue_),
                       _JSET_SETTING_FMT.format('AdvancedPanel.selReadRepeat', self.repeat),
                       _JSET_SETTING_FMT.format('AdvancedPanel.selReadRestart', self.restart),
                       ])
        return s


JSETImpuritiesTuple = namedtuple('JSETImpuritiesTuple', ['select', 'source'])
JSETImpuritiesTuple.__new__.__defaults__ = ('true', 'Sanco')


class JSETImpurities(JSETImpuritiesTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('ImpOptionPanel.select', self.select),
                       _JSET_SETTING_FMT.format('ImpOptionPanel.source', self.source)])
        return s


JSETSancoTuple = namedtuple('JSETSancoTuple', ['transport_select', 'grid_select'])
JSETSancoTuple.__new__.__defaults__ = ('true', 'true')


class JSETSanco(JSETSancoTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('SancoTransportPanel.transportFileSelect', self.transport_select),
                       _JSET_SETTING_FMT.format('SancoOtherPanel.selReadGridFile', self.grid_select), ])
        return s


JSETBinaryTuple = namedtuple('JSETBinaryTuple', ['binary', 'user'])
JSETBinaryTuple.__new__.__defaults__ = ('v060619', 'sim')


class JSETBinary(JSETBinaryTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('JobProcessingPanel.name ', self.binary)])
        return s


JSETEquilibriumTuple = namedtuple('JSETEquilibriumTuple', ['source', 'boundary'])
JSETEquilibriumTuple.__new__.__defaults__ = ('ESCO', 'EQDSK using FLUSH')


class JSETEquilibrium(JSETEquilibriumTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('EquilibriumPanel.source', self.source),
                       _JSET_SETTING_FMT.format('EquilEscoRefPanel.boundSource', self.source), ])

        return s


JSETWFTuple = namedtuple('JSETWFTuple', ['select', ])
JSETWFTuple.__new__.__defaults__ = ('true', )


class JSETWF(JSETWFTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('ExternalWFPanel.select', self.select), ])

        return s


JSETBoundCondTuple = namedtuple('JSETBoundCondTuple', ['faraday', 'current'])
JSETBoundCondTuple.__new__.__defaults__ = ('Current (amps)', 'From PPF', )


class JSETBoundCond(JSETBoundCondTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('BoundCondPanel.faradayOption', self.faraday),
                       _JSET_SETTING_FMT.format('BoundCondPanel.current', self.current), ])

        return s


JSETEquationsTuple = namedtuple('JSETEquationsTuple', ['usage'])
JSETEquationsTuple.__new__.__defaults__ = ('Predictive', )


class JSETEquations(JSETEquationsTuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('EquationsPanel.current.usage', self.usage), ])

        return s


JSETNBITuple = namedtuple('JSETNBITuple', ['select', 'source', 'ascot_source'])
JSETNBITuple.__new__.__defaults__ = ('true', 'Ascot', 'From File')


class JSETNBI(JSETNBITuple):
    def as_string(self):
        s = '\n'.join([_JSET_SETTING_FMT.format('NBIPanel.select', self.select),
                       _JSET_SETTING_FMT.format('NBIPanel.source', self.source),
                       _JSET_SETTING_FMT.format('NBIAscotRef.source', self.ascot_source), ])

        return s


JSETFileTuple = namedtuple('JSETFileTuple', ['header', 'details_section', 'details',
                                             'settings_section', 'settings', 'exfile',
                                             'binary', 'extra', 'sanco_extra', 'processors',
                                             'impurities', 'advanced', 'jetto_files',
                                             'equilibrium', 'wf', 'sanco', 'bound_cond',
                                             'equations', 'nbi', 'eof'])
JSETFileTuple.__new__.__defaults__ = (_HEADER, _DETAILS_SECTION, JSETDetails(),
                                      _SETTINGS_SECTION, JSETSettings(), JSETExfile(),
                                      JSETBinary(), JSETJettoExtraNamelists(), JSETSancoExtraNamelists(),
                                      JSETProcessors(), JSETImpurities(), JSETAdvanced(), [],
                                      JSETEquilibrium(), JSETWF(), JSETSanco(), JSETBoundCond(),
                                      JSETEquations(), JSETNBI(), _EOF_SECTION)


class JSETFile(JSETFileTuple):
    def as_string(self):
        """Concatenate the sections into the JSET file"""
        return '\n'.join([self.header,
                          self.details_section,
                          self.details.as_string(),
                          self.settings_section,
                          self.settings.as_string(),
                          self.exfile.as_string(),
                          self.binary.as_string(),
                          self.processors.as_string(),
                          self.extra.as_string(),
                          self.sanco_extra.as_string(),
                          self.impurities.as_string(),
                          self.advanced.as_string(),
                          '\n'.join([file.as_string() for file in self.jetto_files]),
                          self.equilibrium.as_string(),
                          self.wf.as_string(),
                          self.sanco.as_string(),
                          self.bound_cond.as_string(),
                          self.equations.as_string(),
                          self.nbi.as_string(),
                          self.eof])


class TestJSETSectionParsingFailure:
    """Test that exceptions are raised if the JSET input does not have the expected sections"""

    def test_does_not_raise_if_all_expected_sections_are_present(self):
        s = JSETFile().as_string()

        _ = JSET(s)

    def test_raises_if_details_section_missing(self):
        s = JSETFile(details_section='').as_string()

        with pytest.raises(JSETError):
            _ = JSET(s)

    def test_raises_if_settings_section_missing(self):
        s = JSETFile(settings_section='').as_string()

        with pytest.raises(JSETError):
            _ = JSET(s)

    def test_raises_if_eof_section_missing(self):
        s = JSETFile(eof='').as_string()

        with pytest.raises(JSETError):
            _ = JSET(s)

    def test_raises_if_extra_section_present(self):
        extra_section = ('*\n'
                         '*Extra\n')
        s = JSETFile().as_string() + extra_section

        with pytest.raises(JSETError):
            _ = JSET(s)


class TestJSETSettingsParsingError:
    """Test that exceptions are raised if the JSET 'Settings' section has invalid content"""

    def test_does_not_raise_if_settings_section_is_empty(self):
        class EmptySettings:
            def as_string(self):
                return ''
        jsetfile = JSETFile(settings=EmptySettings())

        _ = JSET(jsetfile.as_string())

    def test_raises_if_setting_cannot_be_parsed(self):
        class BadSettings:
            def as_string(self):
                return 'blah blah no colon blah blah'
        jsetfile = JSETFile(settings=BadSettings())

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_can_read_setting_with_whitespace_in_value(self):
        class WhiteSpaceSetting:
            def as_string(self):
                return 'BoundCondPanel.current.option  : Constant Value'
        jsetfile = JSETFile(settings=WhiteSpaceSetting())

        jset = JSET(jsetfile.as_string())

        assert jset['BoundCondPanel.current.option'] == 'Constant Value'

    def test_can_read_setting_with_brackets_in_name(self):
        class BracketsSetting:
            def as_string(self):
                return 'BoundCondPanel.current.tpoly.select[0] : false'
        jsetfile = JSETFile(settings=BracketsSetting())

        jset = JSET(jsetfile.as_string())

        assert jset['BoundCondPanel.current.tpoly.select[0]'] is False

    def test_can_read_setting_with_nonword_characters_in_name(self):
        class NonWordsSetting:
            def as_string(self):
                return 'TransportStdQLKDialog.Spatial smoothing (Chis+Ds 3pts) : true'
        jsetfile = JSETFile(settings=NonWordsSetting())

        jset = JSET(jsetfile.as_string())

        assert jset['TransportStdQLKDialog.Spatial smoothing (Chis+Ds 3pts)'] is True


class TestJSETFileDetailsParsingError:
    """Test that exceptions are raised if the JSET 'File Details' section has invalid content"""

    def test_raises_if_creation_name_line_is_missing(self):
        details = JSETDetails(name='')
        jsetfile = JSETFile(details=details)

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_raises_if_creation_date_line_is_missing(self):
        details = JSETDetails(date='')
        jsetfile = JSETFile(details=details)

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_raises_if_creation_time_line_is_missing(self):
        details = JSETDetails(time='')
        jsetfile = JSETFile(details=details)

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_raises_if_version_line_is_missing(self):
        details = JSETDetails(version='')
        jsetfile = JSETFile(details=details)

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_raise_if_date_cannot_be_parsed(self):
        details = JSETDetails(date='Creation Date : not-a-date')
        jsetfile = JSETFile(details=details)

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_raise_if_time_cannot_be_parsed(self):
        details = JSETDetails(time='Creation Time : not-a-time')
        jsetfile = JSETFile(details=details)

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_raise_if_unrecognised_detail_is_present(self):
        details = JSETDetails(extra='Extra field : foo')
        jsetfile = JSETFile(details=details)

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_raise_if_detail_cannot_be_parsed(self):
        details = JSETDetails(extra='blah blah no colon blah blah')
        jsetfile = JSETFile(details=details)

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())


class TestJSETReadEmptyDetails:
    """Test that the JSET parser will allow empty values in the File Details section"""
    def test_empty_creation_name_is_allowed(self):
        details = JSETDetails(name='Creation Name : ')
        jsetfile = JSETFile(details=details)

        jset = JSET(jsetfile.as_string())

        assert jset.cname == ''

    def test_empty_creation_date_is_allowed(self):
        details = JSETDetails(date='Creation Date : ')
        jsetfile = JSETFile(details=details)

        jset = JSET(jsetfile.as_string())

        assert jset.cdate == _DEFAULT_DATE

    def test_empty_creation_time_is_allowed(self):
        details = JSETDetails(time='Creation Time : ')
        jsetfile = JSETFile(details=details)

        jset = JSET(jsetfile.as_string())

        assert jset.ctime == _DEFAULT_TIME

    def test_empty_creation_version_is_allowed(self):
        details = JSETDetails(version='Version : ')
        jsetfile = JSETFile(details=details)

        jset = JSET(jsetfile.as_string())

        assert jset.version == ''


class TestExtraNamelistItemScalar:
    """Test creation and use of extra namelist items"""

    @pytest.fixture(params=[0, 1.5, 'foo', True, None], ids=['int', 'float', 'string', 'bool', 'None'])
    def scalar_value(self, request):
        return request.param

    def test_can_initialise_a_scalar_item(self, scalar_value):
        _ = ExtraNamelistItem(scalar_value)

    def test_raises_if_scalar_value_has_invalid_type(self):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem([])

    def test_is_scalar_returns_true_for_scalar_item(self, scalar_value):
        item = ExtraNamelistItem(scalar_value)

        assert item.is_scalar() is True

    def test_can_index_a_scalar_item_with_none(self, scalar_value):
        item = ExtraNamelistItem(scalar_value)

        assert item[None] == scalar_value

    def test_raises_if_index_a_scalar_item_with_int(self, scalar_value):
        item = ExtraNamelistItem(scalar_value)

        with pytest.raises(ExtraNamelistsError):
            _ = item[1]

    def test_raises_if_index_a_scalar_item_with_tuple(self, scalar_value):
        item = ExtraNamelistItem(scalar_value)

        with pytest.raises(ExtraNamelistsError):
            _ = item[1, 2]

    def test_type_returns_expected_value(self, scalar_value):
        item = ExtraNamelistItem(scalar_value)

        assert item.type() == type(scalar_value)

    def test_is_contiguous_raises_for_scalar_item(self):
        item = ExtraNamelistItem(0)

        with pytest.raises(ExtraNamelistsError):
            _ = item.is_contiguous()

    def test_can_set_value_of_scalar_item(self):
        item = ExtraNamelistItem(0)

        item[None] = 1

        assert item[None] == 1

    def test_as_list_raises_for_scalar_item(self):
        item = ExtraNamelistItem(0)

        with pytest.raises(ExtraNamelistsError):
            _ = item.as_list()

    def test_as_array_raises_for_scalar_item(self):
        item = ExtraNamelistItem(0)

        with pytest.raises(ExtraNamelistsError):
            _ = item.as_array()


class TestExtraNamelistItemVector:
    @pytest.fixture(params=[False, True], ids=['New', 'Old'])
    def style(self, request):
        def _style(v):
            if request.param:
                return v
            else:
                return [v]

        return _style

    @pytest.fixture(params=[2, 2.2, 'foo', False, None], ids=['int', 'float', 'string', 'bool', 'None'])
    def vector_param_single_value(self, request):
        return request.param

    def test_can_initialise_a_vector_item_with_a_single_value(self, vector_param_single_value, style):
        _ = ExtraNamelistItem(style(vector_param_single_value), 1)

    def test_can_retrieve_vector_item_value_via_index(self, vector_param_single_value, style):
        item = ExtraNamelistItem(style(vector_param_single_value), 1)

        assert item[1] == vector_param_single_value

    def test_is_scalar_returns_false_for_vector_item(self, vector_param_single_value, style):
        item = ExtraNamelistItem(style(vector_param_single_value), 1)

        assert item.is_scalar() is False

    def test_is_vector_returns_true_for_vector_item(self, vector_param_single_value, style):
        item = ExtraNamelistItem(style(vector_param_single_value), 1)

        assert item.is_vector() is True

    def test_is_contiguous_returns_true_for_single_element(self, style):
        item = ExtraNamelistItem(style(1), 1)

        assert item.is_contiguous() is True

    def test_is_contiguous_returns_true_for_multiple_elements(self, style):
        item = ExtraNamelistItem(style(1), 1)

        assert item.is_contiguous() is True

    def test_is_contiguous_returns_true(self, style):
        item = ExtraNamelistItem([1, 2, 3], 1)

        assert item.is_contiguous() is True

    def test_is_contiguous_returns_false(self):
        item = ExtraNamelistItem([1], 1)
        other_item = ExtraNamelistItem([3], 3)
        item.combine(other_item)

        assert item.is_contiguous() is False

    @pytest.mark.parametrize('invalid_index', [-1, 0], ids=['negative-index', 'zero-index'])
    def test_raises_if_index_is_invalid(self, invalid_index, vector_param_single_value, style):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem(vector_param_single_value, invalid_index)

    @pytest.fixture(params=[[1, 2, 3],
                            [1.1, 2.2, 3.3],
                            ['foo', 'bar', 'baz'],
                            [True, True, False],
                            [None, None, None]],
                    ids=['int', 'float', 'string', 'bool', 'None'])
    def vector_param_multiple_values(self, request):
        return request.param

    def test_can_initialise_vector_item_with_multiple_values(self, vector_param_multiple_values):
        _ = ExtraNamelistItem(vector_param_multiple_values, 1)

    def test_can_retrieve_from_multiple_values_by_index(self, vector_param_multiple_values):
        item = ExtraNamelistItem(vector_param_multiple_values, 1)

        assert item[1] == vector_param_multiple_values[0] and \
               item[2] == vector_param_multiple_values[1] and \
               item[3] == vector_param_multiple_values[2]

    def test_raises_if_vector_item_has_empty_value(self):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem([], 1)

    def test_raises_if_vector_item_has_invalid_types(self):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem([{}], 1)

    @pytest.mark.parametrize('value, type_', ([[0], int],
                                             [(1.1, 2.2), float],
                                             [('Three', 'Four', 'Five'), str],
                                             [(True, False, True, True, True), bool],
                                             [(0, 1.0), float],
                                             ))
    def test_type_returns_expected_value(self, value, type_):
        item = ExtraNamelistItem(value)

        assert item.type() == type_

    @pytest.fixture(params=[['a', 'b', 3.0],
                            [1, 2, True],
                            ['foo', False, 'bar'],
                            ['bar', False, False]],
                    ids=['float-in-strings',
                         'bool-in-int',
                         'bool-in-strings',
                         'string-in-bools'])
    def inconsistent_types(self, request):
        return request.param

    def test_raises_if_vector_value_has_inconsistent_types(self, inconsistent_types):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem(inconsistent_types)

    @pytest.mark.parametrize('compatible_types', ([1.0, 2, 3.0, 4.0], [1, 2.0, 3, 4]))
    def test_compatible_numeric_types_are_allowed(self, compatible_types):
        _ = ExtraNamelistItem(compatible_types)

    @pytest.mark.parametrize('value', [[1, None],
                                       [None, 1.1],
                                       ['foo', None, 'bar'],
                                       [True, True, None, False]],
                    ids=['with-int',
                         'with-float',
                         'with-str',
                         'with-bool'])
    def test_can_include_none_with_other_consistent_types(self, value):
        _ = ExtraNamelistItem(value)

    def test_raises_if_access_with_invalid_index(self):
        item = ExtraNamelistItem([1, 2, 3], 1)

        with pytest.raises(ExtraNamelistsError):
            _ = item[4]

    def test_can_set_value_of_existing_index(self):
        item = ExtraNamelistItem([1, 2, 3], 1)

        item[1] = 4

        assert item[1] == 4

    def test_cannot_set_value_of_existing_index_to_none(self):
        item = ExtraNamelistItem([1, 2, 3], 1)

        with pytest.raises(ExtraNamelistsError):
            item[1] = None

    def test_can_add_value_with_new_index(self):
        item = ExtraNamelistItem(['a', 'b', 'c'], 1)

        item[4] = 'd'

        assert item[4] == 'd'

    def test_cannot_add_none_with_new_index(self):
        item = ExtraNamelistItem(['a', 'b', 'c'], 1)

        with pytest.raises(ExtraNamelistsError):
            item[4] = None

    def test_can_add_value_with_non_contiguous_index(self):
        item = ExtraNamelistItem(['a', 'b', 'c'], 1)

        item[5] = 'd'

        assert item[5] == 'd'

    def test_raises_if_new_value_has_different_type(self):
        item = ExtraNamelistItem(['a', 'b', 'c'], 1)

        with pytest.raises(ExtraNamelistsError):
            item[4] = True

    def test_cannot_set_item_value_with_invalid_index_type(self):
        item = ExtraNamelistItem([1, 2, 3], 1)

        with pytest.raises(ExtraNamelistsError):
            item['foo'] = 4

    def test_combine_raises_if_self_is_scalar(self):
        item = ExtraNamelistItem(0)
        other_item = ExtraNamelistItem([1, 2, 3], 1)

        with pytest.raises(ExtraNamelistsError):
            item.combine(other_item)

    def test_combine_raises_if_other_is_scalar(self):
        item = ExtraNamelistItem([1, 2, 3], 1)
        other_item = ExtraNamelistItem(0)

        with pytest.raises(ExtraNamelistsError):
            item.combine(other_item)

    def test_can_combine_items_with_disjoint_indices(self):
        item1 = ExtraNamelistItem([1, 2, 3], 1)
        item2 = ExtraNamelistItem([4, 5, 6], 4)

        item1.combine(item2)

        assert item1.as_dict() == {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}

    def test_cannot_combine_items_with_overlapping_indices(self):
        item1 = ExtraNamelistItem([1, 2, 3], 1)
        item2 = ExtraNamelistItem([3, 4, 5], 3)

        with pytest.raises(ExtraNamelistsError):
            item1.combine(item2)

    @pytest.mark.parametrize('item1, item2', [(ExtraNamelistItem([1, 2, 3], 1), ExtraNamelistItem([1.0, 2.0, 3.0], 3)),
                                              (ExtraNamelistItem([True, False, True], 1), ExtraNamelistItem([1.0, 2.0, 3.0], 3)),
                                              (ExtraNamelistItem(['foo', 'bar', 'baz'], 1), ExtraNamelistItem([None, None, None], 3))])
    def test_cannot_combine_items_with_different_types(self, item1, item2):
        with pytest.raises(ExtraNamelistsError):
            item1.combine(item2)

    def test_as_dict_returns_expected_value_for_scalar_item(self):
        item = ExtraNamelistItem(0)

        assert item.as_dict() == {None: 0}

    def test_as_dict_returns_expected_value_for_vector_item(self):
        item = ExtraNamelistItem([1, 2], 1)

        assert item.as_dict() == {1: 1, 2: 2}

    def test_as_list_for_vector_item(self):
        item = ExtraNamelistItem([1, 2, 3], 1)

        assert item.as_list() == [1, 2, 3]

    def test_as_list_raises_for_non_contiguous_item(self):
        item = ExtraNamelistItem([1], 1)
        other_item = ExtraNamelistItem([3], 3)
        item.combine(other_item)

        with pytest.raises(ExtraNamelistsError):
            _ = item.as_list()

    def test_as_array_raises_for_vector(self):
        item = ExtraNamelistItem([1, 2, 3], 1)

        with pytest.raises(ExtraNamelistsError):
            _ = item.as_array()

    def test_can_compare_scalar_items_for_equality(self):
        item1 = ExtraNamelistItem(0)
        item2 = ExtraNamelistItem(0)

        assert item1 == item2

    def test_can_compare_scalar_items_for_inequality(self):
        item1 = ExtraNamelistItem(0)
        item2 = ExtraNamelistItem(1)

        assert item1 != item2

    def test_can_compare_vector_items_for_equality(self):
        item1 = ExtraNamelistItem([1, 2, 3], 1)
        item2 = ExtraNamelistItem([1, 2, 3], 1)

        assert item1 == item2

    def test_can_compare_vector_items_for_inequality(self):
        item1 = ExtraNamelistItem([0, 2, 3], 1)
        item2 = ExtraNamelistItem([1, 2, 3], 1)

        assert item1 != item2


class TestExtraNamelistItemArray:
    @pytest.fixture(params=[False, True], ids=['New', 'Old'])
    def style(self, request):
        def _style(v):
            if request.param:
                return v
            else:
                return [[v]]

        return _style

    @pytest.fixture(params=[2, 2.2, 'foo', False, None], ids=['int', 'float', 'string', 'bool', 'None'])
    def array_param_single_value(self, request):
        return request.param

    @pytest.fixture(params=[(1, 1), (2, 2), (1, 2), (2, 1)])
    def array_index(self, request):
        return request.param

    def test_can_initialise_an_array_item_with_a_single_value(self, array_param_single_value, array_index):
        _ = ExtraNamelistItem(array_param_single_value, array_index)

    @pytest.fixture(params=[[[1]],
                            [[1, 2]],
                            [[True, False], [False, True]],
                            [['foo'], ['bar']],
                            [[3.0, 2.0, 1.0], [1.5, 1.0, 0.5], [0.75, 0.5, 0.25]]])
    def array_param_multiple_values(self, request):
        return request.param

    def test_can_initialise_an_array_item_with_multiple_values(self, array_param_multiple_values):
        _ = ExtraNamelistItem(array_param_multiple_values)

    def test_can_retrieve_array_item_value_via_index(self, array_param_single_value, array_index):
        item = ExtraNamelistItem(array_param_single_value, array_index)

        assert item[array_index] == array_param_single_value

    @pytest.mark.parametrize('array, index, expected', [
        ([[1]], (1, 1), 1),
        ([['foo', 'bar'], ['baz', 'bah']], (1, 2), 'bar'),
        ([[True, False, True], [False, False, True]], (2, 1), False)
    ])
    def test_can_retrieve_array_item_via_index_from_multiple_values(self, array, index, expected):
        item = ExtraNamelistItem(array)

        assert item[index] == expected

    def test_raises_if_array_is_empty(self):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem([[]])

    def test_raises_if_array_has_inconsistent_row_lengths(self):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem([[1.0, 2.0, 3.0], [1.0, 2.0]])

    @pytest.mark.parametrize('value, type_', ([[[True]], bool],
                                              [[[0, 1]], int],
                                              [[[2.2, 3.3], [4.4, 5.5]], float],
                                              [[['Six'], ['Seven'], ['Eight']], str],
                                              [[[0, 1.0]], float],
                                              ))
    def test_type_returns_expected_value(self, value, type_):
        item = ExtraNamelistItem(value)

        assert item.type() == type_

    @pytest.mark.parametrize('value', [[[1, 2], [3.0, 4.0]], [[-1.0, 0, 2.3], [100, 100.0, 1]]])
    def test_compatible_numeric_types_are_allowed(self, value):
        _ = ExtraNamelistItem(value)

    @pytest.mark.parametrize('value', [[['foo', 2], [3.0, 4.0]], [['foo'], [False]]])
    def test_raises_if_array_value_has_inconsistent_types(self, value):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem(value)

    def test_raises_if_initialise_array_with_tuple_index(self):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem([[1.0, 2.0, 3.0], [1.0, 2.0]], (1, 1))

    @pytest.mark.parametrize('value', [[[None]],
                                       [[1, None]],
                                       [[True, None], [None, True]],
                                       [[None], ['bar']],
                                       [[None, None, None], [None, None, None], [None, None, None]]],
                             ids=['1x1', '1x2', '2x2', '1x2', '3x3'])
    def test_can_initialise_array_with_missing_values(self, value):
        _ = ExtraNamelistItem(value)

    def test_is_scalar_returns_false_for_array_item(self, array_param_single_value):
        item = ExtraNamelistItem(array_param_single_value, (1, 1))

        assert item.is_scalar() is False

    def test_is_vector_returns_false_for_array_item(self, array_param_single_value):
        item = ExtraNamelistItem(array_param_single_value, (1, 1))

        assert item.is_vector() is False

    @pytest.mark.parametrize('value, index', [(1, (1, 1)),
                                              ([[1, 2]], None),
                                              ([[1.0, 2.0], [3.0, 4.0]], None),
                                              ([['a', 'b'], ['c', 'd']], None)])
    def test_is_contiguous_returns_true_for_array_item(self, value, index):
        item = ExtraNamelistItem(value, index)

        assert item.is_contiguous() is True

    @pytest.mark.parametrize('value', [[[None]],
                                       [[1, None]],
                                       [[True, None], [None, True]],
                                       [[None], ['bar']],
                                       [[None, None, None], [None, None, None], [None, None, None]]],
                             ids=['1x1', '1x2', '2x2', '1x2', '3x3'])
    def test_is_contiguous_returns_true_for_array_item_with_missing_values(self, value):
        item = ExtraNamelistItem(value)

        assert item.is_contiguous() is True

    def test_is_contiguous_returns_false_for_array_item(self):
        item = ExtraNamelistItem(1, (1, 1))
        other_item = ExtraNamelistItem(3, (1, 3))
        item.combine(other_item)

        assert item.is_contiguous() is False

    @pytest.mark.parametrize('invalid_index', [(-1, 1), (1, 0)], ids=['negative-index', 'zero-index'])
    def test_raises_if_array_index_is_invalid(self, invalid_index, array_param_single_value):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem(array_param_single_value, invalid_index)

    def test_cannot_initialise_array_item_with_multiple_values(self):
        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelistItem([1, 2], (1, 1))

    def test_raises_if_access_with_invalid_array_index(self):
        item = ExtraNamelistItem(1, (1, 1))

        with pytest.raises(ExtraNamelistsError):
            _ = item[1, 2]

    def test_can_set_value_of_existing_array_index(self):
        item = ExtraNamelistItem(1, (2, 2))

        item[2, 2] = 4

        assert item[2, 2] == 4

    def test_can_add_value_with_new_array_index(self):
        item = ExtraNamelistItem(1, (1, 1))

        item[2, 2] = 2

        assert item[2, 2] == 2

    def test_raises_if_new_array_value_has_different_type(self):
        item = ExtraNamelistItem(1, (1, 1))

        with pytest.raises(ExtraNamelistsError):
            item[2, 2] = 2.0

    def test_cannot_set_item_value_with_invalid_array_index_type(self):
        item = ExtraNamelistItem(1, (1, 1))

        with pytest.raises(ExtraNamelistsError):
            item['foo'] = 2

    def test_combine_with_array_raises_if_other_is_scalar(self):
        item = ExtraNamelistItem(1, (1, 1))
        other_item = ExtraNamelistItem(0)

        with pytest.raises(ExtraNamelistsError):
            item.combine(other_item)

    def test_combine_with_array_raises_if_other_is_vector(self):
        item = ExtraNamelistItem(1, (1, 1))
        other_item = ExtraNamelistItem([1, 2, 3], 1)

        with pytest.raises(ExtraNamelistsError):
            item.combine(other_item)

    def test_can_combine_array_items_with_disjoint_indices(self):
        item1 = ExtraNamelistItem(1, (1, 1))
        item2 = ExtraNamelistItem(2, (2, 2))

        item1.combine(item2)

        assert item1.as_dict() == {(1, 1): 1, (2, 2): 2}

    def test_cannot_combine_array_items_with_overlapping_indices(self):
        item1 = ExtraNamelistItem(1, (1, 1))
        item2 = ExtraNamelistItem(2, (1, 1))

        with pytest.raises(ExtraNamelistsError):
            item1.combine(item2)

    def test_as_dict_returns_expected_value_for_array_item(self):
        item = ExtraNamelistItem(1, (1, 1))

        assert item.as_dict() == {(1, 1): 1}

    def test_as_list_raises_for_array_item(self):
        item = ExtraNamelistItem(1, (1, 1))

        with pytest.raises(ExtraNamelistsError):
            _ = item.as_list()

    def test_can_compare_array_items_for_equality(self):
        item1 = ExtraNamelistItem(1, (1, 1))
        item2 = ExtraNamelistItem(1, (1, 1))

        assert item1 == item2

    def test_can_compare_array_items_for_inequality(self):
        item1 = ExtraNamelistItem(1, (1, 1))
        item2 = ExtraNamelistItem(2, (1, 1))

        assert item1 != item2

    @pytest.mark.parametrize('value', [[[1]], [[1.0, 2.0]], [['a', 'b'], ['c', 'd']], [[True], [False]]])
    def test_as_array_returns_contiguous_item(self, value):
        item = ExtraNamelistItem(value)

        assert item.as_array() == value

    def test_as_array_raises_for_non_contiguous_item(self):
        item = ExtraNamelistItem(1, (1, 2))

        with pytest.raises(ExtraNamelistsError):
            _ = item.as_array()


class TestExtraNamelistItemActiveState:
    def test_item_has_no_active_state_by_default(self):
        item = ExtraNamelistItem(0)

        assert item.active is None

    @pytest.mark.parametrize('active', [True, False, None])
    def test_item_has_active_state(self, active):
        item = ExtraNamelistItem(0, active=active)

        assert item.active is active

    @pytest.mark.parametrize('active', [True, False, None])
    def test_can_set_active_state(self, active):
        item = ExtraNamelistItem(0)

        item.active = active

        assert item.active is active

    @pytest.mark.parametrize('active1, active2', [(None, True), (None, False), (True, None),
                                                    (False, None), (True, False), (False, True)])
    def test_combine_raises_if_active_status_differs(self, active1, active2):
        item1 = ExtraNamelistItem([1, 2, 3], 1, active=active1)
        item2 = ExtraNamelistItem([4, 5, 6], 4, active=active2)

        with pytest.raises(ExtraNamelistsError):
            item1.combine(item2)

    @pytest.mark.parametrize('active', [None, True, False])
    def test_combined_item_retains_active_status(self, active):
        item1 = ExtraNamelistItem([1, 2, 3], 1, active=active)
        item2 = ExtraNamelistItem([4, 5, 6], 4, active=active)

        item1.combine(item2)

        assert item1.active is active

    @pytest.mark.parametrize('active', [True, False])
    def test_items_with_different_active_status_compare_not_equal(self, active):
        item1 = ExtraNamelistItem(0)
        item2 = ExtraNamelistItem(0, active=active)

        assert item1 != item2

    @pytest.mark.parametrize('active', [True, False])
    def test_items_with_same_active_status_compare_equal(self, active):
        item1 = ExtraNamelistItem(0, active=active)
        item2 = ExtraNamelistItem(0, active=active)

        assert item1 == item2


class TestExtraNamelists:
    @pytest.fixture(params=['', 'Sanco'], ids=['jetto', 'sanco'])
    def prefix_and_raw_extra(self, request):
        prefix = request.param

        return prefix, {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "IPRAUX",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 2,
            f"{prefix}OutputExtraNamelist.selItems.cell[1][0]": "IPRTOTSMTH",
            f"{prefix}OutputExtraNamelist.selItems.cell[1][1]": 1,
            f"{prefix}OutputExtraNamelist.selItems.cell[1][2]": 2,
            f"{prefix}OutputExtraNamelist.selItems.cell[10][0]": "ITRGLFSM",
            f"{prefix}OutputExtraNamelist.selItems.cell[10][1]": 2,
            f"{prefix}OutputExtraNamelist.selItems.cell[10][2]": '1, 2, 3',
            f"{prefix}OutputExtraNamelist.selItems.cell[11][0]": "qlk_rhomax",
            f"{prefix}OutputExtraNamelist.selItems.cell[11][1]": 1,
            f"{prefix}OutputExtraNamelist.selItems.cell[11][2]": '0.1, 0.2, 0.3',
            f"{prefix}OutputExtraNamelist.selItems.cell[12][0]": "LBLADSS",
            f"{prefix}OutputExtraNamelist.selItems.cell[12][1]": 1,
            f"{prefix}OutputExtraNamelist.selItems.cell[12][2]": "'a', 'b'",
            f"{prefix}OutputExtraNamelist.selItems.cell[13][0]": "PFCIPLIN",
            f"{prefix}OutputExtraNamelist.selItems.cell[13][1]": '1,1',
            f"{prefix}OutputExtraNamelist.selItems.cell[13][2]": 1e6,
            f"{prefix}OutputExtraNamelist.selItems.cell[14][0]": "PFCIPLIN",
            f"{prefix}OutputExtraNamelist.selItems.cell[14][1]": '1,2',
            f"{prefix}OutputExtraNamelist.selItems.cell[14][2]": 2e6,
            f"{prefix}OutputExtraNamelist.selItems.cell[15][0]": "VECTOR1",
            f"{prefix}OutputExtraNamelist.selItems.cell[15][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[15][2]": '(1,,2)',
            f"{prefix}OutputExtraNamelist.selItems.cell[16][0]": "ARRAY1",
            f"{prefix}OutputExtraNamelist.selItems.cell[16][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[16][2]": '((1.0, 2.0), (3.0,))',
            f"{prefix}OutputExtraNamelist.selItems.cell[2][0]": "BCINTRHON",
            f"{prefix}OutputExtraNamelist.selItems.cell[2][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[2][2]": '(1, 2, 3)',
            f"{prefix}OutputExtraNamelist.selItems.cell[3][0]": "IEQUOP",
            f"{prefix}OutputExtraNamelist.selItems.cell[3][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[3][2]": '("a", "b")',
            f"{prefix}OutputExtraNamelist.selItems.cell[4][0]": "IPENCILSMTHONAXIS",
            f"{prefix}OutputExtraNamelist.selItems.cell[4][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[4][2]": '((T, F), (F, T))',
            f"{prefix}OutputExtraNamelist.selItems.cell[5][0]": "QMAXRHOMAX",
            f"{prefix}OutputExtraNamelist.selItems.cell[5][1]": 1,
            f"{prefix}OutputExtraNamelist.selItems.cell[5][2]": "T,F,T",
            f"{prefix}OutputExtraNamelist.selItems.cell[6][0]": "TDEBUG",
            f"{prefix}OutputExtraNamelist.selItems.cell[6][1]": 2,
            f"{prefix}OutputExtraNamelist.selItems.cell[6][2]": "'foo','bar'",
            f"{prefix}OutputExtraNamelist.selItems.cell[7][0]": "KWMAIN",
            f"{prefix}OutputExtraNamelist.selItems.cell[7][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[7][2]": 1,
            f"{prefix}OutputExtraNamelist.selItems.cell[8][0]": "IGLF23SMSIGNCONS",
            f"{prefix}OutputExtraNamelist.selItems.cell[8][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[8][2]": 1,
            f"{prefix}OutputExtraNamelist.selItems.cell[9][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[9][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[9][2]": 'f',
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 17,
            f"{prefix}OutputExtraNamelist.select": True
        }

    def test_can_load_valid_raw_namelists(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        _ = ExtraNamelists(raw_extra_namelists, prefix)

    @pytest.fixture
    def prefix_and_raw_extra_4_columns(self, prefix_and_raw_extra):
        prefix, raw_extra = prefix_and_raw_extra

        item_with_4_columns = {
            f"{prefix}OutputExtraNamelist.selItems.cell[17][0]": "DFNEFB",
            f"{prefix}OutputExtraNamelist.selItems.cell[17][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[17][2]": 0.0,
            f"{prefix}OutputExtraNamelist.selItems.cell[17][3]": True,
        }
        raw_extra = {**raw_extra, **item_with_4_columns}
        raw_extra[f"{prefix}OutputExtraNamelist.selItems.rows"] = \
            raw_extra[f"{prefix}OutputExtraNamelist.selItems.rows"] + 1
        raw_extra[f"{prefix}OutputExtraNamelist.selItems.columns"] = 4

        return prefix, raw_extra

    def test_can_load_valid_raw_namelists_with_4_columns(self, prefix_and_raw_extra_4_columns):
        prefix, raw_extra_namelists = prefix_and_raw_extra_4_columns

        _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_accepts_unknown_extra_namelist_fields(self, prefix_and_raw_extra):
        prefix, raw_extra = prefix_and_raw_extra

        misc_extra = {
            f"{prefix}OutputExtraNamelist.foo": None,
            f"{prefix}OutputExtraNamelist.foo.bar": "All",
            f"{prefix}OutputExtraNamelist.foo.bar.baz": 0
        }

        raw_extra = {**raw_extra, **misc_extra}

        _ = ExtraNamelists(raw_extra, prefix)

    def test_raises_if_4_columns_required_but_3_specified(self, prefix_and_raw_extra_4_columns):
        prefix, raw_extra_namelists = prefix_and_raw_extra_4_columns

        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.columns"] = 3

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_select_flag_is_missing(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        del raw_extra_namelists[f'{prefix}OutputExtraNamelist.select']

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_select_flag_is_not_boolean(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        raw_extra_namelists[f'{prefix}OutputExtraNamelist.select'] = None

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_column_count_is_missing(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        del raw_extra_namelists[f'{prefix}OutputExtraNamelist.selItems.columns']

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_column_count_is_invalid(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        raw_extra_namelists[f'{prefix}OutputExtraNamelist.selItems.columns'] = 5

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_row_count_is_missing(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        del raw_extra_namelists[f'{prefix}OutputExtraNamelist.selItems.rows']

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_row_count_is_not_int(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        raw_extra_namelists[f'{prefix}OutputExtraNamelist.selItems.rows'] = None

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_parameter_name_has_invalid_format(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        raw_extra_namelists['invalid-key'] = raw_extra_namelists.pop(f'{prefix}OutputExtraNamelist.selItems.cell[0][0]')

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_len_reports_number_of_distinct_items(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert len(extras) == 16

    def test_raises_if_item_is_missing(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        for k in raw_extra_namelists.copy():
            if k.startswith(f'{prefix}OutputExtraNamelist.selItems.cell[0]'):
                raw_extra_namelists.pop(k)

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_parameter_is_missing_a_column(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra

        raw_extra_namelists.pop(f'{prefix}OutputExtraNamelist.selItems.cell[0][0]')

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_len_reports_number_of_rows_selected(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f'{prefix}OutputExtraNamelist.selItems.rows'] = 1

        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert len(extras) == 1

    def test_raises_if_number_of_rows_is_greater_than_items_present(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f'{prefix}OutputExtraNamelist.selItems.rows'] = 18

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_len_is_zero_if_no_rows_selected(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f'{prefix}OutputExtraNamelist.select'] = False

        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert len(extras) == 0

    def test_raises_if_value_is_empty(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = None

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_raises_if_name_is_empty(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f'{prefix}OutputExtraNamelist.selItems.cell[0][0]'] = None

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)

    def test_active_is_empty(self, prefix_and_raw_extra_4_columns):
        prefix, raw_extra_namelists = prefix_and_raw_extra_4_columns
        del raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[17][3]"]

        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert extras['DFNEFB'].active is None

    @pytest.mark.parametrize('active', [True, False])
    def test_active_is_set(self, prefix_and_raw_extra_4_columns, active):
        prefix, raw_extra_namelists = prefix_and_raw_extra_4_columns
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[17][3]"] = active

        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert extras['DFNEFB'].active is active

    def test_can_retrieve_item_by_name(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert extras['IPRAUX'] == ExtraNamelistItem(2)

    def test_raises_if_nonexistent_item_is_accessed(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        with pytest.raises(ExtraNamelistsError):
            _ = extras['nonexistent-parameter']

    def test_can_check_if_item_exists(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert 'IPRAUX' in extras

    def test_can_check_if_item_does_not_exist(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert 'nonexistent-parameter' not in extras

    def test_can_update_scalar_item_by_replacement(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        extras['IPRAUX'] = ExtraNamelistItem(0)

        assert extras['IPRAUX'] == ExtraNamelistItem(0)

    def test_cannot_replace_scalar_item_with_different_type(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        with pytest.raises(ExtraNamelistsError):
            extras['IPRAUX'] = ExtraNamelistItem(0.5)

    def test_cannot_replace_scalar_item_with_vector_item(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        with pytest.raises(ExtraNamelistsError):
            extras['IPRAUX'] = ExtraNamelistItem([1, 2, 3], 1)

    def test_cannot_replace_vector_item_with_different_type(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        with pytest.raises(ExtraNamelistsError):
            extras['IPRAUX'] = ExtraNamelistItem(['foo', 'bar'], 1)

    def test_cannot_replace_vector_item_with_scalar_item(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        with pytest.raises(ExtraNamelistsError):
            extras['IPRTOTSMTH'] = ExtraNamelistItem(0)

    def test_can_add_new_item(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        item = ExtraNamelistItem([1, 2, 3], 1)
        extras['NEW'] = item

        assert extras['NEW'] == item

    def test_can_replace_existing_item(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        item = ExtraNamelistItem(0)
        extras['IPRAUX'] = item

        assert extras['IPRAUX'] == item

    def test_can_delete_existing_item(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        del extras['IPRAUX']

        with pytest.raises(ExtraNamelistsError):
            _ = extras['IPRAUX']

    def test_raises_if_attempt_to_delete_nonexistent_item(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        extras = ExtraNamelists(raw_extra_namelists, prefix)

        with pytest.raises(ExtraNamelistsError):
            del extras['NONEXISTENT-PARAM']

    def test_combines_if_item_repeated_with_disjoint_indices(self, prefix_and_raw_extra):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        rows = raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.rows"]

        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[{rows}][0]"] = "IPRTOTSMTH"
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[{rows}][1]"] = 2
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[{rows}][2]"] = -2
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.rows"] = rows + 1

        extras = ExtraNamelists(raw_extra_namelists, prefix)

        assert extras["IPRTOTSMTH"].as_dict() == ExtraNamelistItem([2, -2], 1).as_dict()


class TestExtraNamelistsParseItem:

    @pytest.fixture(params=['', 'Sanco'], ids=['jetto', 'sanco'])
    def prefix_and_raw_extra(self, request):
        prefix = request.param

        return prefix, {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "PARAM",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 2,
            f"{prefix}OutputExtraNamelist.selItems.columns": 4,
            f"{prefix}OutputExtraNamelist.selItems.rows": 1,
            f"{prefix}OutputExtraNamelist.select": True
        }

    @pytest.mark.parametrize('raw_value, expected', [(1, ExtraNamelistItem(1)),
                                                     (2.0, ExtraNamelistItem(2.0)),
                                                     ('T', ExtraNamelistItem(True)),
                                                     ('F', ExtraNamelistItem(False)),
                                                     ('t', ExtraNamelistItem(True)),
                                                     ('f', ExtraNamelistItem(False)),
                                                     ('foo', ExtraNamelistItem('foo')),
                                                     ('foo, bar', ExtraNamelistItem('foo, bar')),
                                                     ('1,2,3', ExtraNamelistItem('1,2,3'))])
    def test_parse_scalar_item_value(self, prefix_and_raw_extra, raw_value, expected):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = None
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_value

        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected


    @pytest.mark.parametrize('raw_value, expected', [('1, 2, 3', ExtraNamelistItem([1, 2, 3], 1)),
                                                     ('0.1, 0.2, 0.3', ExtraNamelistItem([0.1, 0.2, 0.3], 1)),
                                                     ("'a', 'b', 'c'", ExtraNamelistItem(['a', 'b', 'c'], 1)),
                                                     ('"a", "b", "c"', ExtraNamelistItem(['a', 'b', 'c'], 1)),
                                                     ("T, T, F", ExtraNamelistItem([True, True, False], 1)),
                                                     ("t, t, f", ExtraNamelistItem([True, True, False], 1)),
                                                     ("T, t, F", ExtraNamelistItem([True, True, False], 1))])
    def test_parses_old_style_vector(self, prefix_and_raw_extra, raw_value, expected):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = 1
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_value

        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected

    @pytest.mark.parametrize('raw_value, expected', [('1, 2, 3', ExtraNamelistItem([1, 2, 3], 1)),
                                                     ('0.1, 0.2, 0.3', ExtraNamelistItem([0.1, 0.2, 0.3], 1)),
                                                     ("'a', 'b', 'c'", ExtraNamelistItem(['a', 'b', 'c'], 1)),
                                                     ('"a", "b", "c"', ExtraNamelistItem(['a', 'b', 'c'], 1)),
                                                     ("T, T, F", ExtraNamelistItem([True, True, False], 1)),
                                                     ("t, t, f", ExtraNamelistItem([True, True, False], 1)),
                                                     ("T, t, F", ExtraNamelistItem([True, True, False], 1))])
    def test_parses_new_style_vector(self, prefix_and_raw_extra, raw_value, expected):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = None
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = '(' + raw_value + ')'

        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected

    @pytest.mark.parametrize('raw_value, expected', [('()', ExtraNamelistItem([None])),
                                                     ('(1,)', ExtraNamelistItem([1, None])),
                                                     ('(1, )', ExtraNamelistItem([1, None])),
                                                     ('(, 1.0)', ExtraNamelistItem([None, 1.0])),
                                                     ('( ,1.0)', ExtraNamelistItem([None, 1.0])),
                                                     ("(, 'b', 'c')", ExtraNamelistItem([None, 'b', 'c'])),
                                                     ('("a", ,"c")', ExtraNamelistItem(['a', None, 'c'])),
                                                     ('("a" ,, "c")', ExtraNamelistItem(['a', None, 'c'])),
                                                     ("(T, T,)", ExtraNamelistItem([True, True, None]))])
    def test_parses_new_style_vector_with_missing_values(self, prefix_and_raw_extra, raw_value, expected):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = None
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_value

        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected


    @pytest.mark.parametrize('raw_value, expected', [(1, ExtraNamelistItem([1], 1)),
                                                     (0.1, ExtraNamelistItem([0.1], 1)),
                                                     ('a', ExtraNamelistItem(['a'], 1)),
                                                     ("a", ExtraNamelistItem(['a'], 1)),
                                                     ("T", ExtraNamelistItem([True], 1)),
                                                     ("t", ExtraNamelistItem([True], 1)),
                                                     ("F", ExtraNamelistItem([False], 1))])
    def test_parses_old_style_vector_with_single_element(self, prefix_and_raw_extra, raw_value, expected):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = 1
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_value

        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected

    @pytest.mark.parametrize('raw_value, expected', [('(1)', ExtraNamelistItem([1], 1)),
                                                     ('(0.1)', ExtraNamelistItem([0.1], 1)),
                                                     ("('a')", ExtraNamelistItem(['a'], 1)),
                                                     ('("a")', ExtraNamelistItem(['a'], 1)),
                                                     ("(T)", ExtraNamelistItem([True], 1)),
                                                     ("(t)", ExtraNamelistItem([True], 1)),
                                                     ("(F)", ExtraNamelistItem([False], 1))])
    def test_parses_new_style_vector_with_single_element(self, prefix_and_raw_extra, raw_value, expected):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = None
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_value

        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected

    @pytest.mark.parametrize('line', ['1, 2, T',
                                      '0.1, 0.2, "foo"',
                                      '"foo", "bar", T',
                                      'T, F, 0.1'])
    def test_raises_if_vector_values_are_inconsistent(self, prefix_and_raw_extra, line):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = 1
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = line

        with pytest.raises(ExtraNamelistsError):
            _ = ExtraNamelists(raw_extra_namelists, prefix)


    @pytest.fixture(params=[(1, 1), (0.1, 0.1), ('a', 'a'), ("a", "a"), ("T", True), ("t", True), ("F", False)])
    def array_element(self, request):
        return request.param[0], request.param[1]


    def test_parses_old_style_array_with_single_element(self, prefix_and_raw_extra, array_element):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_element, processed_element = array_element
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = '1,1'
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_element

        expected = ExtraNamelistItem(processed_element, (1,1))
        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected

    @pytest.mark.parametrize('raw_value, processed_value', [(1, 1),
                                                            (0.1, 0.1),
                                                            ('a', 'a'),
                                                            ("a", "a"),
                                                            ("T", True),
                                                            ("t", True),
                                                            ("F", False)])
    def test_parses_new_style_array_with_single_element(self, prefix_and_raw_extra, raw_value, processed_value):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = None
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_value

        expected = ExtraNamelistItem(processed_value)
        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected

    @pytest.mark.parametrize('raw_value, processed_value', [('((1, 2, 3))', [[1, 2, 3]]),
                                                            ('((1.0, 2.0), (3.0, 4.0))', [[1.0, 2.0], [3.0, 4.0]]),
                                                            ('(("a"), ("b"), ("c"))', [["a"], ["b"], ["c"]]),
                                                            ('((T, F, f, t))', [[True, False, False, True]])])
    def test_parses_new_style_array_with_multiple_elements(self, prefix_and_raw_extra, raw_value, processed_value):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = None
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_value

        expected = ExtraNamelistItem(processed_value)
        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected

    @pytest.mark.parametrize('raw_value, processed_value', [('(())', [[None]]),
                                                            ('((1.0, 2.0), (,))', [[1.0, 2.0], [None, None]]),
                                                            ('(("a"), ("b"), ())', [["a"], ["b"], [None]]),
                                                            ('((T, F, , t))', [[True, False, None, True]])])
    def test_parses_new_style_array_with_missing_elements(self, prefix_and_raw_extra, raw_value, processed_value):
        prefix, raw_extra_namelists = prefix_and_raw_extra
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][1]"] = None
        raw_extra_namelists[f"{prefix}OutputExtraNamelist.selItems.cell[0][2]"] = raw_value

        expected = ExtraNamelistItem(processed_value)
        actual = ExtraNamelists(raw_extra_namelists, prefix)['PARAM']

        assert actual == expected


class TestExtraNamelistsWrite:
    """Test that transform of the extra namelists back into raw JSET settings works as expected"""

    @pytest.fixture(params=['', 'Sanco'], ids=['jetto', 'sanco'])
    def prefix(self, request):
        return request.param

    @pytest.fixture()
    def prefix_and_raw_in(self, prefix):
        return prefix, {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 0,
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 1,
            f"{prefix}OutputExtraNamelist.select": True
        }

    @pytest.fixture(scope='function')
    def extras_in(self, prefix_and_raw_in):
        prefix, raw_in = prefix_and_raw_in

        return ExtraNamelists(raw_in, prefix)

    def test_unchanged_extra_namelists_lists_the_select_flag(self, extras_in):
        prefix = extras_in.prefix

        raw_out = extras_in.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.select'] is True

    def test_unchanged_extra_namelists_lists_the_expected_number_of_columns(self, extras_in):
        prefix = extras_in.prefix

        raw_out = extras_in.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.columns'] == 3

    def test_unchanged_extra_namelists_lists_the_expected_number_of_rows(self, extras_in):
        prefix = extras_in.prefix

        raw_out = extras_in.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.rows'] == 1

    @pytest.mark.parametrize('value', [1, 1.0, 'T', "'foo'"])
    def test_scalar_appears_in_output(self, prefix_and_raw_in, value):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value
        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] == value

    def test_active_column_not_written(self, extras_in):
        raw_out = extras_in.as_jset_settings()

        assert f'{extras_in.prefix}OutputExtraNamelist.selItems.cell[0][3]' not in raw_out

    @pytest.mark.parametrize('value_in, expected_out', [('1, 2, 3', (1, 2, 3)),
                                                        ('T, T, F', ('T', 'T', 'F')),
                                                        ("'a', 'b', 'c'", ("'a'", "'b'", "'c'"))])
    def test_non_contiguous_old_style_vector_values_appear_in_output(self, prefix_and_raw_in, value_in, expected_out):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = 2
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value_in
        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] == expected_out[0] and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[1][2]'] == expected_out[1] and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[2][2]'] == expected_out[2]

    @pytest.mark.parametrize('value_in, expected_out', [('1, 2, 3', (1, 2, 3)),
                                                        ('T, T, F', ('T', 'T', 'F')),
                                                        ("'a', 'b', 'c'", ("'a'", "'b'", "'c'"))])
    def test_non_contiguous_old_style_vector_indices_appear_in_output(self, prefix_and_raw_in, value_in, expected_out):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = 2
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value_in
        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] == 2 and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[1][1]'] == 3 and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[2][1]'] == 4

    @pytest.mark.parametrize('value_in, expected_out', [('1, 2, 3', '(1, 2, 3)'),
                                                        ('T, T, F', '(T, T, F)'),
                                                        ("'a', 'b', 'c'", "('a', 'b', 'c')")])
    def test_contiguous_old_style_vector_values_appear_in_output(self, prefix_and_raw_in, value_in, expected_out):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = 1
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value_in
        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] == expected_out

    @pytest.mark.parametrize('value_in, expected_out', [('1, 2, 3', (1, 2, 3)),
                                                        ('T, T, F', ('T', 'T', 'F')),
                                                        ("'a', 'b', 'c'", ("'a'", "'b'", "'c'"))])
    def test_contiguous_old_style_vector_indices_do_not_appear_in_output(self, prefix_and_raw_in, value_in, expected_out):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = 1
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value_in
        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] is None


    @pytest.mark.parametrize('value', ['(1)', '(1, 2)', '(1.0, 2.0, 3.0)', '(T, F, T, T, F)'])
    def test_new_style_vector_appears_in_output(self, prefix_and_raw_in, value):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = None
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value

        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] == value and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] is None

    @pytest.mark.parametrize('value', ['()', '(, 2)', '(1.0, , 3.0)', '(T, F, T, T, )'])
    def test_new_style_vector_with_missing_values_appears_in_output(self, prefix_and_raw_in, value):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = None
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value

        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] == value and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] is None

    @pytest.mark.parametrize('value_in', [1, 1.0, 'T', "'foo'"])
    def test_non_contiguous_old_style_array_values_appear_in_output(self, prefix_and_raw_in, value_in):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = '1,2'
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value_in
        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] == value_in and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] == '1,2'

    @pytest.mark.parametrize('value_in, value_out', [(1, '((1))'),
                                                     (1.0, '((1.0))'),
                                                     ('T', "((T))"),
                                                     ("'foo'", "(('foo'))")])
    def test_contiguous_old_style_array_values_appear_in_output(self, prefix_and_raw_in, value_in, value_out):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = '1,1'
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value_in
        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] == value_out and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] == None

    @pytest.mark.parametrize('value', ['(())', '((1.0, 2.0), (, ))', "(('a'), ('b'), ())", '((T, F, , T))'])
    def test_new_style_array_values_with_missing_elements_appear_in_output(self, prefix_and_raw_in, value):
        prefix, raw_in = prefix_and_raw_in
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] = None
        raw_in[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] = value
        extras = ExtraNamelists(raw_in, prefix)

        raw_out = extras.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][2]'] == value and \
               raw_out[f'{prefix}OutputExtraNamelist.selItems.cell[0][1]'] == None

    def test_update_to_scalar_item_appears_in_output(self, extras_in):
        prefix = extras_in.prefix

        extras_in['ITRDOWNSC'] = ExtraNamelistItem(1)
        raw_out = extras_in.as_jset_settings()

        assert raw_out == {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 1,
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 1,
            f"{prefix}OutputExtraNamelist.select": True
        }

    def test_removal_of_scalar_item_appears_in_output(self, extras_in):
        prefix = extras_in.prefix

        del extras_in['ITRDOWNSC']
        raw_out = extras_in.as_jset_settings()

        assert raw_out == {
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 0,
            f"{prefix}OutputExtraNamelist.select": True
        }

    @pytest.mark.parametrize('value_in, value_out', [(1, '(1)'),
                                                     (0.1, '(0.1)'),
                                                     ('foo', "('foo')"),
                                                     (True, '(T)')],
                             ids=['int', 'float', 'string', 'bool'])
    def test_addition_of_vector_item_with_single_index_appears_in_output(self, extras_in, value_in, value_out):
        prefix = extras_in.prefix
        extras_in['NEW'] = ExtraNamelistItem(value_in, 1)

        raw_out = extras_in.as_jset_settings()

        assert raw_out == {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 0,
            f"{prefix}OutputExtraNamelist.selItems.cell[1][0]": "NEW",
            f"{prefix}OutputExtraNamelist.selItems.cell[1][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[1][2]": value_out,
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 2,
            f"{prefix}OutputExtraNamelist.select": True
        }

    @pytest.mark.parametrize('value_in, value_out', [([1, 2], '(1, 2)'),
                                                     ([0.1, 0.2], '(0.1, 0.2)'),
                                                     (['foo', 'bar'], "('foo', 'bar')"),
                                                     ([True, False], "(T, F)")],
                             ids=['int', 'float', 'string', 'bool'])
    def test_addition_of_vector_item_with_multiple_indices_appears_in_output(self, extras_in, value_in, value_out):
        prefix = extras_in.prefix

        extras_in['NEW'] = ExtraNamelistItem(value_in, 1)
        raw_out = extras_in.as_jset_settings()

        assert raw_out == {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 0,
            f"{prefix}OutputExtraNamelist.selItems.cell[1][0]": "NEW",
            f"{prefix}OutputExtraNamelist.selItems.cell[1][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[1][2]": value_out,
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 2,
            f"{prefix}OutputExtraNamelist.select": True
        }

    def test_addition_of_array_item_with_single_index_appears_in_output(self, extras_in):
        prefix = extras_in.prefix
        extras_in['NEW'] = ExtraNamelistItem(1, (1, 2))

        raw_out = extras_in.as_jset_settings()

        assert raw_out == {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 0,
            f"{prefix}OutputExtraNamelist.selItems.cell[1][0]": "NEW",
            f"{prefix}OutputExtraNamelist.selItems.cell[1][1]": '1,2',
            f"{prefix}OutputExtraNamelist.selItems.cell[1][2]": 1,
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 2,
            f"{prefix}OutputExtraNamelist.select": True
        }

    def test_addition_of_array_item_with_multiple_indices_appears_in_output(self, extras_in):
        prefix = extras_in.prefix

        extras_in['NEW'] = ExtraNamelistItem(1, (1, 1))
        extras_in['NEW'].combine(ExtraNamelistItem(2, (1, 3)))
        raw_out = extras_in.as_jset_settings()

        assert raw_out == {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 0,
            f"{prefix}OutputExtraNamelist.selItems.cell[1][0]": "NEW",
            f"{prefix}OutputExtraNamelist.selItems.cell[1][1]": '1,1',
            f"{prefix}OutputExtraNamelist.selItems.cell[1][2]": 1,
            f"{prefix}OutputExtraNamelist.selItems.cell[2][0]": "NEW",
            f"{prefix}OutputExtraNamelist.selItems.cell[2][1]": '1,3',
            f"{prefix}OutputExtraNamelist.selItems.cell[2][2]": 2,
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 3,
            f"{prefix}OutputExtraNamelist.select": True
        }

    def test_no_items_in_output_if_select_was_off(self, prefix):
        raw_in = {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 0,
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 1,
            f"{prefix}OutputExtraNamelist.select": False
        }

        extras = ExtraNamelists(raw_in, prefix)

        assert extras.as_jset_settings() == {
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 0,
            f"{prefix}OutputExtraNamelist.select": False
        }

    def test_adding_new_item_switches_select_on(self, prefix):
        raw_in = {
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 0,
            f"{prefix}OutputExtraNamelist.select": False
        }
        extras = ExtraNamelists(raw_in, prefix)

        extras['ITRDOWNSC'] = ExtraNamelistItem(0)

        assert extras.as_jset_settings()[f"{prefix}OutputExtraNamelist.select"] is True

    @pytest.fixture()
    def prefix_and_raw_in_4_columns(self, prefix_and_raw_in):
        prefix, raw_in = prefix_and_raw_in

        return prefix, {
            **raw_in,
            **{
                f"{prefix}OutputExtraNamelist.selItems.cell[0][3]": True,
                f"{prefix}OutputExtraNamelist.selItems.columns": 4,
            }
        }

    @pytest.fixture(scope='function')
    def extras_in_4_columns(self, prefix_and_raw_in_4_columns):
        prefix, raw_in = prefix_and_raw_in_4_columns

        return ExtraNamelists(raw_in, prefix)

    def test_unchanged_extra_namelists_lists_4_columns(self, extras_in_4_columns):
        raw_out = extras_in_4_columns.as_jset_settings()

        assert raw_out[f'{extras_in_4_columns.prefix}OutputExtraNamelist.selItems.columns'] == 4

    def test_lists_4_columns_even_if_no_item_requires_it(self, extras_in_4_columns):
        extras_in_4_columns['ITRDOWNSC'] = ExtraNamelistItem(0, active=None)

        raw_out = extras_in_4_columns.as_jset_settings()

        assert raw_out[f'{extras_in_4_columns.prefix}OutputExtraNamelist.selItems.columns'] == 4

    @pytest.mark.parametrize('active', [True, False])
    def test_columns_updated_to_4_if_item_with_active_flag_added(self, extras_in, active):
        prefix = extras_in.prefix
        extras_in['NEW'] = ExtraNamelistItem(0, active=active)

        raw_out = extras_in.as_jset_settings()

        assert raw_out[f'{prefix}OutputExtraNamelist.selItems.columns'] == 4

    @pytest.mark.parametrize('active', [True, False])
    def test_active_column_written_for_scalar_item(self, extras_in_4_columns, active):
        extras_in_4_columns['ITRDOWNSC'] = ExtraNamelistItem(0, active=active)

        raw_out = extras_in_4_columns.as_jset_settings()

        assert raw_out[f"{extras_in_4_columns.prefix}OutputExtraNamelist.selItems.cell[0][3]"] is active

    @pytest.mark.parametrize('active', [True, False])
    def test_active_column_written_for_old_style_vector_item(self, extras_in_4_columns, active):
        del extras_in_4_columns['ITRDOWNSC']
        extras_in_4_columns['ITRDOWNSC'] = ExtraNamelistItem([1, 2], 2, active=active)

        raw_out = extras_in_4_columns.as_jset_settings()

        assert raw_out[f"{extras_in_4_columns.prefix}OutputExtraNamelist.selItems.cell[0][3]"] is active and \
               raw_out[f"{extras_in_4_columns.prefix}OutputExtraNamelist.selItems.cell[1][3]"] is active

    @pytest.mark.parametrize('active', [True, False])
    def test_active_column_written_for_new_style_vector_item(self, extras_in_4_columns, active):
        del extras_in_4_columns['ITRDOWNSC']
        extras_in_4_columns['ITRDOWNSC'] = ExtraNamelistItem([1, 2], 1, active=active)

        raw_out = extras_in_4_columns.as_jset_settings()

        assert raw_out[f"{extras_in_4_columns.prefix}OutputExtraNamelist.selItems.cell[0][3]"] is active

    @pytest.mark.parametrize('active', [True, False])
    def test_active_column_written_for_old_style_array_item(self, extras_in_4_columns, active):
        del extras_in_4_columns['ITRDOWNSC']
        extras_in_4_columns['ITRDOWNSC'] = ExtraNamelistItem(1, (1,2), active=active)

        raw_out = extras_in_4_columns.as_jset_settings()

        assert raw_out[f"{extras_in_4_columns.prefix}OutputExtraNamelist.selItems.cell[0][3]"] is active

    def test_miscellaneous_fields_in_input_copied_to_output(self, prefix_and_raw_in):
        prefix, raw_in = prefix_and_raw_in
        misc_in = {
            f"{prefix}OutputExtraNamelist.foo": None,
            f"{prefix}OutputExtraNamelist.foo.bar": "All",
            f"{prefix}OutputExtraNamelist.foo.bar.baz": 0
        }
        raw_in = {**raw_in, **misc_in}

        extras = ExtraNamelists(raw_in, prefix)
        raw_out = extras.as_jset_settings()

        assert all(raw_out[k] == v for k,v in misc_in.items())


class TestExtraNamelistsWriteItem:
    """Test that transform of the extra namelists back into raw JSET settings works as expected"""

    @pytest.fixture(params=['', 'Sanco'], ids=['jetto', 'sanco'])
    def prefix(self, request):
        return request.param

    @pytest.fixture()
    def prefix_and_raw_in(self, prefix):
        return prefix, {
            f"{prefix}OutputExtraNamelist.selItems.cell[0][0]": "ITRDOWNSC",
            f"{prefix}OutputExtraNamelist.selItems.cell[0][1]": None,
            f"{prefix}OutputExtraNamelist.selItems.cell[0][2]": 0,
            f"{prefix}OutputExtraNamelist.selItems.columns": 3,
            f"{prefix}OutputExtraNamelist.selItems.rows": 1,
            f"{prefix}OutputExtraNamelist.select": True
        }

    @pytest.fixture(scope='function')
    def extras_in(self, prefix_and_raw_in):
        prefix, raw_in = prefix_and_raw_in

        return ExtraNamelists(raw_in, prefix)


class TestJSETReadExtraNamelists:
    """Test that the JSET class handles extra namelists correctly"""

    def test_raises_if_no_jetto_namelists_present(self):
        jsetfile = JSETFile(extra=JSETJettoExtraNamelists(enable=False, select='true'))

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    def test_raises_if_no_sanco_namelists_present(self):
        jsetfile = JSETFile(impurities=JSETImpurities(select=False, source='foo'),
                            sanco_extra=JSETSancoExtraNamelists(enable=False))

        with pytest.raises(JSETError):
            _ = JSET(jsetfile.as_string())

    @mock.patch('jetto_tools.jset.ExtraNamelists')
    def test_jset_calls_extra_namelist_constructors_with_expected_dict(self, mock_extra):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        mock_extra.assert_has_calls([mock.call({'OutputExtraNamelist.select': True,
                                                'OutputExtraNamelist.selItems.rows': 0,
                                                'OutputExtraNamelist.selItems.columns': 3}, ''),
                                     mock.call({'SancoOutputExtraNamelist.select': True,
                                                'SancoOutputExtraNamelist.selItems.rows': 0,
                                                'SancoOutputExtraNamelist.selItems.columns': 3}, 'Sanco')])

    @mock.patch('jetto_tools.jset.ExtraNamelists')
    def test_jset_calls_extra_namelist_constructors_with_optional_extra_jetto_fields(self, mock_extra):
        filter=JSETExtraNamelistsFilterTuple()
        
        jsetfile = JSETFile(
            extra=JSETJettoExtraNamelists(
                filter=filter
            )
        )
        jset = JSET(jsetfile.as_string())

        mock_extra.assert_any_call({'OutputExtraNamelist.select': True,
                                    'OutputExtraNamelist.selItems.rows': 0,
                                    'OutputExtraNamelist.selItems.columns': 3,
                                    'OutputExtraNamelist.filter.active': 'All',
                                    'OutputExtraNamelist.filter.model': 'All',
                                    'OutputExtraNamelist.filter.namelist': 'All'}, '')

    @mock.patch('jetto_tools.jset.ExtraNamelists')
    def test_jset_calls_extra_namelist_constructors_with_optional_extra_sanco_fields(self, mock_extra):
        filter=JSETExtraNamelistsFilterTuple()
        
        jsetfile = JSETFile(
            sanco_extra=JSETSancoExtraNamelists(
                filter=filter
            )
        )
        jset = JSET(jsetfile.as_string())

        mock_extra.assert_any_call({'SancoOutputExtraNamelist.select': True,
                                    'SancoOutputExtraNamelist.selItems.rows': 0,
                                    'SancoOutputExtraNamelist.selItems.columns': 3,
                                    'SancoOutputExtraNamelist.filter.active': 'All',
                                    'SancoOutputExtraNamelist.filter.model': 'All',
                                    'SancoOutputExtraNamelist.filter.namelist': 'All'}, 'Sanco')

    @mock.patch('jetto_tools.jset.ExtraNamelists')
    def test_can_retrieve_extras_from_jset(self, mock_extra):
        def mock_return(settings, prefix):
            if prefix == '':
                return 'foo'
            elif prefix == 'Sanco':
                return 'bar'
            else:
                # Nothing to do
                return None

        mock_extra.side_effect = mock_return

        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        assert jset.extras == 'foo' and jset.sanco_extras == 'bar'

    def test_jetto_extra_namelists_are_removed_from_accessible_settings(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        assert 'OutputExtraNamelist.select' not in jset

    def test_sanco_extra_namelists_are_removed_from_accessible_settings(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        assert 'SancoOutputExtraNamelist.select' not in jset


class TestJSETWriteExtraNamelists:
    """Test that the extra namelists are included as expected in the written JSET"""
    def test_jetto_namelists_are_included_on_jset_write(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        s = str(jset)

        assert TestJSETWrite.extract_jset_field('OutputExtraNamelist.select', s) == 'true' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.rows', s) == '0' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.columns', s) == '3'

    def test_sanco_namelists_are_included_on_jset_write(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        s = str(jset)

        assert TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.select', s) == 'true' and \
               TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.selItems.rows', s) == '0' and \
               TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.selItems.columns', s) == '3'

    def test_addition_of_jetto_namelists_item_included_on_jset_write(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        jset.extras['foo'] = ExtraNamelistItem(0)
        s = str(jset)

        assert TestJSETWrite.extract_jset_field('OutputExtraNamelist.select', s) == 'true' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.rows', s) == '1' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.columns', s) == '3' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.cell[0][0]', s) == 'foo' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.cell[0][1]', s) == '' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.cell[0][2]', s) == '0'

    def test_addition_of_sanco_namelists_item_included_on_jset_write(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        jset.sanco_extras['foo'] = ExtraNamelistItem(0)
        s = str(jset)

        assert TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.select', s) == 'true' and \
               TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.selItems.rows', s) == '1' and \
               TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.selItems.columns', s) == '3' and \
               TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.selItems.cell[0][0]', s) == 'foo' and \
               TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.selItems.cell[0][1]', s) == '' and \
               TestJSETWrite.extract_jset_field('SancoOutputExtraNamelist.selItems.cell[0][2]', s) == '0'

    def test_addition_of_active_item_included_on_jset_write(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        jset.extras['foo'] = ExtraNamelistItem(0, active=True)
        s = str(jset)

        assert TestJSETWrite.extract_jset_field('OutputExtraNamelist.select', s) == 'true' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.rows', s) == '1' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.columns', s) == '4' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.cell[0][0]', s) == 'foo' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.cell[0][1]', s) == '' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.cell[0][2]', s) == '0' and \
               TestJSETWrite.extract_jset_field('OutputExtraNamelist.selItems.cell[0][3]', s) == 'true'


class TestExfileRetrieve:
    """Test that we can retrieve the exfile information from a parsed JSET"""

    def test_can_retrieve_private_exfile(self):
        jsetfile = JSETFile()

        jset = JSET(jsetfile.as_string())

        assert jset.exfile == JSETExfile().name

    def test_can_retrieve_catalogued_exfile(self):
        exfile = JSETExfile(source='Cataloged')
        jsetfile = JSETFile(exfile=exfile)

        jset = JSET(jsetfile.as_string())

        assert jset.exfile == (f"/u/{exfile.owner}/cmg/catalog/"
                               f"{exfile.code}/{exfile.machine}/{exfile.shot}/"
                               f"{exfile.date}/seq#{exfile.seq}/jetto.ex")

    def test_raises_if_source_is_invalid(self):
        exfile = JSETExfile(source='foo')
        jsetfile = JSETFile(exfile=exfile)

        with pytest.raises(JSETError):
            jset = JSET(jsetfile.as_string())


class TestExfileWrite:
    """Test that the updated exfile is written back to the JSET correctly"""

    def test_original_exfile_is_written_back(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        s = str(jset)

        assert _JSET_SETTING_FMT.format('SetUpPanel.exFileName', JSETExfile().name) in s and \
               _JSET_SETTING_FMT.format('SetUpPanel.exFileSource', JSETExfile().source) in s and \
               _JSET_SETTING_FMT.format('SetUpPanel.exFilePrvDir', os.path.dirname(JSETExfile().source)) in s

    def test_updated_private_exfile_is_written_back(self):
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        jset.exfile = '/path/to/jetto.ex'
        s = str(jset)

        assert _JSET_SETTING_FMT.format('SetUpPanel.exFileName', '/path/to/jetto.ex') in s and \
               _JSET_SETTING_FMT.format('SetUpPanel.exFileSource', 'Private') in s and \
               _JSET_SETTING_FMT.format('SetUpPanel.exFilePrvDir', '/path/to') in s

    def test_updated_cataloged_exfile_is_written_back_as_private(self):
        exfile = JSETExfile(source='Cataloged')
        jsetfile = JSETFile(exfile=exfile)
        jset = JSET(jsetfile.as_string())

        jset.exfile = '/path/to/jetto.ex'
        s = str(jset)

        assert _JSET_SETTING_FMT.format('SetUpPanel.exFileName', '/path/to/jetto.ex') in s and \
               _JSET_SETTING_FMT.format('SetUpPanel.exFileSource', 'Private') in s and \
               _JSET_SETTING_FMT.format('SetUpPanel.exFilePrvDir', '/path/to') in s


class TestSetCataloguedRestart:
    """Test that restart settings are applied correctly in a catalogued case"""
    def test_continue_not_selected(self):
        advanced = JSETAdvanced(owner='foo', code='edge2d', machine='iter',
                                shot='92398', date='dec1318', seq='1', continue_='false')
        jsetfile = JSETFile(advanced=advanced)
        jset = JSET(jsetfile.as_string())

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot='12345', date='jan0101', seq='2')

        assert jset['AdvancedPanel.catOwner'] == 'sim' and \
               jset['AdvancedPanel.catCodeID'] == 'jetto' and \
               jset['AdvancedPanel.catMachID'] == 'jet' and \
               jset['AdvancedPanel.catShotID'] == '12345' and \
               jset['AdvancedPanel.catDateID'] == 'jan0101' and \
               jset['AdvancedPanel.catSeqNum'] == '2' and \
               jset['AdvancedPanel.catOwner_R'] == advanced.owner_r and \
               jset['AdvancedPanel.catCodeID_R'] == advanced.code_r and \
               jset['AdvancedPanel.catMachID_R'] == advanced.machine_r and \
               jset['AdvancedPanel.catShotID_R'] == int(advanced.shot_r) and \
               jset['AdvancedPanel.catDateID_R'] == advanced.date_r and \
               jset['AdvancedPanel.catSeqNum_R'] == int(advanced.seq_r)

    def test_continue_selected(self):
        advanced = JSETAdvanced(owner='foo', code='edge2d', machine='iter',
                                shot='92398', date='dec1318', seq='1', continue_='true')
        jsetfile = JSETFile(advanced=advanced)
        jset = JSET(jsetfile.as_string())

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot='12345', date='jan0101', seq='2')

        assert jset['AdvancedPanel.catOwner'] == 'sim' and \
               jset['AdvancedPanel.catCodeID'] == 'jetto' and \
               jset['AdvancedPanel.catMachID'] == 'jet' and \
               jset['AdvancedPanel.catShotID'] == '12345' and \
               jset['AdvancedPanel.catDateID'] == 'jan0101' and \
               jset['AdvancedPanel.catSeqNum'] == '2' and \
               jset['AdvancedPanel.catOwner_R'] == advanced.owner and \
               jset['AdvancedPanel.catCodeID_R'] == advanced.code and \
               jset['AdvancedPanel.catMachID_R'] == advanced.machine and \
               jset['AdvancedPanel.catShotID_R'] == int(advanced.shot) and \
               jset['AdvancedPanel.catDateID_R'] == advanced.date and \
               jset['AdvancedPanel.catSeqNum_R'] == int(advanced.seq)


class TestTimeConfiguration:
    @pytest.fixture
    def time_config(self):
        return common.TimeConfig(start_time=90.0, end_time=101.0, n_esco_times=10, n_output_profile_times=20)

    @pytest.mark.parametrize('jset_id, value', [('SetUpPanel.startTime', 90.0),
                                                ('EquilEscoRefPanel.tvalue.tinterval.startRange', 90.0),
                                                ('OutputStdPanel.profileRangeStart', 90.0),
                                                ('SetUpPanel.endTime', 101.0),
                                                ('EquilEscoRefPanel.tvalue.tinterval.endRange', 101.0),
                                                ('OutputStdPanel.profileRangeEnd', 101.0),
                                                ('EquilEscoRefPanel.tvalue.tinterval.numRange', 10),
                                                ('OutputStdPanel.numOfProfileRangeTimes', 20)])
    def test_set_time_config(self, jset, time_config, jset_id, value):
        jset.set_time_config(time_config)

        assert jset[jset_id] == value

    @pytest.mark.parametrize('attr, value', [('start_time', 0.0),
                                             ('end_time', 10.0),
                                             ('n_esco_times', 0),
                                             ('n_output_profile_times', 0)])
    def test_get_time_config(self, jset, attr, value):
        time_config = jset.get_time_config()

        assert getattr(time_config, attr) == value

    @pytest.mark.parametrize('jset_id', [f'OutputStdPanel.profileFixedTimes[{i}]' for i in range(10)])
    def test_reset_profile_output_times(self, jset, jset_id):
        jset.reset_fixed_output_profiles_times()

        assert jset[jset_id] is None


class TestDriverConfiguration:
    def test_driver_is_std(self, jset):
        jset['JobProcessingPanel.driver'] = Driver.Std.value

        assert jset.driver == Driver.Std

    def test_driver_is_imas(self, jset):
        jset['JobProcessingPanel.driver'] = Driver.IMAS.value

        assert jset.driver == Driver.IMAS

    def test_raises_if_existing_driver_is_unrecognised(self, jset):
        jset['JobProcessingPanel.driver'] = 'foo'

        with pytest.raises(JSETError):
            _ = jset.driver

    def test_driver_is_updated_to_std(self, jset):
        jset['JobProcessingPanel.driver'] = Driver.IMAS.value

        jset.driver = Driver.Std

        assert jset.driver == Driver.Std

    def test_driver_is_updated_to_imas(self, jset):
        jset['JobProcessingPanel.driver'] = Driver.Std.value

        jset.driver = Driver.IMAS

        assert jset.driver == Driver.IMAS

    def test_raises_if_new_driver_is_unrecognised(self, jset):
        with pytest.raises(JSETError):
            jset.driver = 'foo'

    def test_defaults_to_none_if_driver_missing(self):
        s = remove_jset_setting('JobProcessingPanel.driver')
        jset = JSET(s)

        assert jset.driver is None


class TestJSETShotAndMachine:
    @pytest.mark.parametrize('shot', (1, 2, 3))
    def test_get_shot(self, jset, shot):
        jset['SetUpPanel.shotNum'] = shot

        assert jset.shot == shot

    @pytest.mark.parametrize('shot', (1, 2, 3))
    def test_set_shot(self, jset, shot):
        jset.shot = shot

        assert jset['SetUpPanel.shotNum'] == shot

    @pytest.mark.parametrize('machine', ('jet', 'mast-u', 'tcv'))
    def test_get_machine(self, jset, machine):
        jset['SetUpPanel.machine'] = machine

        assert jset.machine == machine

    @pytest.mark.parametrize('machine', ('jet', 'mast-u', 'tcv'))
    def test_set_machine(self, jset, machine):
        jset.machine = machine

        assert jset['SetUpPanel.machine'] == machine


class TestJSET_IMAS:
    @pytest.mark.parametrize('read_ids', (True, False))
    def test_get_read_ids(self, jset, read_ids):
        jset['SetUpPanel.selReadIds'] = read_ids

        assert jset.read_ids is read_ids

    @pytest.mark.parametrize('read_ids', (True, False))
    def test_set_read_ids(self, jset, read_ids):
        jset.read_ids = read_ids

        assert jset['SetUpPanel.selReadIds'] == read_ids

    @pytest.mark.parametrize('write_ids', (True, False))
    def test_get_write_ids(self, jset, write_ids):
        jset['JobProcessingPanel.selIdsRunid'] = write_ids

        assert jset.write_ids is write_ids

    @pytest.mark.parametrize('write_ids', (True, False))
    def test_set_write_ids(self, jset, write_ids):
        jset.write_ids = write_ids

        assert jset['JobProcessingPanel.selIdsRunid'] is write_ids

    @pytest.fixture
    def jset_with_private_ids_source(self, jset):
        jset['SetUpPanel.idsFileSource'] = 'Private'
        jset['SetUpPanel.idsIMASDBMachine'] = 'jet'
        jset['SetUpPanel.idsIMASDBUser'] = 'sim'
        jset['SetUpPanel.idsIMASDBShot'] = 12345
        jset['SetUpPanel.idsIMASDBRunid'] = 2
        jset['SetUpPanel.idsFilePrvDir'] = '/home/sim'
        jset['SetUpPanel.idsFileName'] = '/home/sim/imasdb'

        return jset

    def test_get_input_ids_source_private(self, jset_with_private_ids_source):
        assert isinstance(jset_with_private_ids_source.input_ids_source, IMASDB)

    def test_get_input_ids_source_private_fields(self, jset_with_private_ids_source):
        assert jset_with_private_ids_source.input_ids_source == IMASDB('sim', 'jet', 12345, 2)

    @pytest.fixture
    def jset_with_catalogue_ids_source(self, jset):
        jset['SetUpPanel.idsFileSource'] = 'Cataloged'
        jset['SetUpPanel.idsFileCatOwner'] = 'sim'
        jset['SetUpPanel.idsFileCatCodeID'] = 'jetto'
        jset['SetUpPanel.idsFileCatMachID'] = 'jet'
        jset['SetUpPanel.idsFileCatShotID'] = 12345
        jset['SetUpPanel.idsFileCatDateID'] = 'jan0101'
        jset['SetUpPanel.idsFileCatSeqNum'] = 2
        jset['SetUpPanel.idsFilePrvDir'] = ''
        jset['SetUpPanel.idsFileName'] = '/common/simdb/simulations/abcd/imasdb/jet/3/12345/2'

        return jset

    def test_get_input_ids_source_catalogue(self, jset_with_catalogue_ids_source):
        assert isinstance(jset_with_catalogue_ids_source.input_ids_source, CatalogueId)

    def test_get_input_ids_source_private_fields(self, jset_with_catalogue_ids_source):
        assert jset_with_catalogue_ids_source.input_ids_source == CatalogueId('sim', 'jetto', 'jet', 12345, 'jan0101', 2)

    def test_set_input_ids_source_private_updates_fields(self, jset_with_private_ids_source):
        jset_with_private_ids_source.input_ids_source = IMASDB('foo', 'iter', 54321, 3)

        assert jset_with_private_ids_source['SetUpPanel.idsIMASDBUser'] == 'foo' and \
               jset_with_private_ids_source['SetUpPanel.idsIMASDBMachine'] == 'iter' and \
               jset_with_private_ids_source['SetUpPanel.idsIMASDBShot'] == 54321 and \
               jset_with_private_ids_source['SetUpPanel.idsIMASDBRunid'] == 3

    def test_set_input_ids_source_from_cataloged_to_private_updates_fields(self, jset_with_catalogue_ids_source):
        jset_with_catalogue_ids_source.input_ids_source = IMASDB('foo', 'iter', 54321, 3)

        assert jset_with_catalogue_ids_source['SetUpPanel.idsIMASDBUser'] == 'foo' and \
               jset_with_catalogue_ids_source['SetUpPanel.idsIMASDBMachine'] == 'iter' and \
               jset_with_catalogue_ids_source['SetUpPanel.idsIMASDBShot'] == 54321 and \
               jset_with_catalogue_ids_source['SetUpPanel.idsIMASDBRunid'] == 3 and \
               jset_with_catalogue_ids_source['SetUpPanel.idsFileSource'] == 'Private' and \
               jset_with_catalogue_ids_source['SetUpPanel.idsFilePrvDir'] == ''

    def test_set_input_ids_source_from_private_to_catalogued_not_allowed(self, jset_with_private_ids_source):
        with pytest.raises(JSETError):
            jset_with_private_ids_source.input_ids_source = CatalogueId('foo', 'jetto', 'iter', 12345, 'jan0101', 1)

    @pytest.mark.parametrize('user, file_name', (('root', '/root/public/imasdb/iter/3/54321/3'),
                                                 ('/path/to/imasdb', '/path/to/imasdb/iter/3/54321/3')))
    def test_set_input_ids_source_private_relative_updates_filename_hdf5(self, jset_with_private_ids_source, user, file_name, monkeypatch):
        with monkeypatch.context() as m:
            m.setenv('JINTRAC_IMAS_BACKEND', 'HDF5')

            jset_with_private_ids_source.input_ids_source = IMASDB(user, 'iter', 54321, 3)

            assert jset_with_private_ids_source['SetUpPanel.idsFileName'] == file_name and \
                   jset_with_private_ids_source['SetUpPanel.idsFilePrvDir'] == ''

    @pytest.mark.parametrize('user, run, file_name', (('root', 0, '/root/public/imasdb/iter/3/0'),
                                                      ('root', 10000, '/root/public/imasdb/iter/3/1'),
                                                      ('/path/to/imasdb', 25000, '/path/to/imasdb/iter/3/2'),
                                                      ('/path/to/imasdb', 36660, '/path/to/imasdb/iter/3/3')))
    def test_set_input_ids_source_private_relative_updates_filename_mdsplus(self, jset_with_private_ids_source, user,
                                                                            file_name, run, monkeypatch):
        with monkeypatch.context() as m:
            m.setenv('JINTRAC_IMAS_BACKEND', 'MDSPLUS')

            jset_with_private_ids_source.input_ids_source = IMASDB(user, 'iter', 54321, run)

            assert jset_with_private_ids_source['SetUpPanel.idsFileName'] == file_name and \
                   jset_with_private_ids_source['SetUpPanel.idsFilePrvDir'] == ''


class TestApplyBlueprintCoilset:
    @pytest.fixture
    def pfcnum(self):
        return 6

    @pytest.fixture
    def pfcrcen(self):
        return [1.5, 1.5,
                1.5, 1.5,
                8.276353050783275, 8.276353050783275]

    @pytest.fixture
    def pfczcen(self):
        return [8.787573575105338, -8.787573575105338,
                11.307573575105339, -11.307573575105339,
                11.807573575105339, -11.807573575105339]

    @pytest.fixture
    def pfcrwid(self):
        return [0.175 * 2, 0.175 * 2,
                0.25 * 2, 0.25 * 2,
                0.25 * 2, 0.25 * 2]

    @pytest.fixture
    def pfczwid(self):
        return [0.5 * 2, 0.5 * 2,
                0.4 * 2, 0.4 * 2,
                0.4 * 2, 0.4 * 2]

    @pytest.fixture
    def currents(self):
        return [6647346.633462137, 6647346.633462137, 4779115.224674427,
                4779115.224674427, 7951137.5930257235, 7951137.5930257235]

    @pytest.fixture
    def coilset(self, pfcrcen, pfczcen, pfcrwid, pfczwid, currents):
        return {
            k: {
                "x": pfcrcen[i],
                "z": pfczcen[i],
                "dx": pfcrwid[i] / 2,
                "dz": pfczwid[i] / 2,
                "current": currents[i]
            }
            for i, k in enumerate(["PF_1.1", "PF_1.2", "PF_2.1", "PF_2.2", "PF_3.1", "PF_3.2"])
        }

    def test_pfcnum_set(self, jset, coilset, pfcnum):
        jset.apply_bp_coilset(coilset)

        assert jset.extras['PFCNUM'][None] == pfcnum

    def test_pfcrcen_set(self, jset, coilset, pfcrcen):
        jset.apply_bp_coilset(coilset)

        assert jset.extras['PFCRCEN'] == ExtraNamelistItem(pfcrcen, 1)

    def test_pfczcen_set(self, jset, coilset, pfczcen):
        jset.apply_bp_coilset(coilset)

        assert jset.extras['PFCZCEN'] == ExtraNamelistItem(pfczcen, 1)

    def test_pfcrwid_set(self, jset, coilset, pfcrwid):
        jset.apply_bp_coilset(coilset)

        assert jset.extras['PFCRWID'] == ExtraNamelistItem(pfcrwid, 1)

    def test_pfczwid_set(self, jset, coilset, pfczwid):
        jset.apply_bp_coilset(coilset)

        assert jset.extras['PFCZWID'] == ExtraNamelistItem(pfczwid, 1)

    def test_pfciplin_not_set(self, jset, coilset):
        jset.apply_bp_coilset(coilset)

        assert 'PFCIPLIN' not in jset.extras

    @pytest.mark.parametrize('coil, label',
                             zip(range(1, 7), ['PF_1.1', 'PF_1.2', 'PF_2.1', 'PF_2.2', 'PF_3.1', 'PF_3.2']))
    def test_pfciplin_set(self, jset, coilset, coil, label):
        jset.extras['PFCIPLINNUM'] = ExtraNamelistItem(2)

        jset.apply_bp_coilset(coilset)

        assert jset.extras['PFCIPLIN'][1, coil] == coilset[label]['current'] and \
               jset.extras['PFCIPLIN'][2, coil] == coilset[label]['current']

    def test_coils_with_zero_current_are_removed_by_default(self, jset, coilset):
        for coil in coilset:
            if coil != 'PF_2.1':
                coilset[coil]['current'] = 0.0

        jset.apply_bp_coilset(coilset)

        assert jset.extras['PFCNUM'][None] == 1 and \
               jset.extras['PFCRCEN'][1] == coilset['PF_2.1']['x'] and \
               jset.extras['PFCZCEN'][1] == coilset['PF_2.1']['z'] and \
               jset.extras['PFCRWID'][1] == coilset['PF_2.1']['dx'] * 2 and \
               jset.extras['PFCZWID'][1] == coilset['PF_2.1']['dz'] * 2

    def test_coils_with_zero_current_are_included_if_requested(self, jset, coilset):
        pfcrcen = [1.5, 1.5,
                   1.5, 1.5,
                   8.276353050783275, 8.276353050783275]
        for coil in coilset:
            if coil != 'PF_2.1':
                coilset[coil]['current'] = 0.0

        jset.apply_bp_coilset(coilset, include_zero_current_coils=True)

        assert jset.extras['PFCNUM'][None] == len(coilset) and \
               jset.extras['PFCRCEN'] == ExtraNamelistItem(pfcrcen, 1)

    @pytest.mark.parametrize('coil, label',
                             zip(range(1, 7), ['PF_1.1', 'PF_1.2', 'PF_2.1', 'PF_2.2', 'PF_3.1', 'PF_3.2']))
    def test_zero_currents_are_set_in_pfciplin(self, jset, coilset, coil, label):
        jset.extras['PFCIPLINNUM'] = ExtraNamelistItem(2)

        coilset[label]['current'] = 0.0
        jset.apply_bp_coilset(coilset, include_zero_current_coils=True)

        assert jset.extras['PFCIPLIN'][1, coil] == 0.0 and \
               jset.extras['PFCIPLIN'][2, coil] == 0.0


class TestSetGenericCataloguedFile:
    """Test that we can set files to be catalogued where the file requires no special handling"""
    @pytest.mark.parametrize('panel, prefix', [('LHPanel', 'FRTC'),
                                               ('EquilEqdskRefPanel', 'eqdskFile'),
                                               ('EquilCbankRefPanel', 'cbankFile'),
                                               ('ECRHPanel', 'GRAY'),
                                               ('EquilCreateNLRefPanel', 'Create'),
                                               ('EquilCreateNLRefPanel', 'CreateNominalRef'), ],
                             ids=['FRTC', 'EquilEqdsk', 'Cbank', 'GRAY', 'CreateNLRef', 'CreateNomRef'])
    def test_set_catalogued_file(self, panel, prefix):
        if prefix == 'exFile':
            file_flag = False
            file_postfix = ''
        else:
            file_flag = True
            file_postfix = 'File'

        file = JETTOFile(panel=panel, prefix=prefix,
                         owner='foo', code='edge2d', machine='iter',
                         shot='92398', date='dec1318', seq='1', source='Private', file_flag=file_flag)
        jsetfile = JSETFile(jetto_files=[file])
        s = jsetfile.as_string()
        jset = JSET(s)

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot='12345', date='jan0101', seq='2')

        assert jset[f'{panel}.{prefix}Source'] == 'Cataloged' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'sim' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'jetto' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'jet' and \
               jset[f'{panel}.{prefix}CatShotID'] == '12345' and \
               jset[f'{panel}.{prefix}CatDateID'] == 'jan0101' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == '2' and \
               jset[f'{panel}.{prefix}PrvDir'] == '' and \
               jset[f'{panel}.{prefix}{file_postfix}Name'] == ''


class TestSetExFileCataloguedFile:
    def test_set_catalogued_file(self):
        full_prefix = 'SetUpPanel.exFile'
        jsetfile = JSETFile()
        jset = JSET(jsetfile.as_string())

        jset[f'{full_prefix}Source'] = 'Private'
        jset[f'{full_prefix}Name'] = '/path/to/exFile.ex'

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot='12345', date='jan0101', seq='2')

        assert jset[f'{full_prefix}Source'] == 'Cataloged' and \
               jset[f'{full_prefix}CatOwner'] == 'sim' and \
               jset[f'{full_prefix}CatCodeID'] == 'jetto' and \
               jset[f'{full_prefix}CatMachID'] == 'jet' and \
               jset[f'{full_prefix}CatShotID'] == '12345' and \
               jset[f'{full_prefix}CatDateID'] == 'jan0101' and \
               jset[f'{full_prefix}CatSeqNum'] == '2' and \
               jset[f'{full_prefix}PrvDir'] == '' and \
               jset[f'{full_prefix}Name'] == ''


class TestSetReadIDSCataloguedFile:
    def test_set_catalogued_file(self):
        panel = 'SetUpPanel'
        prefix = 'idsFile'
        file = JETTOFile(panel=panel, prefix=prefix,
                         owner='foo', code='jetto', machine='step',
                         shot='88888', date='dec1318', seq='1', source='Private', file_flag=False)
        jsetfile = JSETFile(jetto_files=[file])
        jset = JSET(jsetfile.as_string())

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot='12345', date='jan0101', seq='2')

        assert jset[f'{panel}.{prefix}Source'] == 'Cataloged' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'sim' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'jetto' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'jet' and \
               jset[f'{panel}.{prefix}CatShotID'] == '12345' and \
               jset[f'{panel}.{prefix}CatDateID'] == 'jan0101' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == '2' and \
               jset[f'{panel}.{prefix}PrvDir'] == '' and \
               jset[f'{panel}.{prefix}Name'] == ''


class TestSetGRAYBeamCataloguedFile:
    """Test that we can set the ECRH GRAY Beam file to be catalogued

    Requires separate handling from the other generic files, as JAMS is inconsistent in naming"""
    def test_set_catalogued_file(self):
        file = JETTOFile(panel='ECRHPanel', prefix='GRAY',
                         owner='foo', code='edge2d', machine='iter',
                         shot='92398', date='dec1318', seq='1', source='Private', file_flag=False)
        jsetfile = JSETFile(jetto_files=[file])
        jset = JSET(jsetfile.as_string())

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot='12345', date='jan0101', seq='2')

        full_prefix = 'ECRHPanel.GRAY'
        assert jset[f'{full_prefix}BeamSource'] == 'Cataloged' and \
               jset[f'{full_prefix}CatOwner'] == 'sim' and \
               jset[f'{full_prefix}CatCodeID'] == 'jetto' and \
               jset[f'{full_prefix}CatMachID'] == 'jet' and \
               jset[f'{full_prefix}CatShotID'] == '12345' and \
               jset[f'{full_prefix}CatDateID'] == 'jan0101' and \
               jset[f'{full_prefix}CatSeqNum'] == '2' and \
               jset[f'{full_prefix}BeamPrvDir'] == '' and \
               jset[f'{full_prefix}BeamFileName'] == ''


class TestSetCataloguedEscoEquilFile:
    @pytest.fixture()
    def jset(self):
        file = JETTOFile(panel='EquilEscoRefPanel', prefix='eqdskFile',
                         owner='foo', code='edge2d', machine='iter',
                         shot='92398', date='dec1318', seq='1', source='Private', file_flag=False)
        jsetfile = JSETFile(jetto_files=[file])
        return JSET(jsetfile.as_string())

    @pytest.mark.parametrize('source, boundary',
                             [('', ''),
                              ('ESCO', ''),
                              ('', 'EQDSK using FLUSH')],
                             ids=['Both disabled', 'Boundary disabled', 'Source disabled'])
    def test_file_not_catalogued(self, jset, source, boundary):
        panel = 'EquilEscoRefPanel'
        prefix = 'eqdskFile'
        jset['EquilibriumPanel.source'] = source
        jset['EquilEscoRefPanel.boundSource'] = boundary

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Private' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'foo' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'edge2d' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'iter' and \
               jset[f'{panel}.{prefix}CatShotID'] == 92398 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'dec1318' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 1 and \
               jset[f'{panel}.{prefix}PrvDir'] == '/path/to/prev/dir' and \
               jset[f'{panel}.{prefix}Name'] == '/path/to/prev/dir/file.ext'

    @pytest.mark.parametrize('boundary', ['EQDSK directly', 'EQDSK using FLUSH'], ids=['Direct', 'FLUSH'])
    def test_file_catalogued(self, jset, boundary):
        panel = 'EquilEscoRefPanel'
        prefix = 'eqdskFile'
        jset['EquilibriumPanel.source'] = 'ESCO'
        jset['EquilEscoRefPanel.boundSource'] = boundary

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Cataloged' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'sim' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'jetto' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'jet' and \
               jset[f'{panel}.{prefix}CatShotID'] == 12345 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'jan0101' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 2 and \
               jset[f'{panel}.{prefix}PrvDir'] == '' and \
               jset[f'{panel}.{prefix}Name'] == ''


class TestSetCataloguedWFPanelFile:
    @pytest.fixture()
    def jset(self):
        file = JETTOFile(panel='ExternalWFPanel', prefix='CfgFile',
                         owner='foo', code='edge2d', machine='iter',
                         shot='92398', date='dec1318', seq='1', source='Private', file_flag=False)
        jsetfile = JSETFile(jetto_files=[file])
        return JSET(jsetfile.as_string())

    def test_file_not_catalogued(self, jset):
        panel = 'ExternalWFPanel'
        prefix = 'CfgFile'
        jset['ExternalWFPanel.select'] = False

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Private' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'foo' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'edge2d' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'iter' and \
               jset[f'{panel}.{prefix}CatShotID'] == 92398 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'dec1318' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 1 and \
               jset[f'{panel}.{prefix}PrvDir'] == '/path/to/prev/dir' and \
               jset[f'{panel}.{prefix}Name'] == '/path/to/prev/dir/file.ext'

    def test_file_catalogued(self, jset):
        panel = 'ExternalWFPanel'
        prefix = 'CfgFile'
        jset['ExternalWFPanel.select'] = True

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Cataloged' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'sim' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'jetto' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'jet' and \
               jset[f'{panel}.{prefix}CatShotID'] == 12345 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'jan0101' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 2 and \
               jset[f'{panel}.{prefix}PrvDir'] == '' and \
               jset[f'{panel}.{prefix}Name'] == ''


class TestSetCataloguedEscoBndFile:
    @pytest.fixture()
    def jset(self):
        file = JETTOFile(panel='EquilEscoRefPanel', prefix='bndFile',
                         owner='foo', code='edge2d', machine='iter',
                         shot='92398', date='dec1318', seq='1', source='Private', file_flag=False)
        jsetfile = JSETFile(jetto_files=[file])
        return JSET(jsetfile.as_string())

    @pytest.mark.parametrize('source, boundary',
                             [('', ''),
                              ('ESCO', ''),
                              ('', 'Boundary File')],
                             ids=['Both disabled', 'Boundary disabled', 'Source disabled'])
    def test_file_not_catalogued(self, jset, source, boundary):
        panel = 'EquilEscoRefPanel'
        prefix = 'bndFile'
        jset['EquilibriumPanel.source'] = source
        jset['EquilEscoRefPanel.boundSource'] = boundary

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Private' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'foo' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'edge2d' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'iter' and \
               jset[f'{panel}.{prefix}CatShotID'] == 92398 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'dec1318' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 1 and \
               jset[f'{panel}.{prefix}PrvDir'] == '/path/to/prev/dir' and \
               jset[f'{panel}.{prefix}Name'] == '/path/to/prev/dir/file.ext'

    def test_file_catalogued(self, jset):
        panel = 'EquilEscoRefPanel'
        prefix = 'bndFile'
        jset['EquilibriumPanel.source'] = 'ESCO'
        jset['EquilEscoRefPanel.boundSource'] = 'Boundary File'

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Cataloged' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'sim' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'jetto' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'jet' and \
               jset[f'{panel}.{prefix}CatShotID'] == 12345 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'jan0101' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 2 and \
               jset[f'{panel}.{prefix}PrvDir'] == '' and \
               jset[f'{panel}.{prefix}Name'] == ''


class TestSetCataloguedSancoTransportFile:
    @pytest.fixture()
    def transport_file(self):
        return JETTOFile(panel='SancoTransportPanel', prefix='transport',
                         owner='foo', code='edge2d', machine='iter',
                         shot='92398', date='dec1318', seq='1', source='Private', file_flag=True)

    @pytest.mark.parametrize('impurity_select, source, transport_select',
                             [('false', 'Sanco', 'true'),
                              ('true', '', 'true'),
                              ('true', 'Sanco', 'false')],
                             ids=['Impurities disabled',
                                  'Sanco disabled',
                                  'Transport disabled'])
    def test_file_not_catalogued(self, transport_file, impurity_select, source, transport_select):
        jsetfile = JSETFile(jetto_files=[transport_file],
                            impurities=JSETImpurities(select=impurity_select, source=source),
                            sanco=JSETSanco(transport_select=transport_select))
        jset = JSET(jsetfile.as_string())

        panel = 'SancoTransportPanel'
        prefix = 'transport'

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Private' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'foo' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'edge2d' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'iter' and \
               jset[f'{panel}.{prefix}CatShotID'] == 92398 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'dec1318' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 1 and \
               jset[f'{panel}.{prefix}PrvDir'] == '/path/to/prev/dir' and \
               jset[f'{panel}.{prefix}FileName'] == '/path/to/prev/dir/file.ext'

    def test_file_catalogued(self, transport_file):
        jsetfile = JSETFile(jetto_files=[transport_file],
                            impurities=JSETImpurities(select='true', source='Sanco'),
                            sanco=JSETSanco(transport_select='true'))
        jset = JSET(jsetfile.as_string())

        panel = 'SancoTransportPanel'
        prefix = 'transport'

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Cataloged' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'sim' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'jetto' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'jet' and \
               jset[f'{panel}.{prefix}CatShotID'] == 12345 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'jan0101' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 2 and \
               jset[f'{panel}.{prefix}PrvDir'] == '' and \
               jset[f'{panel}.{prefix}FileName'] == '/u/sim/cmg/catalog/jetto/jet/12345/jan0101/seq#2/jetto.str'


class TestSetCataloguedSancoGridFile:
    @pytest.fixture()
    def grid_file(self):
        return JETTOFile(panel='SancoOtherPanel', prefix='gridFile',
                         owner='foo', code='edge2d', machine='iter',
                         shot='92398', date='dec1318', seq='1', source='Private', file_flag=False)

    @pytest.mark.parametrize('impurity_select, source, grid_select',
                             [('false', 'Sanco', 'true'),
                              ('true', '', 'true'),
                              ('true', 'Sanco', 'false')],
                             ids=['Impurities disabled',
                                  'Sanco disabled',
                                  'Grid disabled'])
    def test_file_not_catalogued(self, grid_file, impurity_select, source, grid_select):
        jsetfile = JSETFile(jetto_files=[grid_file],
                            impurities=JSETImpurities(select=impurity_select, source=source),
                            sanco=JSETSanco(grid_select=grid_select))
        jset = JSET(jsetfile.as_string())

        panel = 'SancoOtherPanel'
        prefix = 'gridFile'

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Private' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'foo' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'edge2d' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'iter' and \
               jset[f'{panel}.{prefix}CatShotID'] == 92398 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'dec1318' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 1 and \
               jset[f'{panel}.{prefix}PrvDir'] == '/path/to/prev/dir' and \
               jset[f'{panel}.{prefix}Name'] == '/path/to/prev/dir/file.ext'

    def test_file_catalogued(self, grid_file):
        jsetfile = JSETFile(jetto_files=[grid_file],
                            impurities=JSETImpurities(select='true', source='Sanco'),
                            sanco=JSETSanco(grid_select='true'))
        jset = JSET(jsetfile.as_string())

        panel = 'SancoOtherPanel'
        prefix = 'gridFile'

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Cataloged' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'sim' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'jetto' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'jet' and \
               jset[f'{panel}.{prefix}CatShotID'] == 12345 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'jan0101' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 2 and \
               jset[f'{panel}.{prefix}PrvDir'] == '' and \
               jset[f'{panel}.{prefix}Name'] == '/u/sim/cmg/catalog/jetto/jet/12345/jan0101/seq#2/jetto.sgrid'


class TestSetNBIAscotFile:
    @pytest.fixture()
    def ascot_file(self):
        return JETTOFile(panel='NBIAscotRef', prefix='config',
                         owner='foo', code='edge2d', machine='iter',
                         shot='92398', date='dec1318', seq='1', source='Private', file_flag=True)

    @pytest.mark.parametrize('select, source, ascot_source',
                             [('false', 'Ascot', 'From File'),
                              ('true', '', 'From File'),
                              ('true', 'Ascot', '')],
                             ids=['NBI disabled',
                                  'Ascot disabled',
                                  'Ascot file disabled'])
    def test_file_not_catalogued(self, ascot_file, select, source, ascot_source):
        jsetfile = JSETFile(jetto_files=[ascot_file],
                            nbi=JSETNBI(select=select, source=source, ascot_source=ascot_source))
        jset = JSET(jsetfile.as_string())

        panel = 'NBIAscotRef'
        prefix = 'config'

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Private' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'foo' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'edge2d' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'iter' and \
               jset[f'{panel}.{prefix}CatShotID'] == 92398 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'dec1318' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 1 and \
               jset[f'{panel}.{prefix}PrvDir'] == '/path/to/prev/dir' and \
               jset[f'{panel}.{prefix}FileName'] == '/path/to/prev/dir/file.ext'

    def test_file_catalogued(self, ascot_file):
        jsetfile = JSETFile(jetto_files=[ascot_file],
                            nbi=JSETNBI(select='true', source='Ascot', ascot_source='From File'))
        jset = JSET(jsetfile.as_string())

        panel = 'NBIAscotRef'
        prefix = 'config'

        jset.set_catalogued_files(owner='sim', code='jetto', machine='jet',
                                  shot=12345, date='jan0101', seq=2)

        assert jset[f'{panel}.{prefix}Source'] == 'Cataloged' and \
               jset[f'{panel}.{prefix}CatOwner'] == 'sim' and \
               jset[f'{panel}.{prefix}CatCodeID'] == 'jetto' and \
               jset[f'{panel}.{prefix}CatMachID'] == 'jet' and \
               jset[f'{panel}.{prefix}CatShotID'] == 12345 and \
               jset[f'{panel}.{prefix}CatDateID'] == 'jan0101' and \
               jset[f'{panel}.{prefix}CatSeqNum'] == 2 and \
               jset[f'{panel}.{prefix}PrvDir'] == '' and \
               jset[f'{panel}.{prefix}FileName'] == ''


class TestSetBackwardsCompatibility:
    def test_no_change_if_date_greater_than_threshold(self):
        jsetfile = JSETFile(details=JSETDetails(version=_JSET_SETTING_FMT.format('Version', 'v271010')),
                            equations=JSETEquations(usage='Interpretive'),
                            bound_cond=JSETBoundCond(faraday='', current=''))
        jset = JSET(jsetfile.as_string())

        jset.set_backwards_compatibility()

        assert jset['BoundCondPanel.faradayOption'] is None and \
               jset['BoundCondPanel.current'] is None

    def test_no_change_if_current_not_interpretive(self):
        jsetfile = JSETFile(details=JSETDetails(version=_JSET_SETTING_FMT.format('Version', 'v251010')),
                            equations=JSETEquations(usage='Predictive'),
                            bound_cond=JSETBoundCond(faraday='', current=''))
        jset = JSET(jsetfile.as_string())

        jset.set_backwards_compatibility()

        assert jset['BoundCondPanel.faradayOption'] is None and \
               jset['BoundCondPanel.current'] is None

    def test_change_if_date_less_than_threshold(self):
        jsetfile = JSETFile(details=JSETDetails(version=_JSET_SETTING_FMT.format('Version', 'v251010')),
                            equations=JSETEquations(usage='Interpretive'),
                            bound_cond=JSETBoundCond(faraday='', current=''))
        jset = JSET(jsetfile.as_string())

        jset.set_backwards_compatibility()

        assert jset['BoundCondPanel.faradayOption'] == 'Current (amps)' and \
               jset['BoundCondPanel.current'] == 'From PPF'

    def test_change_if_date_equals_threshold(self):
        jsetfile = JSETFile(details=JSETDetails(version=_JSET_SETTING_FMT.format('Version', 'v261010')),
                            equations=JSETEquations(usage='Interpretive'),
                            bound_cond=JSETBoundCond(faraday='', current=''))
        jset = JSET(jsetfile.as_string())

        jset.set_backwards_compatibility()

        assert jset['BoundCondPanel.faradayOption'] == 'Current (amps)' and \
               jset['BoundCondPanel.current'] == 'From PPF'


class TestSetAdvancedPanel:
    def test_params_set_if_continuation(self):
        jsetfile = JSETFile(advanced=JSETAdvanced(continue_='true', restart='false', repeat='true'))
        jset = JSET(jsetfile.as_string())

        jset.set_restart_flags(continue_=True)

        assert jset.continue_ is True and jset.restart is True and jset.repeat is False

    def test_params_set_if_not_continuation_and_is_restart(self):
        jsetfile = JSETFile(advanced=JSETAdvanced(continue_='true', restart='true', repeat='false'))
        jset = JSET(jsetfile.as_string())

        jset.set_restart_flags(continue_=False)

        assert jset.continue_ is False and jset.restart is True and jset.repeat is True

    def test_params_set_if_not_continuation_and_is_not_restart(self):
        jsetfile = JSETFile(advanced=JSETAdvanced(continue_='true', restart='false', repeat='false'))
        jset = JSET(jsetfile.as_string())

        jset.set_restart_flags(continue_=False)

        assert jset.continue_ is True and jset.restart is False and jset.repeat is False
