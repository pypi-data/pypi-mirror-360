# Pkg imports
try:
    from jetto_tools.binary import read_binary_file, write_binary_exfile, create_exfile_structure, generate_entry_info
except:
    # this might cause issues if directly calling from python
    import sys
    sys.exit('JETTO python tools needs to be loaded for this program to work')

# Std imports
import copy
from datetime import datetime
import os
import json
import argparse
from pathlib import Path

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

array_types = (list, tuple, np.ndarray)
number_types = (int, float, np.int8, np.int16, np.int32, np.float16, np.float32, np.float64)

def plot_profiles(exfile_orig, jsp, key):
    plt.figure(1)
    plt.plot(exfile_orig, '-r', label='jsp')
    plt.ylabel(key)
    plt.plot(jsp, '-k', label='exfile')
    plt.legend()
    plt.title('Please close figure when finished to contine with plotting')
    plt.show()


def format_jsp_profiles(jsp):
    temp = (jsp).tolist()
    temp1 = [temp]
    return  np.array(temp1)


def check_xaxis(jsp, jsp_key, key):
    """
    check that the x vector for the profile is XVEC1 and nothing else. Returns  boolean for checking
    :param jsp: jsp dictionary
    :param jsp_key: signal for the jsp
    :param key: signal for the exfile
    :return: Boolean
    """
    if key == 'XVEC1':
        # this doesn't need to be checked. Special case.
        return True

    if jsp['INFO'][jsp_key]['XBASE'] != 'XVEC1':
        print('The JSP signal {key} is on the wrong X axis - {xbasis} cannot be used the signal'
              '{ex_signal} is being removed the EXFILE. The EXFILE can only contain profiles on XVEC1 axis'
              .format(key=jsp_key, xbasis=jsp['INFO'][jsp_key]['XBASE'], ex_signal=key))

        return False
    else:
        return True


def extract_as_new(jsp_dir, time_slices=None, time_range=None, user_config_path=None, interpolate=False, plot_debug=False, verbosity=2):
    """
    Desc - reads JETTO outputs (JSP and JST) and transfers the requested physics signals into a new EXFILE

    :param jsp_dir: path to JSP directory to be used, assumed to be named jetto.jsp in provided directory
    :param time_slices: array of times which the profiles should be read from the JSP as the nearest slices (takes precedence over time_range)
    :param time_range: array of length-2 which define the time window which the profiles should be read from the JSP
    :param user_config_path: optional path to configuration file specifying which fields to transfer
    :param interpolate: toggles linear interpolation of signals onto exact time slices, but uses nearest instead of extrapolating
    :param plot_debug: debug output which allows plotting of the matched JSP signal on top the template EXFILE signals (not functional!)
    :param verbosity: set verbosity level for debugging

    :return: exfile_data - dictionary which contains the EXFILE data
    """

    # the JSP file read should throw an error is it doesn't exist
    jsp_path = Path(jsp_dir) / 'jetto.jsp'
    jsp = read_binary_file(jsp_path)
    jst_path = Path(jsp_dir) / 'jetto.jst'
    jst = read_binary_file(jst_path)

    time_start = None
    time_end = None
    time_vector = None
    if isinstance(time_slices, array_types):
        time_vector = [float(tt) for tt in time_slices]
    elif isinstance(time_slices, number_types):
        time_vector = [float(time_range)]
    elif isinstance(time_range, array_types):
        time_start = float(time_range[0]) if len(time_range) >= 1 and isinstance(time_range[0], number_types) else None
        time_end = float(time_range[1]) if len(time_range) >= 2 and isinstance(time_range[1], number_types) else None

    # Provides the mapping between EXFILE and JSP signals
    default_config_path = Path(__file__).resolve().parent / 'convert_jsp_to_exfile_config.json'
    json_config_file = Path(user_config_path) if user_config_path is not None else default_config_path
    config = None
    if json_config_file.is_file():
        with open(json_config_file, 'r') as read_file:
            config = json.load(read_file)
    else:
        print('User-defined config file not found, defaulting to jetto-pythontools internal config')
        with open(default_config_file, 'r') as read_file:
            config = json.load(read_file)
    if config is None:
        raise TypeError("JSP conversion config not defined! Aborting!")
    jsp_keymap = config.pop('jsp_keymap', {})
    jst_keymap = config.pop('jst_keymap', {})

    # Define the exfile structure, use user-defined base if provided
    exf = create_exfile_structure(jsp['DDA NAME'], int(jsp['SHOT']))
    ext = create_exfile_structure(jst['DDA NAME'], int(jst['SHOT']), extfile=True)

    time_basis = jsp['TIME'].flatten()
    if time_vector is not None:
        time_basis = np.array(time_vector)
    elif time_start is not None:
        if time_end is not None:
            time_mask = (time_vector >= time_start) & (time_vector <= time_end)
            time_basis = time_basis[time_mask]
        else:
            time_mask = (time_vector >= time_end)
            time_basis = time_basis[time_mask]
    elif time_end is not None:
        time_mask = (time_vector <= time_end)
        time_basis = time_basis[time_mask]
    else:
        time_basis = np.array([time_basis[-1]])
    jsp_idx_time = []
    jst_idx_time = []
    for time in time_basis:
        # TODO possibly change this to use built xarray nearest
        jsp_index = (np.abs(jsp['TIME'].flatten() - time)).argmin()
        jsp_idx_time.append(jsp_index)
        jst_index = (np.abs(jst['TVEC1'].flatten() - time)).argmin()
        jst_idx_time.append(jst_index)

    exf['XVEC1'] = copy.deepcopy(jsp['XVEC1'])
    exf['TVEC1'] = np.atleast_3d(time_basis)
    ext['TVEC1'] = np.atleast_3d(time_basis)

    profile_secnum = jsp['SECTIONS'].index('Profiles') + 1
    jsp_varlist = []
    for key in jsp['INFO']:
        if 'SECNUM' in jsp['INFO'][key] and jsp['INFO'][key]['SECNUM'] == profile_secnum:
            jsp_varlist.append(key)
    trace_secnum = jst['SECTIONS'].index('Traces') + 1
    jst_varlist = []
    for key in jst['INFO']:
        if 'SECNUM' in jst['INFO'][key] and jst['INFO'][key]['SECNUM'] == trace_secnum:
            jst_varlist.append(key)

    # Print out what has been added to the new EXFILE and units
    no_columns = 5
    columns = ["EXFILE VAR", "JSP VAR", "Description from EXFILE", "Description from JSP", "Units for EXFILE", "Units from JSP"]
    row_format = '{:<15}{:<10}{:<40}{:<40}{:<20}{:<20}'
    if verbosity >= 1:
        print("PROFILE WRITTEN TO NEW EXFILE FROM SPECIFIED JSP")
        print(row_format.format(*['='*15,'='*10,'='*40,'='*40,'='*20,'='*20]))
        print(row_format.format(*columns))
        print(row_format.format(*['='*15,'='*10,'='*40,'='*40,'='*20,'='*20]))

    for jsp_key in jsp_varlist:
        if jsp_key in jsp_keymap:
            ex_key = jsp_keymap[jsp_key]
            info_entry = generate_entry_info(ex_key, target='jsp')
            if info_entry is not None:
                new_data = copy.deepcopy(jsp[jsp_key][jsp_idx_time])
                if interpolate:
                    # Interpolate JSP x-vector into base EXFILE x-vector if provided
                    edge_values = (jsp[jsp_key].T[:, 0], jsp[jsp_key].T[:, -1])
                    ifunc = interp1d(jsp['TIME'].flatten(), jsp[jsp_key].T, kind='linear', bounds_error=False, fill_value=edge_values)
                    new_data = ifunc(exf['TVEC1'].flatten())
                exf[ex_key] = copy.deepcopy(new_data)
                # Provided required metadata and labels, if field is not already in EXFILE
                if 'INFO' in exf and ex_key not in exf['INFO']:
                    exf['INFO'][ex_key] = info_entry
                if verbosity >= 1:
                    print(
                        row_format.format(
                            ex_key, jsp_key, str(exf['INFO'][ex_key]['DESC']), str(jsp['INFO'][jsp_key]['DESC']), str(exf['INFO'][ex_key]['UNITS']), str(jsp['INFO'][jsp_key]['UNITS'])
                        )
                    )

    for jst_key in jst_varlist:
        if jst_key in jst_keymap:
            ex_key = jst_keymap[jst_key]
            info_entry = generate_entry_info(ex_key, target='jst')
            if info_entry is not None:
                new_data = copy.deepcopy(jst[jst_key][:, jst_idx_time])
                if interpolate:
                    # Interpolate JSP x-vector into base EXFILE x-vector if provided
                    edge_values = (jst[jst_key][:, 0], jst[jst_key][:, -1])
                    ifunc = interp1d(jst['TVEC1'].flatten(), jst[jst_key].T, kind='linear', bounds_error=False, fill_value=edge_values)
                    new_data = ifunc(ext['TVEC1'].flatten()).T
                ext[ex_key] = copy.deepcopy(new_data)
                # Provided required metadata and labels, if field is not already in EXFILE
                if 'INFO' in ext and ex_key not in ext['INFO']:
                    ext['INFO'][ex_key] = info_entry
                if verbosity >= 1:
                    print(
                        row_format.format(
                            ex_key, jst_key, str(ext['INFO'][ex_key]['DESC']), str(jst['INFO'][jst_key]['DESC']), str(ext['INFO'][ex_key]['UNITS']), str(jst['INFO'][jst_key]['UNITS'])
                        )
                    )

#   Removed since generalization would produce too many plots, perhaps a function to insert a single signal can be used
#    if plot_debug:
#        plot_profiles(exfile_struct[key][-1], jsp[jsp_key][idx_time], key)

    # Update the creation date and time
    today = datetime.today()
    DB_name_string = 'JSP2EX'
    exf['CREATION_DATE'] = today.strftime("%d/%m/%Y")
    exf['CREATION_TIME'] = today.strftime("%H:%M:%S")
    exf['DATABASE NAME'] = DB_name_string
    ext['CREATION_DATE'] = today.strftime("%d/%m/%Y")
    ext['CREATION_TIME'] = today.strftime("%H:%M:%S")
    ext['DATABASE NAME'] = DB_name_string

    return exf, ext


def extract_into_existing(jsp_dir, time_slices=None, time_range=None, user_config_path=None, base_exfile_struct=None, remove_excess=False, plot_debug=False, verbosity=2):
    """
    Desc - reads JETTO outputs (JSP and JST) and transfers the requested physics signals into a provided EXFILE, over writes existing signals and keeps the INFO section

    :param jsp_dir: path to JSP directory to be used, assumed to be named jetto.jsp in provided directory
    :param time_slices: array of times which the profiles should be read from the JSP as the nearest slices (takes precedence over time_range)
    :param time_range: array of length-2 which define the time window which the profiles should be read from the JSP
    :param user_config_path: optional path to configuration file specifying which fields to transfer
    :param base_exfile_struct: optional Python EXFILE structure on which modifications are made, a new structure is created if None is given
    :param remove_excess: optional flag to remove all unspecified data fields from EXFILE when base_exfile_struct is given
    :param plot_debug: debug output which allows plotting of the matched JSP signal on top the template EXFILE signals (not functional!)
    :param verbosity: set verbosity level for debugging

    :return: exfile_data - dictionary which contains the EXFILE data
    """

    # the JSP file read should throw an error is it doesn't exist
    jsp_path = Path(jsp_dir) / 'jetto.jsp'
    jsp = read_binary_file(jsp_path)
    jst_path = Path(jsp_dir) / 'jetto.jst'
    jst = read_binary_file(jst_path)

    time_start = None
    time_end = None
    time_vector = None
    if isinstance(time_slices, array_types):
        time_vector = [float(tt) for tt in time_slices]
    elif isinstance(time_slices, number_types):
        time_vector = [float(time_range)]
    elif isinstance(time_range, array_types):
        time_start = float(time_range[0]) if len(time_range) >= 1 and isinstance(time_range[0], number_types) else None
        time_end = float(time_range[1]) if len(time_range) >= 2 and isinstance(time_range[1], number_types) else None

    # Provides the mapping between EXFILE and JSP signals
    default_config_path = Path(__file__).resolve().parent / 'convert_jsp_to_exfile_config.json'
    json_config_file = Path(user_config_path) if user_config_path is not None else default_config_path
    config = None
    if json_config_file.is_file():
        with open(json_config_file, 'r') as read_file:
            config = json.load(read_file)
    else:
        print('User-defined config file not found, defaulting to jetto-pythontools internal config')
        with open(default_config_file, 'r') as read_file:
            config = json.load(read_file)
    if config is None:
        raise TypeError("JSP conversion config not defined! Aborting!")
    jsp_keymap = config.pop('jsp_keymap', {})
    jst_keymap = config.pop('jst_keymap', {})

    # Define the exfile structure, use user-defined base if provided
    fexternal = isinstance(base_exfile_struct, dict)
    exf = copy.deepcopy(base_exfile_struct) if fexternal else create_exfile_structure(jsp['DDA NAME'], int(jsp['SHOT']))
    ext = create_exfile_structure(jst['DDA NAME'], int(jst['SHOT']), extfile=True)

    base_idx_time = []
    if len(exf['TVEC1'].flatten()) > 0:
        for time in time_basis:
            # TODO possibly change this to use built xarray nearest
            index = (np.abs(exf['TVEC1'].flatten() - time)).argmin()
            base_idx_time.append(index)

    if len(exf['XVEC1']) != len(jsp['XVEC1']):
        finterp = True
    elif not np.all(np.isclose(exf['XVEC1'], jsp['XVEC1'])):
        finterp = True

    profile_secnum = jsp['SECTIONS'].index('Profiles') + 1
    jsp_varlist = []
    for key in jsp['INFO']:
        if 'SECNUM' in jsp['INFO'][key] and jsp['INFO'][key]['SECNUM'] == profile_secnum:
            jspvarlist.append(key)
    trace_secnum = jst['SECTIONS'].index('Traces') + 1
    jst_varlist = []
    for key in jst['INFO']:
        if 'SECNUM' in jst['INFO'][key] and jst['INFO'][key]['SECNUM'] == trace_secnum:
            jst_varlist.append(key)

    # Print out what has been added to the new EXFILE and units
    no_columns = 5
    columns = ["EXFILE VAR", "JSP VAR", "Description from EXFILE", "Description from JSP", "Units for EXFILE", "Units from JSP"]
    row_format = '{:<15}{:<10}{:<40}{:<40}{:<20}{:<20}'
    if verbosity >= 1:
        print("PROFILE WRITTEN TO NEW EXFILE FROM SPECIFIED JSP")
        print(row_format.format(*['='*15,'='*10,'='*40,'='*40,'='*20,'='*20]))
        print(row_format.format(*columns))
        print(row_format.format(*['='*15,'='*10,'='*40,'='*40,'='*20,'='*20]))

    keep_jsp_keys = config.pop('jsp_keep', [])   # Can provide list of variables in base EXFILE to keep, even if data is not replaced
    for jsp_key in jsp_varlist:
        if jsp_key in jsp_keymap:
            ex_key = keymap[jsp_key]
            info_entry = generate_entry_info(ex_key)
            if info_entry is not None:
                new_data = copy.deepcopy(jsp[jsp_key][idx_time])
                if finterp:
                    # Interpolate JSP x-vector into base EXFILE x-vector if provided
                    edge_values = (jsp[jsp_key][idx_time, 0], jsp[jsp_key][idx_time, -1])
                    ifunc = interp1d(jsp['XVEC1'].flatten(), jsp[jsp_key][idx_time], kind='linear', bounds_error=False, fill_value=edge_values)
                    new_data = ifunc(exfile_struct['XVEC1'].flatten())
                if fexternal:
                    # Paste appropriate JSP time slice data into base EXFILE if provided
                    exfile_struct[ex_key][base_idx_time] = new_data
                else:
                    exfile_struct[ex_key] = copy.deepcopy(new_data)
                # Records entries that have been modified by this loop
                if ex_key not in keep_jsp_keys:
                    keep_jsp_keys.append(ex_key)
                # Provided required metadata and labels, if field is not already in EXFILE
                if 'INFO' in exfile_struct and ex_key not in exfile_struct['INFO']:
                    exfile_struct['INFO'][ex_key] = info_entry
                if verbosity >= 1:
                    print(
                        row_format.format(
                            ex_key, jsp_key, str(exfile_struct['INFO'][ex_key]['DESC']),
                            str(jsp['INFO'][jsp_key]['DESC']), str(exfile_struct['INFO'][ex_key]['UNITS']),
                            str(jsp['INFO'][jsp_key]['UNITS'])
                        )
                    )

    keep_jst_keys = config.pop('jst_keep', [])   # Can provide list of variables in base EXFILE to keep, even if data is not replaced
    for jst_key in jst_varlist:
        if jst_key in jst_keymap:
            ex_key = keymap[jst_key]
            ex_key = jst_keymap[jst_key]
            info_entry = generate_entry_info(ex_key, target='jst')
            if info_entry is not None:
                new_data = copy.deepcopy(jst[jst_key][:, jst_idx_time])
                if interpolate:
                    # Interpolate JSP x-vector into base EXFILE x-vector if provided
                    edge_values = (jst[jst_key][:, 0], jst[jst_key][:, -1])
                    ifunc = interp1d(jst['TVEC1'].flatten(), jst[jst_key].T, kind='linear', bounds_error=False, fill_value=edge_values)
                    new_data = ifunc(ext['TVEC1'].flatten()).T
                if fexternal:
                    # Paste appropriate JSP time slice data into base EXFILE if provided
                    exfile_struct[ex_key][base_idx_time] = new_data
                else:
                    exfile_struct[ex_key] = copy.deepcopy(new_data)
                ext[ex_key] = copy.deepcopy(new_data)
                # Records entries that have been modified by this loop
                if ex_key not in keep_jst_keys:
                    keep_jst_keys.append(ex_key)
                # Provided required metadata and labels, if field is not already in EXFILE
                if 'INFO' in ext and ex_key not in ext['INFO']:
                    ext['INFO'][ex_key] = info_entry
                if verbosity >= 1:
                    print(
                        row_format.format(
                            ex_key, jst_key, str(ext['INFO'][ex_key]['DESC']), str(jst['INFO'][jst_key]['DESC']), str(ext['INFO'][ex_key]['UNITS']), str(jst['INFO'][jst_key]['UNITS'])
                        )
                    )

    # Removes all keys not modified by this routine - must be specified as argument (default: False)
    if fexternal and remove_excess:
        secnum = exfile_struct['SECTIONS'].index('Profiles')
        remove_keys = []
        for key in exfile_struct['INFO']:
            if exfile_struct['INFO'][key]['SECNUM'] == secnum and key not in keep_keys:
                remove_keys.append(key)
        for key in remove_keys:
            print('\nSignal present in original EXFILE ({exfile}) is not present in the JSP, and was requested to be removed.\n'.format(exfile=key))
            if key in exfile_struct:
                del exfile_struct[key]
            if 'INFO' in exfile_struct and key in exfile_struct['INFO']:
                del exfile_struct['INFO'][key]

#   Removed since generalization would produce too many plots, perhaps a function to insert a single signal can be used
#    if plot_debug:
#        plot_profiles(exfile_struct[key][-1], jsp[jsp_key][idx_time], key)

    # Update the creation date and time
    today = datetime.today()
    exfile_struct['CREATION_DATE'] = today.strftime("%d/%m/%Y")
    exfile_struct['CREATION_TIME'] = today.strftime("%H:%M:%S")
    DB_name_string = 'JSP2EX'
    exfile_struct['DATABASE NAME'] = DB_name_string

    return exfile_struct

def convert(jsp_dir, time_range=None, time_slices=None, num_points=None, user_config_path=None, orig_exfile_path=None, remove_excess=False, verbosity=2):
    """
    Desc - reads JSP physics signals and writes it into a new EXFILE structure, populating the INFO sections,
           then returns the EXFILE structure. Option to write data on top of a template EXFILE (not tested)

    :param jsp_dir: path to JSP directory to be used as input, assumed to be named jetto.jsp in the provided directory
    :param time_range: array of length-2 which define the time window which the profiles should be read from the JSP (takes precedence over time_slices)
    :param time_slices: array of times which the profiles should be read from the JSP as the nearest slices
    :param num_points: number of evenly spaced points for interpolation in time window (including endpoints)
    :param user_config_path: optional path to configuration file specifying which fields to transfer
    :param orig_exfile_path: optional path to base EXFILE for pasting of JSP data (takes precedence over num_points)
    :param remove_excess: optional flag to remove all unspecified data fields from EXFILE when orig_exfile_path is given
    :param verbosity: set verbosity level for debugging

    :return: exfile_data, extfile_data - dictionaries containing requested EXFILE data and corresponding time trace data
    """

    base_exfile_data = None
    if orig_exfile_path is not None:
        base_exfile_path = Path(orig_exfile_path)
        if base_exfile_path.is_file():
            base_exfile_data = read_binary_file(base_exfile_path)

    if isinstance(time_range, array_types):
        time_slices = None
        if base_exfile_data is None and isinstance(num_points, int) and len(time_range) >= 2 and isinstance(time_range[0], number_types) and isinstance(time_range[1], number_types):
            time_slices = np.linspace(time_range[0], time_range[1], num_points)
            time_range = None

    exfile_data, extfile_data = extract_as_new(
        jsp_dir,
        time_slices=time_slices,
        time_range=time_range,
        user_config_path=user_config_path,
        #base_exfile_struct=base_exfile_data,
        #remove_excess=remove_excess,
        verbosity=verbosity
    )

    return exfile_data, extfile_data

def convert_and_write(exfile_path, new_exfile_name, jsp_dir, time_range=None, time_slices=None, num_points=None, user_config_path=None, orig_exfile_path=None, remove_excess=False, verbosity=2):
    """
    Desc - reads JSP physics signals and writes it into a new EXFILE structure, populating the INFO sections,
           then writes that new EXFILE structure out. Option to write data on top of a template EXFILE (not tested)

    :param exfile_path: path to directory for new exfile output
    :param new_exfile_name: name of the new exfile to be written
    :param jsp_dir: path to JSP directory to be used as input, assumed to be named jetto.jsp in the provided directory
    :param time_range: array of length-2 which define the time window which the profiles should be read from the JSP (takes precedence over time_slices)
    :param time_slices: array of times which the profiles should be read from the JSP as the nearest slices
    :param num_points: number of evenly spaced points for interpolation in time window (including endpoints)
    :param user_config_path: optional path to configuration file specifying which fields to transfer
    :param orig_exfile_path: optional path to base EXFILE for pasting of JSP data (takes precedence over num_points)
    :param remove_excess: optional flag to remove all unspecified data fields from EXFILE when orig_exfile_path is given
    :param verbosity: set verbosity level for debugging

    :return: status - return from write_binary_exfile 0 - written other - failed
    """

    # Check if new EXFILE already exists
    status = 1
    output_exfile_path = Path(exfile_path)
    output_exfile_name = new_exfile_name
    fextension = True
    while fextension:
        if output_exfile_name.endswith('.ex'):
            output_exfile_name = output_exfile_name[:-3]
        elif output_exfile_name.endswith('.ext'):
            output_exfile_name = output_exfile_name[:-4]
        else:
            fextension = False
    output_base = output_exfile_path / output_exfile_name

    if output_exfile_path.is_dir():
        exfile_data, extfile_data = convert(
            jsp_dir,
            time_range=time_range,
            time_slices=time_slices,
            num_points=num_points,
            user_config_path=user_config_path,
            orig_exfile_path=orig_exfile_path,
            remove_excess=remove_excess,
            verbosity=verbosity
        )
        status_jsp = write_binary_exfile(exfile_data, output_file=str(output_base))
        status_jst = write_binary_exfile(extfile_data, output_file=str(output_base))
        status = status_jsp + status_jst
    else:
        print('Cannot find target directory for EXFILE write - {path}'.format(path=str(output_exfile_path)))

    return status

