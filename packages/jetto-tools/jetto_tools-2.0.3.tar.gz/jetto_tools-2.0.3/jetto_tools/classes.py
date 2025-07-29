import os
import warnings
from collections import OrderedDict
from pathlib import Path
import logging
import copy
from itertools import chain, zip_longest

import numpy as np
import pandas as pd
import xarray as xr

from jetto_tools.binary import read_binary_file
from jetto_tools.nested_dicts import _gen_dict_extract

from IPython import embed

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
def jhp_to_xarray(parsed):
    """ See `jsp_to_xarray` """
    return jetto_to_xarray(parsed, ['TIME', 'XVEC1'])

def jht_to_xarray(parsed):
    """ See `jsp_to_xarray` """
    return jetto_to_xarray(parsed, ['TVEC1', 'TVEC2'])

def ssp_to_xarray(parsed):
    """ See `jsp_to_xarray` """
    return jetto_to_xarray(parsed, ['TIME', 'XVEC1'])

def sst_to_xarray(parsed):
    """ See `jsp_to_xarray` """
    return jetto_to_xarray(parsed, ['TVEC1'])

def jasp_to_xarray(parsed):
    """ See `jsp_to_xarray` """
    return jetto_to_xarray(parsed, ['TIME', 'XVEC1'])

def jast_to_xarray(parsed):
    """ See `jsp_to_xarray` """
    return jetto_to_xarray(parsed, ['TVEC1'])

def jsd_to_xarray(parsed):
    """ See `jsp_to_xarray` """
    return jetto_to_xarray(parsed, ['TVEC1'])

def jst_to_pandas(jst):
    time = jst.pop('TVEC1')
    meta = strip_meta(jst)
    time = pd.Index(np.squeeze(time[:,0]), name="time")
    time_ax = 1
    space_ax = 0
    time1 = {}

    for name in list(jst.keys()):
        if jst[name].shape[time_ax] == len(time):
            if jst[name].shape[space_ax] == 1:
                df = pd.Series(np.squeeze(jst.pop(name)), index=time)
                time1[name] = df
    #time1 = pd.concat(time1)
    if len(jst) != 0:
        warnings.warn('Could not read full JST, {!s} are left behind!'.format(
            jst.keys()))
    time1 = pd.concat(time1).unstack(0)
    return time1, meta

def jst_to_xarray(jst):
    meta = strip_meta(jst)
    if 'TIME' in jst:
        jst['TVEC1'] = jst.pop('TIME')
        jst['INFO']['TVEC1'] = jst['INFO'].pop('TIME')
    time = handle_variable_meta(jst, 'TVEC1')
    data = {}

    for name in list(jst.keys()):
        if name != 'INFO':
            data[name] = handle_variable_meta(jst, name)

    meta['INFO'] = jst.pop('INFO')
    if len(jst) != 0:
        warnings.warn('Could not read full JST, {!s} are left behind!'.format(
            jst.keys()))
    ds = xr.Dataset(data, coords={'time': time})
    ds.attrs = meta
    return ds

def strip_meta(vardict):
    meta = {}
    meta["SHOT"] = int(vardict.pop("SHOT")[0][0])
    for name in ["SECTIONS", "CREATION_DATE", "CREATION_TIME", "FILE FORMAT",
                 "FILE DESCRIPTION", "VERSION", "DDA NAME"]:
        meta[name] = vardict.pop(name)
    return meta

def handle_variable_meta(jetto_part_dict, name):
    info_dict = jetto_part_dict['INFO']

    data = np.squeeze(jetto_part_dict.pop(name))

    # Save interesting metadata as variable attribute
    var_attrs = {
        'units': info_dict[name].pop('UNITS'),
        'label': info_dict[name].pop('LABEL'),
        'description': info_dict[name].pop('DESC'),
    }

    # If it has an XBASE, it depends on one of our global axes
    # Usually (time, xvec1, xvec2)
    if 'XBASE' in info_dict[name]:
        if data.ndim == 2:
            xbase = info_dict[name].pop('XBASE')
            dims = ('time', jetto_to_xarray_dimension[xbase])
        else:
            dims = (jetto_to_xarray_dimension[info_dict[name].pop('XBASE')], )
    else:
        # It IS one of our axes
        dims = (jetto_to_xarray_dimension[name], )
    data = np.atleast_1d(data)

    # Delete uninteresting attributes
    for key in ['FORM', 'SECNUM', 'SCSTR']:
        if key in info_dict[name]:
            del info_dict[name][key]

    # Remove from global dict if info is empty
    if len(info_dict[name]) == 0:
        del info_dict[name]

    var = xr.Variable(dims, data, attrs=var_attrs)
    return var

jetto_to_xarray_dimension = {
    'XVEC1': 'xvec1',
    'XVEC2': 'xvec2',
    'TVEC1': 'time',
    'TVEC2': 'time2',
    'TIME': 'time',
}

def jetto_to_xarray(parsed, dims):
    meta = strip_meta(parsed)
    coords = OrderedDict()
    for dim in dims:
        coords[jetto_to_xarray_dimension[dim]] = \
            handle_variable_meta(parsed, dim)

    data = {}
    for name in list(parsed.keys()):
        if name != 'INFO':
            data[name] = handle_variable_meta(parsed, name)

    meta['INFO'] = parsed.pop('INFO')
    if len(parsed) != 0:
        warnings.warn('Could not read full file, {!s} are left behind!'.format(
            parsed.keys()))

    try:
        ds = xr.Dataset(data, coords=coords)
    except ValueError:
        # Something weird, usually in data. Try heuristic fixes
        # Maybe the timebase got borked
        warnings.warn('File seems broken, trying to save it')
        if 'time' in coords:
            for varname in list(data.keys()):
                var = data[varname]
                if var.sizes['time'] != len(coords['time']):
                    warnings.warn('Appending empty timeslice to {!s}'.format(
                        varname))
                    time_idx = var.dims.index('time')
                    no_timeshape = [x if i != time_idx else 1 for i, x in
                                    enumerate(var.shape)]
                    fill_var = xr.Variable(var.dims,
                                           np.full(no_timeshape, np.NaN))
                    new_var = xr.Variable.concat([var, fill_var], 'time')
                    new_var.attrs = var.attrs
                    data[varname] = new_var
        ds = xr.Dataset(data, coords=coords)

    ds.attrs = meta
    return ds

def jsp_to_xarray(parsed):
    """ Convert a JSP dictionary to pandas

    Assumes the JSP is in dictionary format, for example as loaded with
    `jetto_tools.binary.read_binary_file`. It merges the two radial profiles
    with bases XVEC1 and XVEC2 together for each timepoint in the JSP, on
    base TIME.

    Args:
        parsed:         A JSP binary in dict form

    Returns:
        ds:          An `xr.Dataset` with two spatial bases and one timebase
    """
    return jetto_to_xarray(parsed, ['TIME', 'XVEC1', 'XVEC2'])

def jsp_to_pandas(jsp):
    time = jsp.pop("TIME")
    xvec1 = np.squeeze(jsp.pop("XVEC1"))
    xvec2 = np.squeeze(jsp.pop("XVEC2"))
    time_ax = 0
    space_ax = 1
    jsp_meta = strip_meta(jsp)

    spacetime1 = {}
    spacetime2 = {}
    time = pd.Index(np.squeeze(time[:,0]), name="time")
    space1 = pd.Index(xvec1, name="space")
    space2 = pd.Index(xvec2, name="space")
    for name in list(jsp.keys()):
        if jsp[name].shape[time_ax] == len(time):
            if jsp[name].shape[space_ax] == len(xvec1):
                df = pd.DataFrame(jsp.pop(name), index=time, columns=space1)
                df = df.stack()
                spacetime1[name] = df
            elif jsp[name].shape[space_ax] == len(xvec2):
                df = pd.DataFrame(jsp.pop(name), index=time, columns=space2)
                df = df.stack()
                spacetime2[name] = df

    spacetime1 = pd.concat(spacetime1).unstack(0)
    spacetime2 = pd.concat(spacetime2).unstack(0)
    if len(jsp) != 0:
        warnings.warn('Could not read full JSP, {!s} are left behind!'.format(
            jsp.keys()))

    return spacetime1, spacetime2, jsp_meta

def merge_jsp_jst_meta(meta, meta_jst):
    del meta['SECTIONS']
    del meta['DDA NAME']
    for key in ['SHOT', 'CREATION_DATE', 'CREATION_TIME', 'FILE FORMAT',
                'FILE DESCRIPTION', 'VERSION']:
        if meta_jst[key] != meta[key]:
            warnings.warn('Key {!s} of JST and JSP metadata does not match!'.format(key))
    del meta['INFO']['SECTIONS']
    del meta['INFO']['DDA NAME']
    for key in list(meta_jst['INFO'].keys()):
        if key not in ['SHOT', 'FILE FORMAT', 'FILE DESCRIPTION', 'VERSION',
                       'CREATION_DATE', 'CREATION_TIME', 'INFO', 'SECTIONS']:
            if key not in meta['INFO']:
                meta['INFO'][key] = meta_jst['INFO'].pop(key)
            else:
                if meta['INFO'][key] != meta_jst['INFO'][key]:
                    print('Warning! Found {!s} both in JST and JSP info, and they are different.'.format(key))
                else:
                    meta_jst['INFO'].pop(key)
        else:
            print('skipping {!s}'.format(key))

def merge(a, b, path=None):
    """merges dictionary b into a

    From https://stackoverflow.com/a/7205107/3613853
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def clean_meta(meta_dict):
    for key in ['SECTIONS', 'CREATION_DATE', 'CREATION_TIME', 'FILE FORMAT',
                'FILE DESCRIPTION', 'VERSION', 'DDA NAME']:
        if key in meta_dict:
            del meta_dict[key]

def rename_duplicates(ds_jsp, jst):
    for var in ds_jsp.data_vars:
        if var in jst:
            jst[var + '0D'] = jst.pop(var)
            jst['INFO'][var + '0D'] = jst['INFO'].pop(var)


# Even though dicts are sorted in recent Python,
# Use SortedDicts for backwards compat
class OrdinaryOrderedDictionaryStructure(OrderedDict):
    """Structure to save searchable OrderedDicts

    Attributes:
        _dict_like_convert_classes: A list of dict-like classes we can convert
        _list_like_convert_classes: A list of list-like classes we can convert
    """
    _dict_like_convert_classes = (dict, OrderedDict)
    _list_like_convert_classes = (list, )
    """ Defines a wrapper for regular Python dicts """
    def __init__(self, init_structure=None):
        """ Inits OrdinaryOrderedDictionaryStructure with an existing structure

        Args:
            init_structure: The dictionary to initialize with. Can be
                list-like or dict-like.
        """
        super().__init__()
        if init_structure is None:
            init_structure = {}
        # This is a very protective way of initialization, so only allow
        # specific classes
        if isinstance(init_structure, self._dict_like_convert_classes):
            for key in init_structure.keys():
                self[key] = init_structure[key]
        elif isinstance(init_structure, self._list_like_convert_classes):
            for el in init_structure:
                if len(el) != 2:
                    raise ValueError('When passing a list-like, make sure all elements are iteratables of ("key_name", value)')
                self[el[0]] = el[1]
        else:
            raise TypeError('You deal with it! (pass an allowed class)')

    def recursive_find(self, keyname, verbosity=0):
        """ Find a key recursively in OODS structure

        """
        return _gen_dict_extract(self, keyname, verbosity=verbosity)

    def values_middle_first(self, remove_none=True):
        """ Like .values() but with middle values first
        """
        for value in self.values():
            if len(value) > 2:
                # Value is something list-like
                mid_index = int(len(value) / 2)
                # For a 10-length list, this is splitting in 5 and 5
                # value[mid_index::]
                # value[mid_index-1::-1]
                iteratable = chain.from_iterable(
                    zip_longest(value[mid_index::],
                                value[mid_index - 1::-1]))
                sort = list(iteratable)
                # Contains None if value was of uneven length
                # The last value should be the _first_ value in the 
                # generated iteratable
                if sort[-1] != value[0]:
                    del sort[-1]
                # Sanity checks
                if len(sort) != len(value):
                    raise Exception("Tried to sort, but sorted return value has different length")
                if set(sort) != set(value):
                    raise Exception("Tried to sort, but sorted return value has different values")
                yield sort
            else:
                yield value

    def __deepcopy__(self, memo):
        return OrdinaryOrderedDictionaryStructure(copy.deepcopy(OrderedDict(self)))


OODS = OrdinaryOrderedDictionaryStructure  # Define a useful short name

class JETTO(OrderedDict):
    def __init__(self, runfolder, on_read_error='raise', load_sanco=True,
                 load_pion=True, load_ascot=True, load_mishka=True, **kw):
        OrderedDict.__init__(self, **kw)

        runfolder = Path(runfolder)
        # allow initializing this class from a jsp filename
        if runfolder is not None:
            self.run_path = str(runfolder.absolute())
            self.load_jetto(on_read_error=on_read_error)

            if load_pion:
                self.load_pion(on_read_error=on_read_error)

            if load_sanco:
                self.load_sanco(on_read_error=on_read_error)

            if load_ascot:
                self.load_ascot(on_read_error=on_read_error)

            if load_mishka:
                self.load_mishka(on_read_error=on_read_error)

    def print_dims(self):
        for field, ds in self.items():
            print('{:4s}: {!s}'.format(field, dict(ds.dims)))

    def load_jetto(self, on_read_error='raise'):
        runfolder = self.run_path
        jsp_path = os.path.join(runfolder, 'jetto.jsp')
        jsp = read_binary_file(jsp_path)

        self['JSP'] = try_convert_xarray(jsp, jsp_path, jsp_to_xarray, on_read_error=on_read_error)

        jst_path = os.path.join(runfolder, 'jetto.jst')
        jst = read_binary_file(jst_path)

        self['JST'] = try_convert_xarray(jst, jst_path, jst_to_xarray, on_read_error=on_read_error)

    def load_pion(self, on_read_error='raise'):
        runfolder = self.run_path
        jhp_path = os.path.join(runfolder, 'jetto.jhp')
        if os.path.isfile(jhp_path):
            jhp = read_binary_file(jhp_path)
            self['JHP'] = try_convert_xarray(jhp, jhp_path, jhp_to_xarray, on_read_error=on_read_error)

        jht_path = os.path.join(runfolder, 'jetto.jht')
        if os.path.isfile(jht_path):
            jht = read_binary_file(jht_path)
            self['JHT'] = try_convert_xarray(jht, jht_path, jht_to_xarray, on_read_error=on_read_error)

    def load_ascot(self, on_read_error='raise'):
        runfolder = self.run_path
        ppath = os.path.join(runfolder, 'jetto.jasp')
        if os.path.isfile(ppath):
            pparsed = read_binary_file(ppath)
            self['JASP'] = try_convert_xarray(pparsed, ppath, jasp_to_xarray, on_read_error=on_read_error)

        tpath = os.path.join(runfolder, 'jetto.jast')
        if os.path.isfile(tpath):
            tparsed = read_binary_file(tpath)
            self['JAST'] = try_convert_xarray(tparsed, tpath, jast_to_xarray, on_read_error=on_read_error)

    def load_mishka(self, on_read_error='raise'):
        runfolder = self.run_path
        #ppath = os.path.join(runfolder, 'jetto.msm')
        #if os.path.isfile(ppath):
        #    pparsed = read_binary_file(ppath)
        #    self['MSM'] = try_convert_xarray(pparsed, ppath, msm_to_xarray, on_read_error=on_read_error)

        tpath = os.path.join(runfolder, 'jetto.jsd')
        if os.path.isfile(tpath):
            tparsed = read_binary_file(tpath)
            self['JSD'] = try_convert_xarray(tparsed, tpath, jsd_to_xarray, on_read_error=on_read_error)

    def load_sanco(self, on_read_error='raise'):
        runfolder = self.run_path
        ssp_path = os.path.join(runfolder, 'jetto.ssp')
        if os.path.isfile(ssp_path):
            ssp = read_binary_file(ssp_path)
            self['SSP'] = try_convert_xarray(ssp, ssp_path, ssp_to_xarray, on_read_error=on_read_error)

        # SSPs are special. All SSPs have the same time/spatial base, so merge them together
        # Do not merge them for now. Too slow! Mechanism kept commented out
        ssp_part_paths = [os.path.join(runfolder, file) for file in os.listdir(runfolder) if
                            file[:-1].endswith('ssp')]
        #sub_dss = []
        #all_vars = set()
        for ssp_path in sorted(ssp_part_paths):
            ssp = read_binary_file(ssp_path)
            n_ssp = int(ssp_path[-1])
            ds = try_convert_xarray(ssp, ssp_path, ssp_to_xarray, on_read_error=on_read_error)
            #ds = ds.expand_dims({'nion': n_ssp})
            #all_vars = all_vars.union(ds.data_vars)
            #sub_dss.append(ds)
            self['SSP' + str(n_ssp)] = ds
        #n_time = len(ds['time'])
        #n_xvec1 = len(ds['xvec1'])
        #for ii, ds in enumerate(sub_dss):
        #    for var in all_vars:
        #        if var not in ds.data_vars:
        #            ds[var] = xr.Variable(('nion', 'time', 'xvec1'), np.full((1, n_time, n_xvec1), np.nan))
        #    sub_dss[ii] = ds

        sst_path = os.path.join(runfolder, 'jetto.sst')
        if os.path.isfile(sst_path):
            sst = read_binary_file(sst_path)
            self['SST'] = try_convert_xarray(sst, sst_path, sst_to_xarray, on_read_error=on_read_error)

        # ssts are special. All ssts have the same time/spatial base, so merge them together
        # Do not merge them for now. Too slow! Mechanism kept commented out
        sst_part_paths = [os.path.join(runfolder, file) for file in os.listdir(runfolder) if
                            file[:-1].endswith('sst')]

        for sst_path in sorted(sst_part_paths):
            sst = read_binary_file(sst_path)
            n_sst = int(sst_path[-1])
            ds = try_convert_xarray(sst, sst_path, sst_to_xarray, on_read_error=on_read_error)
            self['SST' + str(n_sst)] = ds


def try_convert_xarray(parsed_file, file_path, function, on_read_error='raise'):
    try:
        ds = function(parsed_file)
    except Exception as ee:
        print('ERROR: converting {!s} to xarray using {!s} raises:'.format(file_path, function))
        print('ERROR:', ee)
        print('ERROR: Something might be off with the raw binary file. Ignoring..')
        ds = None
        if on_read_error == 'raise':
            raise
    return ds


if __name__ == '__main__':
    jetto_run = JETTO('/home/karel/working/jetto-pythontools/testdata/jetto-sanco-pencil-esco-qlknn')
    embed()
    #import ipdb; ipdb.set_trace()
    #jst = JETTO('../testdata/jetto-sanco-pencil-esco-qlknn')
