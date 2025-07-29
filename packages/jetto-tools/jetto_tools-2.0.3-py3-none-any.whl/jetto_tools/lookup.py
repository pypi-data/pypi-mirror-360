"""Module to read, validate and write JETTO lookup maps"""

import json
from typing import Dict
import pathlib

import cerberus

_VALIDATION_SCHEMA = {
    'jset_flex_id': {
        'type': 'list',
        'empty' : False,
        'schema' : {
            'type' : 'string'
        }
    },
    'jset_id': {
        'type': 'string',
        'required': True,
        'nullable': True,
        'empty': False
    },
    'nml_id': {
        'type': 'dict',
        'schema': {
            'namelist': {
                'required': True,
                'type': 'string',
                'empty': False
            },
            'field': {
                'required': True,
                'type': 'string',
                'empty': False
            }
        }
    },
    'type': {
        'required': True,
        'type': 'string',
        'allowed': ['str', 'int', 'real']
    },
    'dimension': {
        'required': True,
        'type': 'string',
        'empty': False,
        'allowed': ['scalar', 'vector']
    }
}
_VALIDATOR = cerberus.Validator(_VALIDATION_SCHEMA)


class ParseError(Exception):
    """Generic exception used for parsing errors in the ``lookup`` module"""
    pass


class ValidationError(Exception):
    """Generic exception used for validation errors in the ``lookup`` module"""
    pass


def from_file(path: pathlib.Path) -> Dict:
    """Read JETTO lookup map from a file

    Reads the contents of the file, and then calls ``from_json`` to convert the contents to a lookup map

    :param path: Path to the lookup file
    :type path: pathlib.Path
    :return: Validated lookup map
    :rtype: dict
    :raise: ParseError if the JSON parsing fails; ValidationError if the map validation fails
    """
    with open(path, 'r', encoding='utf-8') as f:
        d = from_json(f.read())

    return d


def from_json(s: str) -> Dict:
    """Read JETTO lookup map from JSON string

    First converts the JSON string into a lookup map, and then validates it against the map schema

    :param s: JSON string containing the map
    :type s: str
    :return: Lookup map
    :rtype: dict
    :raise: ParseError if the JSON parsing fails; ValidationError if the map validation fails
    """
    try:
        d = json.loads(s)
    except json.decoder.JSONDecodeError as err:
        raise ParseError('Failed to parse lookup JSON "{}"'.format(err.msg))

    validate(d)

    return d


def to_file(d: Dict, path: pathlib.Path):
    """Write JETTO lookup map to a file

    Calls ``to_json`` to convert the map to a JSON string, and then writes it to the file

    :param d: Lookup map
    :type d: dict
    :param path: Destination path
    :type path: pathlib.Path
    """
    s = to_json(d)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)


def to_json(d: Dict) -> str:
    """Write JETTO lookup map to JSON string

    First validates the lookup map, and then converts it into a JSON string

    :param d: Lookup map
    :type d: dict
    :return: JSON string
    :rtype: str
    :raise: ValidationError if the map validation fails
    """
    validate(d)

    return json.dumps(d, indent=4)


def validate(d: Dict):
    """Validate a JETTO lookup map

    Performs validation against the standard schema provided by the ``lookup`` module.

    :param d: Lookup map
    :type d: dict
    :raise: ValidationError if the validation fails
    """
    for param in d:
        if not _VALIDATOR.validate(d[param]):
            raise ValidationError('Validation of lookup parameter {} failed'
                                  ' (Cerberus feedback : "{}")'.format(param, _VALIDATOR.errors))
