import copy
import json
import datetime
import logging
from pathlib import Path
import importlib.util
from typing import MutableMapping, Optional

import numpy as np
import xarray as xr
from IPython import embed  # noqa: F401 For debugging

from jetto_tools import _template_path
from jetto_tools.binary import write_binary_exfile
from jetto_tools.matlab import mat_headers
from jetto_tools.nested_dicts import _gen_dict_extract

# Set up fancy logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

raptor_singles = []
ignore_list = ['STtimes', 'STper']

if __name__ != '__main__':
    this_module = importlib.util.find_spec(__name__, package='jetto_tools')
    this_file = Path(this_module.origin)
else:
    this_file = Path(__file__)

ex_to_raptor_map = {
    'Q': 'q',
    'NE': 'ne',
    'TE': 'te',
    'TI': 'ti',
    'PRAD': 'prad',
    'ZEFF': 'ze',
    'QNBE': 'pnbe',
    'QNBI': 'pnbi',
    'JZNB': 'jnb',
    'QECE': 'pec',
    'JZEC': 'jec',
}


def deconstruct_raptor_out(oods: MutableMapping, run_name: str,
                           on_read_error: Optional[str] = 'raise'
                           ) -> xr.Dataset:
    """ Deconstruct a .mat file loaded with `loadmat`

    Args:
        oods: An ordered mutable mappable. Will be deep-copied.
        run_name: Leaf name to try and convert

    Keyword Args:
        on_read_error: What to do when unable to convert MATLAB to Python.
            Can be 'raise' to raise an exception and 'warn' to raise a warning.

    Returns:
        A xarray.Dataset with the read variables. Tries to find the common
        base between variables on the same grid.
    """
    # To be sure, make a deepcopy
    dictobj = copy.deepcopy(oods)
    # Delete MATLAB metadata headers
    for header in mat_headers:
        try:
            del dictobj[header]
        except KeyError:
            pass
    all_matches = list(_gen_dict_extract(dictobj, run_name))
    if len(all_matches) == 0:
        raise Exception(f'Could not find any run_name={run_name!r} in oods={oods!r}')
    if len(all_matches) >= 2:
        logger.warning('More than one run matching found, grabbing the first match')

    rap_out = all_matches[0]
    time = rap_out.pop('time')
    if isinstance(time, (int, float)):
        time = [time]
    rho = rap_out.pop('rho')
    if rap_out['ntime'] == len(time):
        rap_out.pop('ntime')
    else:
        raise Exception('ntime in raptor out is not equal to the length of the time vector')
    if rap_out['nrho'] == len(rho):
        rap_out.pop('nrho')
    else:
        raise Exception('nrho in raptor out is not equal to the length of the rho vector')
    try:
        rhogauss = rap_out.pop('rhogauss')
    except KeyError:
        logger.warning('No gaussgrid found!')
        rhogauss = None
    else:
        if rap_out['nrhogauss'] == len(rhogauss):
            rap_out.pop('nrhogauss')
        else:
            raise Exception('nrhogauss in raptor out is not equal to the length of the rho vector')
    singles = {}
    vecs = time_vecs = {}
    rho_vecs = {}
    rhogauss_vecs = {}
    for key in list(rap_out.keys()):
        val = rap_out.pop(key)
        if key in ignore_list:
            logger.warning(f'{key} is in the ignore_list! Ignoring. If you need this, report on GitLab')
            continue
        # MATLAB squeezes away 1-length last dimension to annoy us, re-add it
        # Unfortunately cannot distinguish between length time values or floats
        if len(time) == 1:
            val = np.expand_dims(val, -1)
        if isinstance(val, (int, float)) or key in raptor_singles:
            if key not in raptor_singles:
                logger.warning(f'Key {key} is not in the RAPTOR singles list! Please report on GitLab')
            singles[key] = val
        elif isinstance(val, (np.ndarray)):
            if len(val) == 0:
                logger.warning('{!s} is empty! Ignoring'.format(key))
                continue
            if val.ndim == 1:
                if val.size > 0 and isinstance(val[0], np.ndarray):
                    # This was a cell array
                    # Probably jacobians
                    logger.warning('{key} is a cell array! Not implemented yet, so ignoring')
                    continue
                elif val.shape[0] == len(time):
                    time_vecs[key] = xr.Variable('time', val)
                else:
                    msg = f'1D vector {key} has shape {val.shape}, not sure what to do..'  # noqa: E501
                    if on_read_error == 'warn':
                        logger.warning(msg)
                    else:
                        raise Exception(msg)
            elif val.ndim == 2:
                if val.shape == (len(rho), len(time)):
                    rho_vecs[key] = xr.Variable(('rho', 'time'), val)
                elif val.shape == (len(rhogauss), len(time)):
                    rhogauss_vecs[key] = xr.Variable(('rhogauss', 'time'), val)
                else:
                    msg = '2D vector {key} not len(rho), len(time), not sure what to do..'
                    if on_read_error == 'warn':
                        logger.warning(msg)
                    else:
                        raise Exception(msg)
            else:
                raise Exception('vector {key} is ND, not sure what to do..')
        else:
            raise Exception('{key} is not a number, nor an array, not sure what to do..')

    vecs.update(rho_vecs)
    vecs.update(rhogauss_vecs)
    ds = xr.Dataset(time_vecs, {'rho': rho,
                                'rhogauss': rhogauss,
                                'time': time})
    if len(rap_out) != 0:
        logger.warning('Warning! Could not read variables {!s}'.format(list(rap_out.keys())))
    return ds


def raptor_out_to_exfile(raptor_ds, exfile_path, islice=-1):
    ds = extrapolate_raptor_out(raptor_ds)
    ds = ds.isel(time=islice)
    check_raptor_sanity(ds)
    with open(_template_path) as f_:
        template = json.load(f_)
    ex = copy.deepcopy(template)

    # Metadata
    now = datetime.datetime.now()
    ex['CREATION_DATE'] = now.strftime('%d/%m/%Y')
    ex['CREATION_TIME'] = now.strftime('%H:%M:%S')
    ex['VERSION'] = 'RAPTOR to EXFILE'
    # Probably contains some info needed by JAMS?
    #ex['DATABASE NAME'] = 'Some weird string'
    ex['SHOT'] = np.atleast_2d(99999)
    #ex['SHOT'] = np.atleast_2d(ex['SHOT'])

    # Coordinates

    ex['XRHO'] = np.expand_dims(ds['rho'], 0)
    ex['XVEC1'] = ex['XRHO']
    ex['TVEC1'] = np.atleast_3d(ds['time'])  # If time is 1D I guess
    ex['PSI'] = np.expand_dims(ds['psi'], 0)
    ex['SPSI'] = np.sqrt(ex['PSI'])

    for var in ['Q', 'NE', 'TE', 'TI', 'PRAD', 'ZEFF', 'QNBE', 'QNBI', 'JZNB', 'QECE', 'JZEC']:
        print('var', var, 'has RAPTOR name', ex_to_raptor_map[var])
        ex[var] = np.expand_dims(ds[ex_to_raptor_map[var]], 0)
    for var in ['RHO', 'R', 'RA']:
        #ex[var] = np.array(ex[var])
        ex[var] = np.array([[0]])
    write_binary_exfile(ex, output_file=exfile_path)


def check_raptor_sanity(ds):
    raptor_is_sane = True
    for var in ['te', 'ti', 'ne']:
        if np.any(ds[var] < 0):
            print('Negative {!s}!'.format(var))
            raptor_is_sane = False
    return raptor_is_sane


def extrapolate_raptor_out(ds):
    new_ds = ds.interp(coords={'rho': np.linspace(0, 1, len(ds['rho']))},
                       kwargs={'fill_value': 'extrapolate'})
    if ds['rhogauss'].shape != ():
        new_ds = new_ds.interp(
            coords={'rhogauss': np.linspace(0, 1, len(ds['rhogauss']))},
            kwargs={'fill_value': 'extrapolate'})
    return new_ds
