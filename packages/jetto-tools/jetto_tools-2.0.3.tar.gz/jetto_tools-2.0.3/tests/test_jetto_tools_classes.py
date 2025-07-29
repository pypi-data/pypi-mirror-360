import pytest
import copy

from IPython import embed  # noqa: F401 For debugging

from jetto_tools.classes import *  # noqa: F403 Import everything as a test


@pytest.fixture
def init_dict():
    return {
        'kip': 'tok-tok',
        'paard': 'hihihihi',
    }


@pytest.fixture
def nested_dict():
    return {
        'kip': 'tok-tok',
        'paard': 'hihihihi',
        'translations': {
            'kip': 'chicken',
            'paard': 'horse',
        }
    }


def test_OrdinaryOrderedDictionaryStructure_dict_init(init_dict):
    oods = OrdinaryOrderedDictionaryStructure(init_dict)
    assert oods['kip'] == 'tok-tok'
    assert oods['paard'] == 'hihihihi'


def test_OODS_dict_init(init_dict):
    oods = OODS(init_dict)
    assert oods['kip'] == 'tok-tok'
    assert oods['paard'] == 'hihihihi'


def test_OODS_empty_init():
    oods = OODS()
    assert len(oods) == 0


def test_OODS_shallow_copy(nested_dict):
    oods = OODS(nested_dict)
    oods_copy = copy.copy(oods)
    # Check equality (==) recursively
    assert oods['kip'] == oods_copy['kip']
    assert oods['paard'] == oods_copy['paard']
    assert oods['translations'] == oods_copy['translations']
    # Now change a field, as it is shallow, the copy should change with it
    oods['translations']['kip'] = 'hen'
    assert oods_copy['translations']['kip'] == 'hen'

    # Or more directly
    assert id(oods['translations']) == id(oods_copy['translations'])
    assert id(oods) != id(oods_copy)


def test_OODS_deep_copy(nested_dict):
    oods = OODS(nested_dict)
    oods_copy = copy.deepcopy(oods)
    # Check equality (==) recursively
    assert oods['kip'] == oods_copy['kip']
    assert oods['paard'] == oods_copy['paard']
    assert oods['translations'] == oods_copy['translations']
    # Now change a field, as it is deep, the copy should _not_ change with it
    oods['translations']['kip'] = 'hen'
    assert oods_copy['translations']['kip'] == 'chicken'

    # Or more directly
    assert id(oods['translations']) != id(oods_copy['translations'])
    assert id(oods) != id(oods_copy)
