# Created by buchanj, 28 Nov 2016
# Adapted by aaronho, 31 Jul 2020

# These functions read and manipulate the output netCDF file of a TRANSP run.

import os
from getpass import getuser
import re
import datetime
from collections import OrderedDict
from pathlib import Path
import logging

import numpy as np
from scipy.interpolate import interp1d

from jetto_tools import binary

logger = logging.getLogger('jetto_tools.jams')
logger.setLevel(logging.INFO)

try:
    from netCDF4 import Dataset
except ImportError:
    logger.warning("Python module 'netCDF4' not found. Submodule 'transp' needs it")
    raise


# ================================================================================================================

# List of required 2D signals from netCDF file (dict value is name in PPF)
signals = {
    'BDENS'   : 'BDN',
    'BDENS_H' : 'BDNH',
    'BDENS_D' : 'BDND',
    'BDENS_T' : 'BDNT',
    'BDEP_D': 'BDPD',
    'CURB'  : 'CURB',
    'ECCUR' : 'ECC',
    'LHCUR' : 'LHC',
    'NE'    : 'NE',
    'NI'    : 'NI',
    'NIMP'  : 'NIMP',
    'NMINI' : 'NMIN',
    'OMEGA' : 'OME',
    'PBE'   : 'PBE',
    'PBI'   : 'PBI',
    'PBTH'  : 'PBTH',
    'PCUR'  : 'XIP',
    'PEECH' : 'PEC',
    'PEICH' : 'QRFE',
    'PIICH' : 'QRFI',
    'PPLAS' : 'PR',
    'PRAD'  : 'PRAD',
    'Q'     : 'Q',
    'SBE'   : 'SBE',
    'SBE_D' : 'SBED',
    'SBE_T' : 'SBET',
    'SBTH_H': 'SBH',
    'SBTH_D': 'SBD',
    'SBTH_T': 'SBT',
    'SCEV'  : 'SCEV',
    'SDEP_D': 'SDPD',
    'SVH'   : 'SVH',
    'SVD'   : 'SVD',
    'SVT'   : 'SVT',
    'TE'    : 'TE',
    'TI'    : 'TI',
    'TQIN'  : 'TQIN',
    'UBPAR_H' : 'UPAH',
    'UBPRP_H' : 'UPPH',
    'UBPAR_D' : 'UPAD',
    'UBPRP_D' : 'UPPD',
    'UBPAR_T' : 'UPAT',
    'UBPRP_T' : 'UPPT',
    'UMINPA'  : 'UMPA',
    'UMINPP'  : 'UMPP',
    'ZEFFP'   : 'ZEF'
    }

# Conversion factors from TRANSP units to SI units
conversions = {
    'BDENS'   : 1.0e6,      # -> 1/m3
    'BDENS_H' : 1.0e6,      # -> 1/m3
    'BDENS_D' : 1.0e6,      # -> 1/m3
    'BDENS_T' : 1.0e6,      # -> 1/m3
    'BDEP_D': 1.0e6,        # -> 1/m3/s
    'CURB'  : 1.0e4,        # -> A/m2
    'ECCUR' : 1.0e4,        # -> A/m2
    'LHCUR' : 1.0e4,        # -> A/m2
    'NE'    : 1.0e6,        # -> 1/m3
    'NI'    : 1.0e6,        # -> 1/m3
    'NIMP'  : 1.0e6,        # -> 1/m3
    'NMINI' : 1.0e6,        # -> 1/m3
    'OMEGA' : 1.0,          # -> rad/s
    'PBE'   : 1.0e6,        # -> W/m3
    'PBI'   : 1.0e6,        # -> W/m3
    'PBTH'  : 1.0e6,        # -> W/m3
    'PCUR'  : 1.0,          # -> A
    'PEECH' : 1.0e6,        # -> W/m3
    'PEICH' : 1.0e6,        # -> W/m3
    'PIICH' : 1.0e6,        # -> W/m3
    'PPLAS' : 1.0,          # -> Pa
    'PRAD'  : 1.0e6,        # -> W/m3
    'Q'     : 1.0,          # -> unitless
    'SBE'   : 1.0e6,        # -> 1/m3/s
    'SBE_D' : 1.0e6,        # -> 1/m3/s
    'SBE_T' : 1.0e6,        # -> 1/m3/s
    'SBTH_H': 1.0e6,        # -> 1/m3/s
    'SBTH_D': 1.0e6,        # -> 1/m3/s
    'SBTH_T': 1.0e6,        # -> 1/m3/s
    'SCEV'  : 1.0e6,        # -> 1/m3/s
    'SDEP_D': 1.0e6,        # -> 1/m3/s
    'SVH'   : 1.0e6,        # -> 1/m3/s
    'SVD'   : 1.0e6,        # -> 1/m3/s
    'SVT'   : 1.0e6,        # -> 1/m3/s
    'TE'    : 1.0,          # -> eV
    'TI'    : 1.0,          # -> eV
    'TQIN'  : 1.0e6,        # -> Nm/m3
    'UBPAR_H' : 1.0e6,      # -> J/m3
    'UBPRP_H' : 1.0e6,      # -> J/m3
    'UBPAR_D' : 1.0e6,      # -> J/m3
    'UBPRP_D' : 1.0e6,      # -> J/m3
    'UBPAR_T' : 1.0e6,      # -> J/m3
    'UBPRP_T' : 1.0e6,      # -> J/m3
    'UMINPA'  : 1.0e6,      # -> J/m3
    'UMINPP'  : 1.0e6,      # -> J/m3
    'ZEFFP' : 1.0           # -> unitless
    }

transp_ex_signals = ['PPLAS', 'Q', 'NE', 'TE', 'TI', 'NIMP', 'OMEGA', 'PRAD', 'ZEFFP', 'PBE', 'PBI', 'SBTH_D', 'CURB', 'BDENS_D', 'UBPAR_D', 'TQIN', 'PEICH', 'PIICH', 'UMINPA', 'NMINI']
transp_ext_signals = ['PCUR']

# Name of signals inside JETTO ex-file structure
exfile_signals = {
    'BDENS_D' : 'NB',
    'CURB'  : 'JZNB',
    'NE'    : 'NE',
    'NMINI' : 'RF',
    'NIMP'  : 'NIMP',
    'OMEGA' : 'ANGF',
    'PBE'   : 'QNBE',
    'PBI'   : 'QNBI',
    'PEICH' : 'QRFE',
    'PIICH' : 'QRFI',
    'PPLAS' : 'PR',
    'PRAD'  : 'PRAD',
    'Q'     : 'Q',
    'SBTH_D': 'SB1',
    'TE'    : 'TE',
    'TI'    : 'TI',
    'TQIN'  : 'TORQ',
    'UBPAR_D' : 'WFNB',
    'UMINPA'  : 'WFRF',
    'ZEFFP' : 'ZEFF'
    }
extfile_signals = {
    'PCUR'  : 'CUR'
    }

# Conversion factor string from SI units into JETTO units (numeric value added inside function of binary.py)
exfile_scales = {
    'BDENS_D' : '1.0E6',
    'CURB'  : '1.0E7',
    'NE'    : '1.0E6',
    'NMINI' : '1.0E6',
    'NIMP'  : '1.0E6',
    'OMEGA' : '1.0',
    'PBE'   : '0.1',
    'PBI'   : '0.1',
    'PEICH' : '0.1',
    'PIICH' : '0.1',
    'PPLAS' : '1.0',
    'PRAD'  : '0.1',
    'Q'     : '1.0',
    'SBTH_D': '1.0E6',
    'TE'    : '1.0',
    'TI'    : '1.0',
    'TQIN'  : '0.1',
    'TVEC1' : '1.0',
    'UBPAR_D' : '0.1',
    'UMINPA'  : '0.1',
    'XVEC1' : '1.0',
    'ZEFFP' : '1.0'
    }
extfile_scales = {
    'PCUR'  : '1.0',
    'TVEC1' : '1.0'
    }


# Description of data field for display in MODEX
exfile_descriptions = {
    'BDENS_D' : 'Fast Ion Density',
    'CURB'  : 'NB Driven Curr.Dens.',
    'NE'    : 'Electron Density',
    'NMINI' : 'Ion Density',
    'NIMP'  : 'Impurity Density',
    'OMEGA' : 'Angular Frequency',
    'PBE'   : 'Power Density Electrons',
    'PBI'   : 'Power Density Ions',
    'PEICH' : 'Power Density Electrons',
    'PIICH' : 'Power Density Ions',
    'PPLAS' : 'Pressure (from TRANSP)',
    'PRAD'  : 'Radiation',
    'Q'     : 'q (safety factor)',
    'SBTH_D'  : 'Particle Source 1',
    'TE'    : 'Electron Temperature',
    'TI'    : 'Ion Temperature',
    'TQIN'  : 'Torque',
    'TVEC1' : 'TIME',
    'UBPAR_D' : 'Fast Ion Energy Density',
    'UMINPA'  : 'Fast Ion Energy Density',
    'XVEC1' : 'RHO normalized',
    'ZEFFP' : 'Z-effective'
    }
extfile_descriptions = {
    'PCUR'  : 'Plasma Current',
    'TVEC1' : 'TIME'
    }

# Description of data units for display in MODEX
exfile_units = {
    'BDENS_D' : 'm-3',
    'CURB'  : 'A m-2',
    'NE'    : 'm-3',
    'NMINI' : 'm-3',
    'NIMP'  : 'm-3',
    'OMEGA' : 'rad s-1',
    'PBE'   : 'W m-3',
    'PBI'   : 'W m-3',
    'PEICH' : 'W m-3',
    'PIICH' : 'W m-3',
    'PPLAS' : 'Pa',
    'PRAD'  : 'W m-3',
    'Q'     : '',
    'SBTH_D': 'm-3 s-1',
    'TE'    : 'eV',
    'TI'    : 'eV',
    'TQIN'  : 'N m-2',
    'TVEC1' : 's',
    'UBPAR_D' : 'J m-3',
    'UMINPA'  : 'J m-3',
    'XVEC1' : None,
    'ZEFFP' : ''
    }
extfile_units = {
    'PCUR'  : 'A',
    'TVEC1' : 's'
    }


def generate_exfile_structure(rootgrp, database, shot, tbeg=None, tend=None, metatag=None, time_shift=None, use_x_bdy=False):

    exdata = None
    if isinstance(rootgrp,Dataset):
        tag = metatag if isinstance(metatag,str) else rootgrp.Runid.strip()

        if 'X' not in rootgrp.variables:
            raise ValueError("XVEC1 cannot be computed from TRANSP data. Aborting!")

        xctr = rootgrp['X'][0]
        xbdy = rootgrp['XB'][0]
        raw_time = rootgrp[rootgrp['X'].dimensions[0]][:]

        # netCDF 1.15 returns arrays as numpy masked arrays, script assumes regular numpy arrays for backwards compatibility
        if isinstance(raw_time,np.ma.core.MaskedArray):
            raw_time = raw_time.data
        if isinstance(xctr,np.ma.core.MaskedArray):
            xctr = xctr.data
        if isinstance(xbdy,np.ma.core.MaskedArray):
            xbdy = xbdy.data

        # Determine indices belonging to requested time window, if applicable
        idxbeg = None
        if tbeg is not None:
            idxvec = np.where(raw_time > tbeg)[0]
            if len(idxvec) > 0:
                idxbeg = idxvec[0]
            else:
                print("TRANSP simulation ends at t=%.4f" % (np.nanmax(raw_time)))
        idxend = None
        if tend is not None:
            idxvec = np.where(raw_time < tend)[0]
            if len(idxvec) > 0:
                idxend = idxvec[-1] + 1 if idxvec[-1] != raw_time.size else None
            else:
                print("TRANSP simulation begins at t=%.4f" % (np.nanmin(raw_time)))

        # Shift time vector to convert to 'real time'
        tshift = float(time_shift) if isinstance(time_shift,(int,float)) else 0.0
        time = np.atleast_3d(raw_time[idxbeg:idxend] + tshift)
        time = np.swapaxes(time,0,1)

        # JETTO stretches profiles without an explicit rho=0 and might extrapolate to negative values without an explicit rho=1
        xvec = np.hstack((np.atleast_2d([0.0]),np.atleast_2d(xbdy))) if use_x_bdy else np.hstack((np.atleast_2d([0.0]),np.atleast_2d(xctr),np.atleast_2d([1.0])))

        # Generate blank ex-file structure
        exdata = binary.create_exfile_structure(database, shot)

        xtag = 'XVEC1'
        exdata = binary.modify_entry(exdata, xtag, xvec, dtype='float', units=exfile_units[xtag], description=exfile_descriptions[xtag], scale=exfile_scales[xtag])
        ttag = 'TVEC1'
        exdata = binary.modify_entry(exdata, ttag, time, dtype='float', units=exfile_units[ttag], description=exfile_descriptions[ttag], scale=exfile_scales[ttag])

        # Adds radial coordinate system vectors to EX-file, only RHO is strictly needed by JETTO?
        psin = None
        srho = None
        xbdy = xbdy.flatten()
        xctr = xctr.flatten()
        xexf = xvec.flatten()
        if 'RMNMP' in rootgrp.variables:
            data = rootgrp['RMNMP'][idxbeg:idxend]
            if isinstance(data,np.ma.core.MaskedArray):
                data = data.data
            rmin_bdy = data / np.atleast_2d(data[:,-1]).T
            ifunc = interp1d(xbdy, rmin_bdy, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            rmin = ifunc(xexf)
            exdata = binary.add_entry(exdata, 'RA', rmin, dtype='float', units='m', description='Minor radius, normalised', scale='1.0', xbase=xtag, tag=tag)
        if 'PLFLX' in rootgrp.variables:
            data = rootgrp['PLFLX'][idxbeg:idxend]
            if isinstance(data,np.ma.core.MaskedArray):
                data = data.data
            psin_bdy = data / np.atleast_2d(data[:,-1]).T
            ifunc = interp1d(xbdy, psin_bdy, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            psin = ifunc(xexf)
            exdata = binary.add_entry(exdata, 'PSI', psin, dtype='float', units=None, description='Normalised poloidal flux', scale='1.0', xbase=xtag, tag=tag)
        if 'TRFLX' in rootgrp.variables:
            data = rootgrp['TRFLX'][idxbeg:idxend]
            if isinstance(data,np.ma.core.MaskedArray):
                data = data.data
            srho = np.sqrt(np.abs(data))
            xrho_bdy = srho / np.atleast_2d(srho[:,-1]).T
            ifunc = interp1d(xbdy, xrho_bdy, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            xrho = ifunc(xexf)
            exdata = binary.add_entry(exdata, 'XRHO', xrho, dtype='float', units=None, description='Sqrt of normalised toroidal flux', scale='1.0', xbase=xtag, tag=tag)
        if psin is not None:
            spsi = np.sqrt(np.abs(psin))
            exdata = binary.add_entry(exdata, 'SPSI', spsi, dtype='float', units=None, description='Sqrt of normalised poloidal flux', scale='1.0', xbase=xtag, tag=tag)
        if 'RMNMP' in rootgrp.variables and 'RMJMP' in rootgrp.variables:
            rout_bdy = (rootgrp['RMNMP'][idxbeg:idxend] + rootgrp['RMJMP'][idxbeg:idxend]) * 0.01
            if isinstance(rout_bdy,np.ma.core.MaskedArray):
                rout_bdy = rout_bdy.data
            ifunc = interp1d(xbdy, rout_bdy, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            rout = ifunc(xexf)
            exdata = binary.add_entry(exdata, 'R', rout, dtype='float', units='m', description='Major radius', scale='0.01', xbase=xtag, tag=tag)
        if srho is not None and 'BMIN' in rootgrp.variables and 'BMAX' in rootgrp.variables:
            bmag = (rootgrp['BMAX'][idxbeg:idxend] + rootgrp['BMIN'][idxbeg:idxend]) / 2.0
            if isinstance(bmag,np.ma.core.MaskedArray):
                bmag = bmag.data
            rhoj_bdy = srho / np.sqrt(np.pi * np.atleast_2d(bmag[:,0]).T)
            ifunc = interp1d(xbdy, rhoj_bdy, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            rhoj = ifunc(xexf)
            exdata = binary.add_entry(exdata, 'RHO', rhoj, dtype='float', units='m', description='JETTO rho coordinate', scale='0.01', xbase=xtag, tag=tag)

        # Add signals - Need X as first dimension, then T. This is opposite to how they seem to be stored in the NetCDF file.
        for ii in range(0,len(transp_ex_signals)):

            key = transp_ex_signals[ii]
            if key in ['NIMP', 'PBI', 'UBPAR_D', 'UMINPA']:
                continue
            if key not in rootgrp.variables:
                print(key+' not found in NETCDF file')
                continue

            # Applies scaling to return to physical units
            data_ctr = rootgrp[key][idxbeg:idxend] * conversions[key]

            # Linear extrapolation to include rho=1, issues in JETTO if negative values occur there
            if isinstance(data_ctr,np.ma.core.MaskedArray):
                data_ctr = data_ctr.data
            ifunc = interp1d(xctr, data_ctr, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            data = ifunc(xexf)

            # Enforces non-negative values for temperature and density profiles (should enforce on energy density as well?)
            if not use_x_bdy:
                if key == 'PPLAS':
                    mask = (data < 1.0e3)
                    if np.any(mask):
                        data[mask] = 1.0e3
                if key in ['TE', 'TI']:
                    mask = (data < 10.0)
                    if np.any(mask):
                        data[mask] = 10.0
                if key == 'NE':
                    mask = (data < 1.0e17)
                    if np.any(mask):
                        data[mask] = 1.0e17
                if key in ['BDENS_D', 'NMINI']:
                    mask = (data < 0.0)
                    if np.any(mask):
                        data[mask] = 0.0

            # Add data to EX-file
            exdata = binary.add_entry(exdata, exfile_signals[key], data, dtype='float', units=exfile_units[key], description=exfile_descriptions[key], scale=exfile_scales[key], xbase=xtag, tag=tag)

        # Create Composite signals
        if 'PBI' in rootgrp.variables:
            data_ctr = rootgrp['PBI'][idxbeg:idxend] * conversions['PBI']
            if 'PBTH' in rootgrp.variables:
                data_ctr = data_ctr + rootgrp['PBTH'][idxbeg:idxend] * conversions['PBTH']
            if isinstance(data_ctr,np.ma.core.MaskedArray):
                data_ctr = data_ctr.data
            ifunc = interp1d(xctr, data_ctr, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            data = ifunc(xexf)
            exdata = binary.add_entry(exdata, exfile_signals['PBI'], data, dtype='float', units=exfile_units['PBI'], description=exfile_descriptions['PBI'], scale=exfile_scales['PBI'], xbase=xtag, tag=tag)
        if 'UBPAR_D' in rootgrp.variables:
            data_ctr = rootgrp['UBPAR_D'][idxbeg:idxend] * conversions['UBPAR_D']
            if 'UBPRP_D' in rootgrp.variables:
                data_ctr = data_ctr + rootgrp['UBPRP_D'][idxbeg:idxend] * conversions['UBPRP_D']
            if isinstance(data_ctr,np.ma.core.MaskedArray):
                data_ctr = data_ctr.data
            ifunc = interp1d(xctr, data_ctr, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            data = ifunc(xexf)
            exdata = binary.add_entry(exdata, exfile_signals['UBPAR_D'], data, dtype='float', units=exfile_units['UBPAR_D'], description=exfile_descriptions['UBPAR_D'], scale=exfile_scales['UBPAR_D'], xbase=xtag, tag=tag)
        if 'UMINPA' in rootgrp.variables:
            data_ctr = rootgrp['UMINPA'][idxbeg:idxend] * conversions['UMINPA']
            if 'UMINPP' in rootgrp.variables:
                data_ctr = data_ctr + rootgrp['UMINPP'][idxbeg:idxend] * conversions['UMINPP']
            if isinstance(data_ctr,np.ma.core.MaskedArray):
                data_ctr = data_ctr.data
            ifunc = interp1d(xctr, data_ctr, axis=1, kind='linear', bounds_error=False, fill_value='extrapolate')
            data = ifunc(xexf)
            exdata = binary.add_entry(exdata, exfile_signals['UMINPA'], data, dtype='float', units=exfile_units['UMINPA'], description=exfile_descriptions['UMINPA'], scale=exfile_scales['UMINPA'], xbase=xtag, tag=tag)

    return exdata


def generate_extfile_structure(rootgrp, database, shot, tbeg=None, tend=None, metatag=None, time_shift=None):

    extdata = None
    if isinstance(rootgrp,Dataset):
        tag = metatag if isinstance(metatag,str) else rootgrp.Runid.strip()

        if 'TIME' not in rootgrp.variables:
            raise ValueError("TVEC1 field cannot be computed from TRANSP data. Aborting!")

        raw_time = rootgrp['TIME'][:]

        # netCDF 1.15 returns arrays as numpy masked arrays, script assumes regular numpy arrays for backwards compatibility
        if isinstance(raw_time,np.ma.core.MaskedArray):
            raw_time = raw_time.data

        # Determine indices belonging to requested time window, if applicable
        idxbeg = None
        if tbeg is not None:
            idxvec = np.where(raw_time > tbeg)[0]
            if len(idxvec) > 0:
                idxbeg = idxvec[0]
            else:
                print("TRANSP simulation ends at t=%.4f" % (np.nanmax(raw_time)))
        idxend = None
        if tend is not None:
            idxvec = np.where(raw_time < tend)[0]
            if len(idxvec) > 0:
                idxend = idxvec[-1] + 1 if idxvec[-1] != raw_time.size else None
            else:
                print("TRANSP simulation begins at t=%.4f" % (np.nanmin(raw_time)))

        # Shift time vector to convert to 'real time'
        tshift = float(time_shift) if isinstance(time_shift,(int,float)) else 0.0
        time = np.atleast_2d(raw_time[idxbeg:idxend] + tshift)

        # Generate blank ex-file structure
        extdata = binary.create_exfile_structure(database, shot, extfile=True)

        ttag = 'TVEC1'
        extdata = binary.modify_entry(extdata, ttag, time, dtype='float', units=extfile_units[ttag], description=extfile_descriptions[ttag], scale=extfile_scales[ttag])

        # Add signals
        for ii in range(0,len(transp_ext_signals)):

            key = transp_ext_signals[ii]
            if key not in rootgrp.variables:
                print(key+' not found in NETCDF file')
                continue
            data = rootgrp[key][idxbeg:idxend] * conversions[key]
            if isinstance(data,np.ma.core.MaskedArray):
                data = data.data
            extdata = binary.add_entry(extdata, extfile_signals[key], data, dtype='float', units=extfile_units[key], description=extfile_descriptions[key], scale=extfile_scales[key], xbase=ttag, tag=tag)

    return extdata


def convert_cdf_to_exfile(machine, pulse, identifier=None, outpath=None, tbeg=None, tend=None, inpath=None, tstart=None):

    if not isinstance(machine,str):
        raise TypeError("Machine specification must be a string")
    if not isinstance(pulse,int):
        raise TypeError("Shot / pulse number must be an integer")

    # Construct path to results directory for this run
    ipath = None
    extension = ".CDF"
    if isinstance(identifier,str):
        ipath = "/common/transp_shared/Data/result/"+machine+"/"+str(pulse)+"/"+identifier+"/"+str(pulse)+identifier+extension
    if isinstance(inpath,str):
        ipath = inpath
    if not isinstance(ipath,str):
        raise ValueError("Input CDF file path not provided!")

    # Path to netCDF file
    cdfpath = Path(ipath)
    if isinstance(inpath,str) and not cdfpath.is_file():
        raise IOError("   Explicitly requested file %s not found. Aborting ex-file generation!" % (inpath))
    elif not cdfpath.is_file():
        extension = ".cdf"
        ipath = "/common/transp_shared/Data/result/"+machine+"/"+str(pulse)+"/"+identifier+"/"+str(pulse)+identifier+extension
        cdfpath = Path(ipath)

    opath = "./"+str(cdfpath.stem)+".ex" if not isinstance(outpath,str) else outpath
    expath = Path(opath)
    extpath = Path(opath+"t")
    if expath.exists() and not expath.is_file():
        raise IOError("   Target %s already exists but is not a file. Aborting ex-file generation!" % str(expath.absolute()))
    elif expath.is_file():
        print("   File %s already exists, overwriting..." % str(expath.absolute()))
    if extpath.exists() and not extpath.is_file():
        raise IOError("   Target %s already exists but is not a file. Aborting ext-file generation!" % str(extpath.absolute()))
    elif extpath.is_file():
        print("   File %s already exists, overwriting..." % str(extpath.absolute()))

    # Check file exists in results directory
    ier = 1
    if cdfpath.is_file():

        # Open existing NetCDF file and read signals from it
        rootgrp = Dataset( str(cdfpath.resolve()), mode='r', format='NETCDF3_CLASSIC' )

        exdata = generate_exfile_structure(rootgrp, machine, pulse, tbeg=tbeg, tend=tend, metatag=str(cdfpath.absolute()), time_shift=tstart, use_x_bdy=False)

        if exdata is not None:
            ier = binary.write_binary_exfile(exdata, str(expath.absolute()))
            if ier != 0:
                print("   Ex-file data write failed! Something went wrong in data transfer from CDF to ex-file format.")
        else:
            print("   Ex-file data generation failed! Check TRANSP file for data availability and validity.")

        extdata = generate_extfile_structure(rootgrp, machine, pulse, tbeg=tbeg, tend=tend, metatag=str(cdfpath.absolute()), time_shift=tstart)

        if extdata is not None:
            ier = binary.write_binary_exfile(extdata, str(expath.absolute()))
            if ier != 0:
                print("   Ext-file data write failed! Something went wrong in data transfer from CDF to ext-file format.")
        else:
            print("   Ext-file data generation failed! Check TRANSP file for data availability and validity.")

    else:
        print("   File %s not found. Aborting ex-file generation!" % (str(cdfpath.absolute())))

    return ier


# Function provided by fkochl - 19/08/2020
def convert_jsp_jst_to_netcdf(
    machine_name,
    shot_no,
    seq_no,
    jsp_file,
    jst_file,
    legacy: bool=True,
    output_directory: Path=None
) -> int:
    """ 
    Converts .jsp and .jst JETTO binary files into TRANSP compatible netCDF3 files
    in accordance with JETDSP TRANSP input format requirements. Effectively all binary
    numerical data is converted into netCDF3.

    legacy : bool
        If True, the signals will be written on a shared radial base for bin
        boundaries (XVEC1) and bin centres (XVEC2). Otherwise (default),
        seperate dimensions will be created.
    """
    # Set status flag on success
    ier = 0
    float_format = 'f4'

    # Create paths to target files to write.
    if output_directory is None:
        trg_file = Path(jsp_file).parent.joinpath('profiles.CDF')
        trg_file2 = Path(jst_file).parent.joinpath('timetraces.CDF')
    else:
        if not isinstance(output_directory, Path):
            output_directory = Path(output_directory)
        
        trg_file = output_directory.joinpath('profiles.CDF')
        trg_file2 = output_directory.joinpath('timetraces.CDF')

    # Check output files don't already exist.
    for file in (trg_file, trg_file2):
        if file.exists():
            raise ValueError(f"Output file \'{file}\' already exists.")

    # Create output directory if it doesn't exist.
    trg_file.parent.mkdir(parents=True, exist_ok=True)
    trg_file2.parent.mkdir(parents=True, exist_ok=True)

    # Load jsp file.
    jspdat = binary.read_binary_file(jsp_file)

    with Dataset(str(trg_file.absolute()), mode='w', format='NETCDF3_CLASSIC') as trg:

        # Create the dimensions of the netCDF file
        xvec1_size = np.size(jspdat['XVEC1'])
        xvec2_size = np.size(jspdat['XVEC2'])
        trg.createDimension('TIME', np.size(jspdat['TIME']))
        trg.createDimension('TIME3', np.size(jspdat['TIME']))
        trg.createDimension('X', xvec1_size)
        trg.createDimension('XB', xvec1_size if legacy else xvec2_size)
        trg.createDimension('RMAJM', xvec1_size)

        TIME = trg.createVariable('TIME', float_format, ('TIME',))
        TIME[:] = jspdat['TIME']
        TIME.units = jspdat['INFO']['TIME']['UNITS']
        TIME.long_name = jspdat['INFO']['TIME']['DESC']

        TIME3 = trg.createVariable('TIME3', float_format, ('TIME3',))
        TIME3[:] = jspdat['TIME']
        TIME3.units = jspdat['INFO']['TIME']['UNITS']
        TIME3.long_name = jspdat['INFO']['TIME']['DESC']

        time_size = len(jspdat['TIME'])
        
        # Radial grid for bin boundaries.
        X = trg.createVariable('X', float_format, ('TIME3','X',))
        X[:, :] = np.tile(jspdat['XVEC1'], (time_size, 1))
        X.units = ' '
        X.long_name = jspdat['INFO']['XVEC1']['DESC']

        # Radial grid for bin centres.
        XB = trg.createVariable('XB', float_format, ('TIME3','XB',))

        if legacy:
            # XB has size of XVEC1 = 1 + size of XVEC2.
            XB[:, :-1] = np.tile(jspdat['XVEC2'], (time_size, 1))
            # Copy 2nd to last column to last column.
            XB[:, -1] = XB[:, -2]
        else:
            # XB has size of XVEC2.
            XB[:, :] = np.tile(jspdat['XVEC2'], (time_size, 1))

        XB.units = ' '
        XB.long_name = jspdat['INFO']['XVEC2']['DESC']

        #RZON: JSP/RHO
        RZON = trg.createVariable('RZON', float_format, ('TIME3','X',))
        RZON[:, :] = jspdat['RHO'][:, :]
        RZON.units = ' '
        RZON.long_name = jspdat['INFO']['RHO']['DESC']

        #RBOUN: JSP/RHO on R2 grid
        RBOUN = trg.createVariable('RBOUN', float_format, ('TIME3', 'X'))
        
        for i in range(time_size):
            RBOUN[i, :] = RZON[i, :] - 0.5*(RZON[i,2]-RZON[i,1])
        
        RBOUN[:, 0] = 0.0
        RBOUN.units = ' '
        RBOUN.long_name = 'rho_tor (cell-facing grid)'

        #RNMNP: JSP/XA (JETTO: evaluated as (R-Rmag/(Rsep,out-Rmag) on R2 grid
        RMNMP = trg.createVariable('RMNMP', float_format, ('TIME3', 'X'))
        RMNMP[:, 0] = jspdat['XA'][:, 0]
        RMNMP[:, 1:] = 0.5 * (jspdat['XA'][:, :-1] + jspdat['XA'][:, 1:])
        RMNMP.units = ' '
        RMNMP.long_name = jspdat['INFO']['XA']['DESC']
        
        #RMAJM: combination of JSP/RI, Rmag, JSP/R
        RMAJM = trg.createVariable('RMAJM', float_format, ('TIME3','RMAJM',))
        RMAJM[:, :] = jspdat['R'][:, :]
        
        # for i in range( time_size ):
        #     RMAJM[i,:] = jspdat['R'][i,:]
#            RMAJM[i,0:xvec1_size] = jspdat['RI'][i,:]
#            RMAJM[i,xvec1_size] = 0.5*(jspdat['RI'][i,0] + jspdat['R'][i,0])
#            RMAJM[i,xvec1_size+1:] = jspdat['R'][i,:]
        RMAJM.units = ' '
        RMAJM.long_name = jspdat['INFO']['XVEC1']['DESC']

        # Create dummy entities:
        dumlist = {'DRAVFAC', 'DVOL', 'DAREA', 'DRAV'}
        for name in dumlist:
            trg.createVariable(name, float_format, ('TIME3','X'))
            trg.variables[name][:] = 0.0
            trg.variables[name].units = '--'
            trg.variables[name].long_name = 'dummy entity'

        # Create JSP entities:
        for name in jspdat:
            if name not in ('TIME', 'XVEC1', 'XVEC2', 'INFO') and 'XBASE' in jspdat['INFO'][name]:
                xbasename = jspdat['INFO'][name]['XBASE']
                xbasenameout = 'XB' if xbasename == 'XVEC2' else 'X'

                trg.createVariable(name, float_format, ('TIME3', xbasenameout))
                
                if legacy:
                    if xbasename == 'XVEC1':
                        trg.variables[name][:, :] = jspdat[name][:, :]
                    elif xbasename == 'XVEC2':
                        trg.variables[name][:, :-1] = jspdat[name][:, :]
                        # Copy 2nd to last column to last column.
                        trg.variables[name][:, -1] = jspdat[name][:, -1]
                else:
                    trg.variables[name][:, :] = jspdat[name][:, :]

                trg.variables[name].units = jspdat['INFO'][name]['UNITS']
                trg.variables[name].long_name = jspdat['INFO'][name]['DESC']

        TDUM = trg.createVariable('TDUM', float_format, ('TIME',))
        TDUM[:] = 0.0
        TDUM.units = '-'
        TDUM.long_name = 'dummy signal'

        trg.description = 'JETTO profile data     '
        if shot_no is not None and seq_no is not None:
           seq_str = str(min(99,max(0,int(seq_no)))).zfill(2)
           shot_str = re.sub('[^0-9]','',repr(shot_no))
           trg.Runid = shot_str+seq_str+'P '
           trg.shot = int(shot_str)
        else:
           #catid=cat.read_catid(os.path.dirname(jsp_file))
           trg.Runid = 1
           #trg.shot = int(catid['Shot ID']) 
           trg.shot = 1         
        trg.CDF_date = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S    ")
        trg.BUILD_date = 'Fri May  3 15:19:16 EDT'
        trg.NFT = 1 #number of entries with TIME dependence only excluding TIME and TIME3 signals - corresponding to JST output
        trg.NBAL = 0 #number of other datasets ("multigraph" etc)
        trg.NFXT = len(trg.variables)-trg.NFT-trg.NBAL-2 #number of profile entries with TIME3 + radial coordinate dependency - corresponding to JSP output
        trg.NZONES = X.shape[1]
        trg.R = np.array([ 0.,  0.])

        print(str(trg_file.absolute())+ ' created')

    # Write time trace output file.
    jstdat = binary.read_binary_file(jst_file)
    jstdat['TVEC1'] = np.transpose(jstdat['TVEC1'])

    with Dataset(str(trg_file2.absolute()), mode='w', format='NETCDF3_CLASSIC') as trg:
        timveclen = np.size(jstdat['TVEC1'])
        trg.createDimension('TIME', timveclen)
        trg.createDimension('TIME3', timveclen)
        trg.createDimension('X', np.size(jspdat['XVEC1']))
        trg.createDimension('XB', np.size(jspdat['XVEC1']))
        trg.createDimension('RMAJM', np.size(jspdat['XVEC1']))

        TIME = trg.createVariable('TIME', float_format, ('TIME',))
        TIME[:] = jstdat['TVEC1']
        TIME.units = jstdat['INFO']['TVEC1']['UNITS']
        TIME.long_name = jstdat['INFO']['TVEC1']['DESC']

        TIME3 = trg.createVariable('TIME3', float_format, ('TIME3',))
        TIME3[:] = jstdat['TVEC1']
        TIME3.units = jstdat['INFO']['TVEC1']['UNITS']
        TIME3.long_name = jstdat['INFO']['TVEC1']['DESC']

        X = trg.createVariable('X', float_format, ('TIME3','X',))
        for i in range( timveclen ):
            X[i,:] = float((i)/(timveclen-1))
        X.units = ' '
        X.long_name = jspdat['INFO']['XVEC1']['DESC']

        XB = trg.createVariable('XB', float_format, ('TIME3','XB',))
        XB[:,:] = X[:,:]
        XB.units = ' '
        XB.long_name = jspdat['INFO']['XVEC2']['DESC']

        RZON = trg.createVariable('RZON', float_format, ('TIME3','X',))
        RZON[:,:] = X[:,:]
        RZON.units = ' '
        RZON.long_name = jspdat['INFO']['XVEC1']['DESC']
        RBOUN = trg.createVariable('RBOUN', float_format, ('TIME3','X',))
        RBOUN[:,:] = X[:,:]
        RBOUN.units = ' '
        RBOUN.long_name = jspdat['INFO']['XVEC1']['DESC']
        RMAJM = trg.createVariable('RMAJM', float_format, ('TIME3','RMAJM',))
        RMAJM[:,:] = X[:,:]
        RMAJM.units = ' '
        RMAJM.long_name = jspdat['INFO']['XVEC1']['DESC']
        RMNMP = trg.createVariable('RMNMP', float_format, ('TIME3','X',))
        RMNMP[:,:] = X[:,:]
        RMNMP.units = ' '
        RMNMP.long_name = jspdat['INFO']['XVEC1']['DESC']

        # Create dummy entities:
        dumlist = {'DRAVFAC', 'DVOL', 'DAREA', 'DRAV', 'SURF'}
        for name in dumlist:
            trg.createVariable(name, float_format, ('TIME3','X',))
            trg.variables[name][:] = 0.0
            trg.variables[name].units = '--'
            trg.variables[name].long_name = 'dummy entity'

        for name in jstdat:
            if name != 'TVEC1' and name != 'INFO' and name != 'SURF' and 'UNITS' in jstdat['INFO'][name]:
                trg.createVariable(name, float_format, ('TIME',))
                trg.variables[name][:] = np.transpose(jstdat[name][:])
                if jstdat['INFO'][name]['UNITS'] is None:
                    trg.variables[name].units = ' '
                else:
                    trg.variables[name].units = jstdat['INFO'][name]['UNITS']
                trg.variables[name].long_name = jstdat['INFO'][name]['DESC']

        trg.description = 'JETTO profile data'   
        if shot_no is not None and seq_no is not None:
          trg.Runid = shot_str+seq_str+'T '
          trg.shot = int(shot_str)
        else:
          trg.Runid = 1
          #trg.shot = int(catid['Shot ID'])
          trg.shot = 1
        trg.CDF_date = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S    ")
        trg.BUILD_date = 'Fri May  3 15:19:16 EDT'
        trg.NFXT = 11 #number of entries with TIME dependence only excluding TIME and TIME3 signals - corresponding to JST output
        trg.NFT = len(trg.variables)-trg.NFXT-2 #number of profile entries with TIME3 + radial coordinate dependency - corresponding to JSP output
        trg.NBAL = 0 #number of other datasets ("multigraph" etc)
        trg.NZONES = X.shape[1]
        trg.R = np.array([ 0.,  0.])

        print(str(trg_file2.absolute())+ ' created')
    
    # setup TRANSP-like symlinks only if requested
    if machine_name is not None and shot_no is not None and seq_no is not None:

        seq_str = str(min(99,max(0,int(seq_no)))).zfill(2)
        shot_str = re.sub('[^0-9]','',repr(shot_no))

        buid = getuser()
        trg_dir = Path('/home/'+buid+'/cmg/catalog_transp/'+machine_name+'/'+shot_str+'/J'+seq_str+'P')
        ln_file = trg_dir / ('J'+seq_str+'P.CDF')
        if not trg_dir.exists():
            trg_dir.mkdir(parents=True)
            os.symlink(trg_file.absolute(), ln_file)
            print(str(trg_dir) + ' TRANSP symlink created')
            #with open("TRANSP-like_output.id", "a") as f:
            #  f.write(str(ln_file.absolute())+ '\n')
            #  f.close()
        else :
          print('Case '+str(trg_dir)+ ' exist(s) already, choose another (max 2 digits seq.)')


        trg_dir2 = Path('/home/'+buid+'/cmg/catalog_transp/'+machine_name+'/'+shot_str+'/J'+seq_str+'T')
        ln_file2 = trg_dir2 / ('J'+seq_str+'T.CDF')
        if not trg_dir2.exists():
            trg_dir2.mkdir(parents=True)
            os.symlink(trg_file2.absolute(), ln_file2)
            print(str(trg_dir2) + ' TRANSP symlink created')
            #with open("TRANSP-like_output.id", "a") as f:
            #  f.write(str(ln_file2.absolute())+ '\n')
            #  f.close()
        else:
          print('Case '+str(trg_dir2)+ ' exist(s) already, choose another (max 2 digits seq.)')

    return ier
