from jetto_tools.namelist import Namelist, NamelistError, read, write
from collections import namedtuple
import pytest
import datetime
import re
import pathlib

_HEADER = """================================================================================
                             CODE INPUT NAMELIST FILE
================================================================================"""

_APP = "JETTO"
_VERSION = "v060619"
_DATE = '08/08/2019'
_TIME = '16:43:37'
_REPO = "/home/sim/cmg/jams/v060619/java"
_TAG = "Release-v060619"
_BRANCH = "master"
_SHA = "638c06e07629f5d100da166aac3e2d2da5727631"
_STATUS = "Clean"

properties_1 = ('application',
                'version',
                'date',
                'time')
properties_2 = ('repo',
              'tag',
              'branch',
              'sha',
              'status')

NmlHeaderTuple = namedtuple('NmlHeaderTuple', properties_1 + properties_2)
NmlHeaderTuple.__new__.__defaults__ = (_APP, _VERSION, _DATE, _TIME, _REPO, _TAG, _BRANCH, _SHA, _STATUS)

header_descriptions_1 = ('Application',
                         'JAMS Version',
                         'Date',
                         'Time'
                         )
header_descriptions_2 = ('Current GIT repository',
                         'Current GIT release tag',
                         'Current GIT branch',
                         'Last commit SHA1-key',
                         'Repository status')
header_descriptions = header_descriptions_1 + header_descriptions_2

class NmlHeader(NmlHeaderTuple):
    def as_string(self):
        """Format the header as a string

        For testing purposes, skips the row of the header if the field value is 'None'
        """
        return '\n'.join([_HEADER,
                          '',
                          '\n'.join(['{:31}: {}'.format(d, getattr(self, p)) for d, p in
                                     zip(header_descriptions_1, properties_1) if getattr(self, p) is not None]),
                          '',
                          'JAMS GIT information:-',
                          '',
                          '\n'.join(['{:31}: {}'.format(d, getattr(self, p)) for d, p in
                                     zip(header_descriptions_2, properties_2) if getattr(self, p) is not None]),
                          '',
                          ''])

_test_props = {'application'    : ('COCONUT', 'EDGE2D'),
               'version'        : ('v012345', 'v543210',),
               'date'           : ('01/01/1970', '06/07/2020'),
               'time'           : ('11:22:33', '12:13:14'),
               'repo'           : ('/home/sim/myrepo', 'home/sim/myotherrepo'),
               'tag'            : ('Release-v060619', 'Release-v060619'),
               'branch'         : ('master', 'development'),
               'sha'            : ('123456789ABCDEF', 'FEDCAB987654321'),
               'status'         : ('Dirty', 'Committed')}


class TestHeaderParsing:
    """Test that we can retrieve values from a parsed namelist header"""

    @pytest.mark.parametrize('value', _test_props['application'])
    def test_application(self, value):
        nml_header = NmlHeader(application=value)
        nml = Namelist(nml_header.as_string())

        assert nml.application == value

    @pytest.mark.parametrize('value', _test_props['version'])
    def test_version(self, value):
        nml_header = NmlHeader(version=value)
        nml = Namelist(nml_header.as_string())

        assert nml.version == value

    @pytest.mark.parametrize('value', _test_props['date'])
    def test_date(self, value):
        nml_header = NmlHeader(date=value)
        nml = Namelist(nml_header.as_string())

        assert nml.date == datetime.datetime.strptime(value, '%d/%m/%Y').date()

    @pytest.mark.parametrize('value', _test_props['time'])
    def test_time(self, value):
        nml_header = NmlHeader(time=value)
        nml = Namelist(nml_header.as_string())

        assert nml.time == datetime.datetime.strptime(value, '%H:%M:%S').time()

    @pytest.mark.parametrize('value', _test_props['repo'])
    def test_repo(self, value):
        nml_header = NmlHeader(repo=value)
        nml = Namelist(nml_header.as_string())

        assert nml.repo == value

    @pytest.mark.parametrize('value', _test_props['tag'])
    def test_tag(self, value):
        nml_header = NmlHeader(tag=value)
        nml = Namelist(nml_header.as_string())

        assert nml.tag == value

    @pytest.mark.parametrize('value', _test_props['branch'])
    def test_branch(self, value):
        nml_header = NmlHeader(branch=value)
        nml = Namelist(nml_header.as_string())

        assert nml.branch == value

    @pytest.mark.parametrize('value', _test_props['sha'])
    def test_sha(self, value):
        nml_header = NmlHeader(sha=value)
        nml = Namelist(nml_header.as_string())

        assert nml.sha == value

    @pytest.mark.parametrize('value', _test_props['status'])
    def test_status(self, value):
        nml_header = NmlHeader(status=value)
        nml = Namelist(nml_header.as_string())

        assert nml.status == value

    def test_raises_if_unrecognised_property_is_requested(self):
        nml_header = NmlHeader()
        nml = Namelist(nml_header.as_string())

        with pytest.raises(NamelistError):
            _ = nml.nonexistent

    @pytest.mark.parametrize('prop, default', Namelist._DEFAULT_PROPS.items())
    def test_missing_header_field_is_set_to_default_value(self, prop, default):
        nml_header = NmlHeader(**{prop : None})
        nml = Namelist(nml_header.as_string())

        assert getattr(nml, prop) == default

    def test_raises_if_date_cannot_be_parsed(self):
        nml_header = NmlHeader(date='foo')

        with pytest.raises(NamelistError):
            _ = Namelist(nml_header.as_string())

    def test_raises_if_time_cannot_be_parsed(self):
        nml_header = NmlHeader(time='foo')

        with pytest.raises(NamelistError):
            _  = Namelist(nml_header.as_string())

class TestHeaderUpdate:
    """Test that we can update values from a parsed namelist"""
    @pytest.mark.parametrize('prop', _test_props)
    def test_update_property(self, prop):
        new_value = _test_props[prop][0]
        nml_header = NmlHeader()
        nml = Namelist(nml_header.as_string())

        setattr(nml, prop, new_value)

        assert getattr(nml, prop) == new_value

    def test_raises_if_unrecognised_property_is_updated(self):
        nml_header = NmlHeader()
        nml = Namelist(nml_header.as_string())

        with pytest.raises(NamelistError):
            nml.nonexistent = ''


NmlTuple = namedtuple('NmlTuple', ['header', 'namelists'])
NmlTuple.__new__.__defaults__ = (NmlHeader(), [])


class NmlTester(NmlTuple):
    def as_string(self):
        return '\n'.join([self.header.as_string(),
                          '',
                          '',
                          '\n\n\n'.join(n for n in self.namelists)])


test_namelist_1 = """--------------------------------------------------------------------------------
 Namelist : INNBI
--------------------------------------------------------------------------------

 &INNBI
  BMASS3   =  2.0      ,
  ENERG3   =  80000.0  ,
  JPINI3   =  1        ,  0        ,  0        ,  0        ,  0        ,
              0        ,  0        ,  0        ,  0        ,  0        ,
              0        ,  0        ,
  NBREF3   =  40       ,
  PFRAC3   =  0.5      ,  0.3      ,  0.2      ,
  CURTI    =  0.1      ,  0.1      ,
 &END"""

test_name_list_2 = """--------------------------------------------------------------------------------
 Namelist : NLIST2
--------------------------------------------------------------------------------

 &NLIST2
  ISYNTHDIAG=  0        ,
  ITOUT    =  1        ,
  KWFRAN   =  0        ,
  KWLH     =  0        ,
  KWMAIN   =  1        ,
  NTINT    =  100      ,
  NTPR     =  20       ,
  TPRINT   =  1.0033445,  1.0133779,  1.0234113,  1.0334449,  1.0434783,
              1.0535117,  1.0635451,  1.0735786,  1.0836121,  1.0936456,
              1.103679 ,  1.1137123,  1.1237458,  1.1337793,  1.1438128,
              1.1538461,  1.1638796,  1.173913 ,  1.1839465,  1.1939799,
 &END"""

test_namelist_3 = """--------------------------------------------------------------------------------
 Namelist : INNBSK
--------------------------------------------------------------------------------

 &INNBSK
 &END"""

test_namelist_4 = """--------------------------------------------------------------------------------
 Namelist : ADAS
--------------------------------------------------------------------------------

 &ADAS
  FILTER = 'NONE',
  IECPOP = 1,
  IYEAR(1:3) = 96, 89, 42,
  LBLADSS(2:3) = '02_6', '02_6',
  USERID = '/usr/local/depot/sim',
 &END"""


class TestNamelistParsing:
    """Test that we can extract the namelists from the file, together with their contents"""

    def test_can_check_if_namelist_field_is_not_present(self):
        raw_nml = NmlTester()
        nml = Namelist(raw_nml.as_string())

        assert nml.exists('not-a-namelist', 'not-a-field') == False

    @pytest.mark.parametrize('test_namelist, namelist_name, field_name',
                             [(test_namelist_1, 'INNBI', 'NBREF3'),
                              (test_name_list_2, 'NLIST2', 'KWMAIN')],
                             ids = ['1-INNBI-NBREF3', '2-NLIST2-KWMAIN'])
    def test_can_check_if_namelist_field_is_present(self, test_namelist, namelist_name, field_name):
        raw_nml = NmlTester(namelists=[test_namelist])
        nml = Namelist(raw_nml.as_string())

        assert nml.exists(namelist_name, field_name) == True

    def test_raises_if_namelist_does_not_exist(self):
        raw_nml = NmlTester(namelists=[test_namelist_3])
        nml = Namelist(raw_nml.as_string())

        with pytest.raises(NamelistError):
            _ = nml.get_field('not-a-namelist', 'not-a-field')

    def test_raises_if_field_does_not_exist(self):
        raw_nml = NmlTester(namelists=[test_namelist_3])
        nml = Namelist(raw_nml.as_string())

        with pytest.raises(NamelistError):
            _ = nml.get_field('INNBSK', 'not-a-field')

    def test_can_read_namelist_integer_field_value(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        assert nml.get_field('INNBI', 'NBREF3') == 40

    def test_can_read_namelist_float_field_value(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        assert nml.get_field('INNBI', 'BMASS3') == 2.0

    @pytest.mark.parametrize('namelist, field, value',
                             [('INNBI', 'CURTI', [0.1, 0.1]),
                              ('INNBI', 'PFRAC3', [0.5, 0.3, 0.2])],
                             ids=['CURTI', 'PFRAC3'])
    def test_can_read_namelist_array_field_value(self, namelist, field, value):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        assert nml.get_field(namelist, field) == value


class TestNamelistUpdate:
    """Test that we can update the fields in namelists"""

    def test_raises_if_namelist_does_not_exist(self):
        raw_nml = NmlTester(namelists=[test_namelist_3])
        nml = Namelist(raw_nml.as_string())

        with pytest.raises(NamelistError):
            nml.set_field('not-a-namelist', 'NBREF3', 0)

    def test_raises_if_field_does_not_exist(self):
        raw_nml = NmlTester(namelists=[test_namelist_3])
        nml = Namelist(raw_nml.as_string())

        with pytest.raises(NamelistError):
            nml.set_field('INNBSK', 'not-a-field', 0)

    def test_can_update_integer_field(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        field = 'INNBI', 'NBREF3'
        value = nml.get_field(*field)
        nml.set_field(*field, value * 2)

        assert nml.get_field(*field) == (value * 2)

    def test_can_update_float_field(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        field = 'INNBI', 'BMASS3'
        value = nml.get_field(*field)
        nml.set_field(*field, value * 2)

        assert nml.get_field(*field) == (value * 2)

    def test_raises_if_try_to_update_array_without_distribute_flag(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        field = 'INNBI', 'CURTI'
        value = nml.get_field(*field)[0]
        with pytest.raises(NamelistError):
            nml.set_field(*field, value * 2, distribute=False)

    @pytest.mark.parametrize('namelist, field, value',
                             [('INNBI', 'CURTI', [0.2, 0.2]),
                              ('INNBI', 'PFRAC3', [1.0, 0.6, 0.4])],
                             ids=['CURTI', 'PFRAC3'])
    def test_can_update_array_field(self, namelist, field, value):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        nml.set_array(namelist, field, value)

        assert nml.get_field(namelist, field) == value

    def test_raises_if_updated_field_not_an_array(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        with pytest.raises(NamelistError):
            nml.set_array('INNBI', 'BMASS3', [1, 2, 3])

    def test_raises_if_array_has_invalid_values(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        with pytest.raises(NamelistError):
            nml.set_array('INNBI', 'CURTI', ['foo', 'bar'])

    def test_can_update_array_field_distributively(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        field = 'INNBI', 'CURTI'
        value = nml.get_field(*field)[0]
        nml.set_field(*field, value * 2, distribute=True)

        assert all(v == (value * 2) for v in nml.get_field(*field))

    def test_can_use_distribute_flag_with_scalar(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        field = 'INNBI', 'BMASS3'
        value = nml.get_field(*field)
        nml.set_field(*field, value * 2, distribute=True)

        assert nml.get_field(*field) == (value * 2)


class TestNamelistWrite:
    """Test that the written namelist contains the expected data"""

    @staticmethod
    def extract_header_field(s: str, field: str):
        """Extract the value of a header field from a raw file string"""
        for line in s.split('\n'):
            if line.startswith(field):
                return line.split(':', 1)[1].strip()

    @staticmethod
    def extract_namelist_field(s: str, namelist: str, field: str):
        # Pattern extracting the namelist
        nml_pattern = r'&{}\s*(.+?)&END'.format(namelist)
        m = re.search(nml_pattern, s, re.MULTILINE | re.DOTALL)
        if m:
            interior = m.group(1)
            # Pattern extracting the specific field value within the namelist
            field_pattern = r'{}\s*=\s*(.+?)\s*\,'.format(field)
            m = re.search(field_pattern, interior)
            if m:
                return m.group(1)

        return ''

    @pytest.mark.xfail
    def test_unmodified_namelist_has_identical_string(self):
        """Expected to fail because of specifics of how JAMS formats namelists - not expected to be important"""
        raw_nml = NmlTester(namelists=[test_namelist_1, test_name_list_2, test_namelist_3])
        nml = Namelist(raw_nml.as_string())

        assert str(nml) == raw_nml.as_string()

    @pytest.mark.parametrize('prop, value, descr, expected', [('application', 'JETTO-PYTHONTOOLS', 'Application', 'JETTO-PYTHONTOOLS'),
                                                     ('version', 'v3.4.5', 'JAMS Version', 'v3.4.5'),
                                                     ('date', datetime.date(year=2020, month=4, day=13), 'Date', '13/04/2020'),
                                                     ('time', datetime.time(hour=21, minute=22, second=23), 'Time', '21:22:23'),
                                                     ('repo', '/path/to/repo', 'Current GIT repository', '/path/to/repo'),
                                                     ('tag', 'v1.2.3rc1', 'Current GIT release tag', 'v1.2.3rc1'),
                                                     ('branch', 'issue-1', 'Current GIT branch', 'issue-1'),
                                                     ('sha', '23B45FDE21', 'Last commit SHA1-key', '23B45FDE21'),
                                                     ('status', 'medium', 'Repository status', 'medium')],
                             ids = header_descriptions)
    def test_header_value_correct(self, prop, value, descr, expected):
        raw_nml = NmlTester()
        nml = Namelist(raw_nml.as_string())

        setattr(nml, prop, value)
        value = self.extract_header_field(str(nml), descr)

        assert value == expected

    def test_namelist_int_value_correct(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        field = ('INNBI', 'NBREF3')
        nml.set_field(*field, 45)

        assert self.extract_namelist_field(str(nml), *field) == '45'

    def test_namelist_float_value_correct(self):
        raw_nml = NmlTester(namelists=[test_namelist_1])
        nml = Namelist(raw_nml.as_string())

        field = ('INNBI', 'BMASS3')
        nml.set_field(*field, 2.3)

        assert self.extract_namelist_field(str(nml), *field) == '2.3'

    def test_namelist_string_path_correct(self):
        raw_nml = NmlTester(namelists=[test_namelist_3, test_namelist_4])
        nml = Namelist(raw_nml.as_string())

        field = ('ADAS', 'USERID')

        assert self.extract_namelist_field(str(nml), *field) == "'/usr/local/depot/sim'"


class TestNamelistLookup:
    """Test that we can perform lookup of items by field name"""
    @pytest.mark.parametrize('namelist, field', [('INNBI', 'ENERG3'), ('INNBI', 'PFRAC3'), ('NLIST2', 'ISYNTHDIAG')],
                             ids=['ENERG3', 'PFRAC3', 'ISYNTHDIAG'])
    def test_can_lookup_namelist_from_field_name(self, namelist, field):
        raw_nml = NmlTester(namelists=[test_namelist_1, test_name_list_2, test_namelist_3])
        nml = Namelist(raw_nml.as_string())

        assert nml.namelist_lookup(field) == namelist

    def test_nonexistent_field_lookup_returns_none(self):
        raw_nml = NmlTester(namelists=[test_namelist_1, test_name_list_2, test_namelist_3])
        nml = Namelist(raw_nml.as_string())

        assert nml.namelist_lookup('non-existent-field') is None


class TestReadWrite:
    """Test that the read and write functions work as expected"""
    def test_read(self, tmpdir):
        raw_nml = NmlTester(namelists=[test_namelist_1, test_name_list_2, test_namelist_3])
        original_nml = Namelist(raw_nml.as_string())

        f = tmpdir.join('namelist.in')
        f.write(str(original_nml))

        read_nml = read(pathlib.Path(f.strpath))

        assert str(read_nml) == str(original_nml)

    def test_write(self, tmpdir, monkeypatch):
        raw_nml = NmlTester(namelists=[test_namelist_1, test_name_list_2, test_namelist_3])
        original_nml = Namelist(raw_nml.as_string())

        f = tmpdir.join('namelist.in')
        write(original_nml, pathlib.Path(f.strpath))


class TestNamelistComparison:
    @pytest.fixture
    def nml(self):
        raw_nml = NmlTester(namelists=[test_namelist_1, test_name_list_2, test_namelist_3, test_namelist_4])
        return Namelist(raw_nml.as_string())

    def test_equality(self, nml):
        other_nml = Namelist(NmlTester(
            namelists=[test_namelist_1, test_name_list_2, test_namelist_3, test_namelist_4]).as_string())

        assert nml == other_nml

    def test_inequality(self, nml):
        other_nml = Namelist(NmlTester(
            namelists=[test_namelist_1, test_name_list_2, test_namelist_3]).as_string())

        assert nml != other_nml

    @pytest.mark.parametrize('attr, value', [('application', 'EDGE2D'),
                                             ('version', 'vaabbcc'),
                                             ('date', datetime.date(year=1642, month=12, day=25)),
                                             ('time', datetime.time(hour=12, minute=12, second=12)),
                                             ('repo', 'foo/bar'),
                                             ('tag', 'rc1'),
                                             ('branch', 'release'),
                                             ('sha', 'HASH'),
                                             ('status', 'clean')],
                             ids=['application', 'version', 'date', 'time', 'repo', 'tag', 'branch', 'sha', 'status'])
    def test_header_does_not_change_equality(self, nml, attr, value):
        other_nml = Namelist(NmlTester(
            namelists=[test_namelist_1, test_name_list_2, test_namelist_3, test_namelist_4]).as_string())

        setattr(other_nml, attr, value)

        assert nml == other_nml

    def test_change_scalar_changes_equality(self, nml):
        other_nml = Namelist(NmlTester(
            namelists=[test_namelist_1, test_name_list_2, test_namelist_3, test_namelist_4]).as_string())

        existing_value = other_nml.get_field('INNBI', 'BMASS3')
        other_nml.set_field('INNBI', 'BMASS3',  existing_value + 1)

        assert nml != other_nml

    def test_change_array_changes_equality(self, nml):
        other_nml = Namelist(NmlTester(
            namelists=[test_namelist_1, test_name_list_2, test_namelist_3, test_namelist_4]).as_string())

        existing_value = other_nml.get_field('INNBI', 'PFRAC3')
        other_nml.set_array('INNBI', 'PFRAC3',  [v + 1 for v in existing_value])

        assert nml != other_nml
