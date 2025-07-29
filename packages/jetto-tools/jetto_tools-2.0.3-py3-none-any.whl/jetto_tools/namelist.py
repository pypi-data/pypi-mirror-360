"""Module to read, update and write JETTO namelist files."""

import pathlib
import datetime
import re
import copy
from typing import Dict, Union, Tuple, Iterable, List

import f90nml
import jetto_tools._utils


_HEADER_START = """================================================================================
                             CODE INPUT NAMELIST FILE
================================================================================"""

_HEADER_REGEX = r"""
    (?P<name>[\S ]+?)           # Match any number of non-whitespace characters and spaces - record as parameter 'name'
    \s*                         # Match any amount of whitespace
    \:                          # Match the dividing colon
    \s*                         # Match any amount of whitespace
    (?P<value>[\S\s]*?)         # Match any whitespace and non-whitespace characters - record as parameter 'value'
    \s*                         # Match zero or more whitespace
    \n                          # Match newline
"""
_HEADER_PATTERN = re.compile(_HEADER_REGEX, re.VERBOSE)


class NamelistError(Exception):
    """Generic exception used for all errors in the ``Namelist`` module"""
    pass


class Namelist:
    """Class representing a JETTO namelist"""

    _DEFAULT_PROPS = {'application'    : 'JETTO',
                      'version'        : '',
                      'date'           : datetime.date(year=1970, month=1, day=1),
                      'time'           : datetime.time(hour=0, minute=0, second=0),
                      'repo'           : '',
                      'tag'            : '',
                      'branch'         : '',
                      'sha'            : '',
                      'status'         : '',
                      }

    _HEADER_PROPS_MAP = {'Application': 'application',
                         'JAMS Version': 'version',
                         'Date': 'date',
                         'Time': 'time',
                         'Current GIT repository': 'repo',
                         'Current GIT release tag': 'tag',
                         'Current GIT branch': 'branch',
                         'Last commit SHA1-key': 'sha',
                         'Repository status': 'status'}
    _DATE_FORMAT = '%d/%m/%Y'
    _TIME_FORMAT = '%H:%M:%S'
    _HEADER_FORMAT = '{:31}: {}'

    def __init__(self, s: str):
        """Initialise a namelist, based on the contents of a namelist file

        Unpacks the header into individual attributes which can be accessed by name. Parses the namelists in the file,
        and stores them for reading and update.

        :param s: Contents of the namelist file
        :type s: str
        """
        self._header = Namelist._unpack_header(s)

        parser = f90nml.Parser()
        self._namelists = parser.reads(s)

    def __getattr__(self, key):
        """Controls getting of class attributes

        Facilitates treating each header field as an attribute of the class, in a systematic way

        :param key: Attribute name
        :type: str
        :raise: NamelistError if the attribute doesn't exist in the header
        """
        if key in self._header:
            return self._header[key]
        else:
            raise NamelistError('Namelist has no property "{}"'.format(key))

    def __setattr__(self, key: str, value):
        """Controls setting of class attributes

        Facilitates treating each header field as an attribute of the class, in a systematic way

        :param key: Attribute name
        :type: str
        :param value: Attribute value
        :type value: Any
        :raise: NamelistError if the attribute doesn't exist
        """
        if key == '_header':
            self.__dict__['_header'] = value
        elif key == '_namelists':
            self.__dict__['_namelists'] = value
        elif key in self._header:
            self._header[key] = value
        else:
            raise NamelistError('Namelist has no property "{}"'.format(key))

    def __deepcopy__(self, memo):
        """Perform a deep copy of a namelist

        Have to provide this boilerplate implementation because __getattr__ will be called otherwise
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))

        return result

    def __str__(self) -> str:
        """Generate a string representation of the file

        Formats the contents of the header and namelists as a string suitable for writing to a
        namelist (.in) file. Appends a newline to avoid potential Fortran parsing problem.

        :return: Namelist as a string
        :rtype: str
        """
        return '\n'.join([self._pack_header(), self._pack_namelists(), ''])

    def __eq__(self, other):
        """Compare two Namelists for equality"""
        return self._namelists.todict() == other._namelists.todict()

    def __ne__(self, other):
        """Compare two Namelists for inequality"""
        return not self == other
    
    def _pack_header(self):
        """Format the header as a string

        Converts each header field into a string, with appropriate description

        :return: Header as a string
        :rtype: str
        """
        return '\n'.join([_HEADER_START,
                          '',
                          '\n'.join([Namelist._HEADER_FORMAT.format(descr, Namelist._detypify(value))
                                     for descr, value in [('Application', self.application),
                                                          ('JAMS Version', self.version),
                                                          ('Date', self.date),
                                                          ('Time', self.time)]]),
                          '',
                          'JAMS GIT information:-',
                          '',
                          '\n'.join([Namelist._HEADER_FORMAT.format(descr, Namelist._detypify(value))
                                     for descr, value in [('Current GIT repository', self.repo),
                                                          ('Current GIT release tag', self.tag),
                                                          ('Current GIT branch', self.branch),
                                                          ('Last commit SHA1-key', self.sha),
                                                          ('Repository status', self.status)]]),
                          '',
                          ''])

    def _pack_namelists(self):
        """Format the namelists as a string

        Converts the namelists into a string suitable for writing to a namelists file. All namelists and fields are
        written in UPPERCASE, with a trailing comma at the end of each field. To remain reasonably close to the JAMS
        namelist format, the trailing '/' at the end of each namelist is replaced by '&END', and a space is prefixed to
        the ampersands ('&') delimiting the start and end of each namelist.

        The f90nml package has a bug where, if end_comma is set to True, any blank field (ordinarily delimited by a
        single comma) will have an additional comma appended, messing up parsing of the namelist by Fortran. As a
        workaround, this function replaces any double commas separated by blanks with a single comma

        :return: Namelists
        :rype: str
        """
        self._namelists.uppercase = True
        self._namelists.end_comma = True
        self._namelists.indent = 2

        s = str(self._namelists)

        # Replace all double commas with single commas
        double_comma_regex = """
        ,           # First comma
        [ ]+        # Any amount of blank spaces
        ,           # Second comma
        [ ]*        # Any amount of blank spaces
        $           # End of the line
        """
        double_comma_pattern = re.compile(double_comma_regex, re.VERBOSE | re.MULTILINE)
        s = double_comma_pattern.sub(',', s)

        # Replace all instances of a forward slash at the end of a line or the end of the string with '&END'
        s = re.sub('/$', '&END', s, flags=re.MULTILINE)
        # Prefix all ampersands at the start of a line with a space
        s = re.sub(r'^&', r' &', s, flags=re.MULTILINE)

        return s

    @classmethod
    def _unpack_header(cls, s: str) -> Dict[str, Union[str, datetime.date, datetime.time]]:
        """Unpack the header fields from the namelist file contents

        Takes the name, value pairs from the namelist header, and extracts the ones we are expecting. Does type
        conversions for internal storage as necessary. Any expected fields which are not present in the namelist field
        are set to their default values

        :param s: Contents of the namelist file
        :type s: str
        :return: Dictionary of name, value items
        """
        d = copy.deepcopy(cls._DEFAULT_PROPS)

        header_fields = cls._parse_header(s)
        for name, value in header_fields.items():
            if name in cls._HEADER_PROPS_MAP:
                prop = cls._HEADER_PROPS_MAP[name]
                d[prop] = cls._typify(name, value)

        return d

    @classmethod
    def _parse_header(cls, s: str) -> Dict[str, str]:
        """Extract the header fields of a namelist file

        Returns a dictionary of name, value pairs, containing each of the fields in the namelist header, e.g.
            {'Application': 'JETTO', 'Date' : '01/01/2020', 'JAMS GIT Information' : '-', ...}

        :param s: Contents of the namelist file
        :type s: str
        :return: Dictionary of header field name, value pairs
        :rtype: Dict[str, str]
        """
        matches = _HEADER_PATTERN.findall(s)

        # Header pattern also matches the 'Namelist : FOO' lines in the individual namelist headers, so filter them out
        return {name: value for name, value in matches if name != 'Namelist'}

    @classmethod
    def _typify(cls, name: str, value: str) -> Union[str, datetime.date, datetime.time]:
        """Convert the header fields of a namelist file into typed values

        Internally, the header fields are almost all stored as strings, except for the 'Date' and 'Time' fields, which
        are stored as datetime.date and datetime.time objects, respectively. This method checks the name of the field,
        and performs the appropriate conversion.

        :param name: :param value: Field to convert
        :type value: String, datetime.date or datetime.time
        :return: Converted string
        :rtype: str
        :raise: NamelistError if the 'Date' or 'Time' fields cannot be parsed
        """
        if name == 'Date':
            try:
                value = datetime.datetime.strptime(value, cls._DATE_FORMAT).date()
            except ValueError:
                raise NamelistError('Cannot parse {} as a valid date'.format(value))
        elif name == 'Time':
            try:
                value = datetime.datetime.strptime(value, cls._TIME_FORMAT).time()
            except ValueError:
                raise NamelistError('Cannot parse {} as a valid time'.format(value))
        else:
            pass

        return value

    @classmethod
    def _detypify(cls, value: Union[str, datetime.date, datetime.time]) -> str:
        """Convert the header fields into strings

        Internally, the header fields are almost all stored as strings, except for the 'Date' and 'Timne' fields, which
        are stored as datetime.date and datetime.time objects, respectively. This method checks the type of the field,
        and performs the appropriate conversion.

        :param value: Field to convert
        :type value: String, datetime.date or datetime.time
        :return: Converted string
        :rtype: str
        """
        if isinstance(value, datetime.date):
            return value.strftime(cls._DATE_FORMAT)
        elif isinstance(value, datetime.time):
            return value.strftime(cls._TIME_FORMAT)
        else:
            return value

    def exists(self, namelist: str, field: str) -> bool:
        """Check if a namelist field exists

        :param namelist: Identifier of the namelist
        :type namelist: str
        :param field: Identifier of the field within the namelist
        :type field: str
        :return: True if the field exists, otherwise False
        :raise: Namelist error if the namelist or the field does not exist        """
        try:
            _ = self._namelists[namelist][field]
        except KeyError:
            return False

        return True

    def get_field(self, namelist: str, field: str) -> Union[int, float]:
        """Get the value of a namelist field

        See get_array if you are expecting an array.

        :param namelist: Identifier of the namelist
        :type namelist: str
        :param field: Identifier of the field within the namelist
        :type field: str
        :raise: Namelist error if the namelist or the field does not exist
        """
        if self.exists(namelist, field):
            # TODO: should this fail if it's being asked to return an
            # array? this feels like the right thing to do, but it
            # might break too much of the API
            return self._namelists[namelist][field]
        else:
            raise NamelistError('Namelist, field pair "{}, {}" not found in namelist file'.format(namelist, field))

    def get_array(self, namelist: str, field: str) -> Union[List[int], List[float]]:
        """Get the value of a vector namelist field

        See get_field if you are expecting a scalar value.

        :param namelist: Identifier of the namelist
        :type namelist: str
        :param field: Identifier of the field within the namelist
        :type field: str
        :raise: Namelist error if the namelist or the field does not exist
        """
        if self.exists(namelist, field):
            value = self._namelists[namelist][field]
            if not isinstance(value, list):
                value = [value]
            return value
        else:
            raise NamelistError('Namelist, field pair "{}, {}" not found in namelist file'.format(namelist, field))

    def set_field(self, namelist: str, field: str, value: Union[int, float], distribute=False):
        """Set the value of a namelist field

        Raises an error if the parameter being updated is not a scalar, unless the *distribute* flag is set to *True*.
        If *distribute* is True, arrays are updated identically for each array element. This is intended to handle
        cases such as CURTI and BTIN, where scalar values in the JSET are used to identically update each element of
        an array in the namelist file.

        :param namelist: Identifier of the namelist
        :type namelist: str
        :param field: Identifier of the field within the namelist
        :type field: str
        :param distribute: If True, update each element of the array
        :type distribute: bool
        :raise: Namelist error if the namelist or the field does not exist
        """
        if not self.exists(namelist, field):
            raise NamelistError(f'Namelist, field pair "{namelist}, {field}" not found in namelist file')

        if type(value) == str:
            self._namelists[namelist][field] = value
            return

        try:
            _ = iter(self._namelists[namelist][field])
        except TypeError:
            self._namelists[namelist][field] = value
        else:
            if not distribute:
                raise NamelistError(f'Namelist, field pair "{namelist}, {field}" is of array type - cannot update')

            for i in range(len(self._namelists[namelist][field])):
                self._namelists[namelist][field][i] = value

    def set_array(self, namelist: str, field: str, value: List[Union[int, float]]):
        """Set the contents of a namelist array

        Replaces the existing array with the contents of *value*. Assumes that the replacement array is a list of
        numeric values.

        :param namelist: Identifier of the namelist
        :type namelist: str
        :param field: Identifier of the field within the namelist
        :type field: str
        :param value: New array contents
        :type value: List of numeric values
        :raise: Namelist error if the namelist or the field does not exist, if the existing value is not already an
                array, or if the new value is not of the expected type
        """
        if not isinstance(self._namelists[namelist][field], list):
            raise NamelistError(f'Namelist parameter {namelist}/{field} is not of array type')

        if not all(jetto_tools._utils.is_numeric(v) for v in value):
            raise NamelistError(f'Array {value} has non-numeric elements')

        self._namelists[namelist][field] = value

    def namelist_lookup(self, field: str) -> Union[str, None]:
        """Search for the namelist containing a field

        Searches through each namelist in the namelists file, looking for the namelist containing the specified field.
        Assumes that there is at most one namelist in the file which has the given field.

        :param field: Field name
        :type field: str
        :return: Namelist name (in uppercase), or None if the field cannot be found
        :rtype: str or None
        """
        for name, namelist in self._namelists.items():
            if field in namelist:
                return name.upper()

        return None


def read(path: pathlib.Path):
    """Read a namelist file

    Reads the contents of the provided file, and constructs a ``Namelist`` object from them

    :Example:

    >>> from jetto_tools.namelist import read
    >>> from pathlib import Path
    >>> nml = read(Path('/path/to/jetto.in'))

    :param path: Path to the JSET file to read
    :type path: pathlib.Path
    :return: Namelist object
    :rtype: Namelist
    """
    with open(path, 'r', encoding='utf-8') as f:
        return Namelist(f.read())


def write(nml: Namelist, path: pathlib.Path):
    """Write a namelist file

    Sets the header of the namelist, and writes the namelist out to the specified path.

    - The 'Date' field is set to the current date
    - The 'Time' field is set to the current time

    :param nml: Namelist object to write out
    :type nml: Namelist
    :param path: Path to write the namelist to
    :type path: pathlib.Path
    """
    now = datetime.datetime.now()
    nml.date = now.date()
    nml.time = now.time()
    with open(path, 'w') as f:
        f.write(str(nml))
