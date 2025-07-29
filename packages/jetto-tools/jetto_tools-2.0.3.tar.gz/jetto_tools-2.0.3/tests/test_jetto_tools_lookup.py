import pytest
import jetto_tools.lookup as lookup
import json
import pathlib


@pytest.fixture(scope='function')
def lookup_dict():
    return {
        "param1": {
            "jset_id": "panel1.name",
            "nml_id": {
                "namelist": "NLIST1",
                "field": "FIELD1"
            },
            "type": "int",
            'dimension': 'scalar'
        },
        "param2": {
            "jset_id": "panel2.name",
            "nml_id": {
                "namelist": "NLIST2",
                "field": "FIELD2"
            },
            "type": "real",
            'dimension': 'scalar'
        },
        "param3": {
            "jset_id": None,
            "nml_id": {
                "namelist": "NLIST3",
                "field": "FIELD3"
            },
            "type": "real",
            'dimension': 'scalar'
        },
        "param4": {
            "jset_id": "panel1.name4",
            "jset_flex_id": [
                "extrapanel.name4",
                "extrapanel2.name4" ],
            "nml_id": {
                "namelist": "NLIST4",
                "field": "FIELD4"
            },
            "type": "real",
            'dimension': 'scalar'
        }
    }


@pytest.fixture(scope='function')
def lookup_json(lookup_dict):
    return json.dumps(lookup_dict, indent=4)


def test_conversion_from_json_returns_dict(lookup_json):
    d = lookup.from_json(lookup_json)

    assert isinstance(d, dict)


def test_conversion_from_json_triggers_validation(mocker, lookup_json, lookup_dict):
    spy = mocker.spy(lookup, 'validate')

    _ = lookup.from_json(lookup_json)

    spy.assert_called_once_with(lookup_dict)


def test_raises_if_json_string_is_empty():
    with pytest.raises(lookup.ParseError):
        _ = lookup.from_json('')


def test_does_not_raise_if_json_dict_is_empty():
    _ = lookup.from_json('{}')


def test_raises_if_json_string_cannot_be_decoded():
    with pytest.raises(lookup.ParseError):
        _ = lookup.from_json('foo')


def test_conversion_matches_input_dict(lookup_dict, lookup_json):
    d = lookup.from_json(lookup_json)

    assert d == lookup_dict


def test_validation_fails_if_parameter_is_empty_dict(lookup_dict):
    lookup_dict['param1'] = {}

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


expected_fields = ('jset_id', 'type', 'dimension') # , 'nml_id' is optional


@pytest.mark.parametrize('expected', expected_fields)
def test_validation_fails_if_expected_field_is_missing(lookup_dict, expected):
    del lookup_dict['param1'][expected]

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


nonempty_fields = ('jset_id', 'nml_id', 'type', 'dimension')


@pytest.mark.parametrize('expected', nonempty_fields)
def test_validation_fails_if_expected_field_is_empty(lookup_dict, expected):
    lookup_dict['param1'][expected] = ''

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


@pytest.mark.parametrize('expected', expected_fields)
def test_validation_fails_if_field_has_wrong_type(lookup_dict, expected):
    lookup_dict['param1'][expected] = 0

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


expected_nml_fields = ('namelist', 'field')


@pytest.mark.parametrize('expected', expected_nml_fields)
def test_validation_fails_if_nml_field_is_missing(lookup_dict, expected):
    del lookup_dict['param1']['nml_id'][expected]

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


@pytest.mark.parametrize('expected', expected_nml_fields)
def test_validation_fails_if_nml_field_has_wrong_type(lookup_dict, expected):
    lookup_dict['param1']['nml_id'][expected] = None

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


def test_validation_passes_if_type_field_is_int(lookup_dict):
    lookup_dict['param1']['type'] = 'int'

    _ = lookup.validate(lookup_dict)


def test_validation_passes_if_type_field_is_real(lookup_dict):
    lookup_dict['param1']['type'] = 'real'

    _ = lookup.validate(lookup_dict)


def test_validation_fails_if_type_field_is_unrecognised(lookup_dict):
    lookup_dict['param1']['type'] = 'foo'

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


def test_validation_passes_if_dimension_field_is_scalar(lookup_dict):
    lookup_dict['param1']['dimension'] = 'scalar'

    _ = lookup.validate(lookup_dict)


def test_validation_passes_if_dimension_field_is_vector(lookup_dict):
    lookup_dict['param1']['dimension'] = 'vector'

    _ = lookup.validate(lookup_dict)


def test_validation_fails_if_dimension_field_is_unrecognised(lookup_dict):
    lookup_dict['param1']['dimension'] = 'foo'

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


def test_validation_passes_if_jset_if_is_none(lookup_dict):
    lookup_dict['param1']['jset_id'] = None

    _ = lookup.validate(lookup_dict)


def test_validation_fails_if_top_level_field_is_unrecognised(lookup_dict):
    lookup_dict['param1']['foo'] = ''

    with pytest.raises(lookup.ValidationError):
        _ = lookup.validate(lookup_dict)


def test_conversion_to_json_triggers_validation(mocker, lookup_dict):
    spy = mocker.spy(lookup, 'validate')

    _ = lookup.to_json(lookup_dict)

    spy.assert_called_once_with(lookup_dict)


def test_conversion_to_json_returns_original_string_if_unchanged(lookup_dict, lookup_json):
    s = lookup.to_json(lookup_dict)

    assert s == lookup_json


def test_read_from_file_triggers_json_conversion(lookup_json, tmpdir, mocker):
    lookup_file = tmpdir.join('lookup.json')
    lookup_file.write(lookup_json)

    spy = mocker.spy(lookup, 'from_json')

    _ = lookup.from_file(pathlib.Path(lookup_file.strpath))

    spy.assert_called_once_with(lookup_json)


def test_read_from_file_returns_expected_dict(lookup_json, lookup_dict, tmpdir):
    lookup_file = tmpdir.join('lookup.json')
    lookup_file.write(lookup_json)

    d = lookup.from_file(pathlib.Path(lookup_file.strpath))

    assert d == lookup_dict


def test_write_to_file_triggers_json_conversion(lookup_dict, tmpdir, mocker):
    lookup_file = tmpdir.join('lookup.json')
    spy = mocker.spy(lookup, 'to_json')

    lookup.to_file(lookup_dict, pathlib.Path(lookup_file.strpath))

    spy.assert_called_once_with(lookup_dict)


def test_writes_expected_json_to_file(lookup_dict, lookup_json, tmpdir):
    lookup_file = tmpdir.join('lookup.json')

    lookup.to_file(lookup_dict, pathlib.Path(lookup_file.strpath))

    with open(lookup_file) as f:
        assert f.read() == lookup_json


def test_write(lookup_json):
    with open('jetto.json', 'w', encoding='utf-8') as f:
        f.write(lookup_json)
