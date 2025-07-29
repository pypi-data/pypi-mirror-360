import scipy.io as spio

import jetto_tools

# Headers that matlab uses for metadata
mat_headers = ['__header__', '__version__', '__globals__']


def loadmat(filename):
    """ Load a .mat file from disk

    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects

    Args:
      - filename: Filename passed to `spio.loadmat`
    Returns:
      - converted_data: OODS with all leafs as MATLAB objects
    """
    data = spio.loadmat(str(filename), struct_as_record=False, squeeze_me=True)
    raw_matlab = _convert_keys_in_place(data)
    return jetto_tools.classes.OODS(raw_matlab)


def _convert_keys_in_place(dictobj):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dictobj:
        if isinstance(dictobj[key], spio.matlab.mio5_params.mat_struct):
            dictobj[key] = _todict(dictobj[key])
    return dictobj


def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dictobj = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dictobj[strg] = _todict(elem)
        else:
            dictobj[strg] = elem
    return dictobj
