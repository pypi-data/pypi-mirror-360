#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 23 15:48:08 2023

@author: zstancar

PURPOSE: reads in JETTO profile jetto.jsp output and replaces the existing
time vectors entries of a selected exfile (only non-zero exfile variables) with
the profiles at the last-time point of the selected JETTO run. Linearly
interpolated on exfile grid.
NOTE: Reads the defined exfile and JETTO output directly, does not check if
files exist, can be added.

INPUTS:
    exfiles: list; string exfile paths, needed to copy format
    newexfiles: list; string exfile paths for files to be created
    jetto: list: string COCONUT/JETTO JSP output paths for extracting desired profiles
    plot: bool; switch for plotting
    vars_remove: list; exfile variables that we wish to preserve
OUTPUT:
    written exfile with updated profiles in target directory
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from jetto_tools import binary
import math
from scipy import interpolate

plot = True # Plot summary of interpolation?

# Location of jetto.ex files
exfiles = ['path_to_format_exfile']
newexfiles = ['path_to_output_new_exfile']
jetto = ['path_to_JETTO_jsp_output']

################ READING EXFILE AND REPLACING VECTORS WITH JSP END-POINT

vars_remove = ['XRHO','R','XVEC1','TVEC1','RA','SPSI','PSI','RHO']

exdata = {}
exdata_allvars = []
for ex in exfiles:
    exdata[ex] = binary.read_binary_file(ex) #binary.write_binary_exfile
    exdata[ex]['variables'] = []
    for i, var in enumerate(exdata[ex]):
        exdata[ex]['variables'].append(var)
    info_index = exdata[ex]['variables'].index('DDA NAME')
    exdata_allvars.extend(exdata[ex]['variables'][info_index+1:-1])
exdata_allvars =  list(set(exdata_allvars))

for i in vars_remove:
    if i in exdata_allvars:
        exdata_allvars.remove(i)

exdata_allvars_nonzero = np.zeros((len(exdata_allvars), len(exfiles)),
                                  dtype=int)
jsp = {}
for runid in jetto:
    jsp[runid] = binary.read_binary_file(runid)
    for k, var in enumerate(exdata_allvars):
        for i, ex in enumerate(exfiles):
            if exdata[ex][var].any():
                exdata_allvars_nonzero[k][i] = int(1)
        for i, ex in enumerate(exfiles):
            if exdata_allvars_nonzero[k].any():
                var_tmp = interpolate.interp1d(
                        jsp[runid]['XVEC1'][-1,:],jsp[runid][var][-1,:],
                        kind='linear', fill_value='extrapolate')
                for t in range(len(exdata[ex]['TVEC1'])):
                    exdata[ex][var][t] = var_tmp(exdata[ex]['XVEC1'][0,:])

for i, ex in enumerate(exfiles):
    tmp_exdata = exdata[ex]
    del tmp_exdata['variables']
    binary.write_binary_exfile(tmp_exdata,newexfiles[i])

################ PLOTTING
if plot:
    newexdata = binary.read_binary_file(newexfiles[0])
    
    for k, var in enumerate(exdata_allvars):
        if exdata_allvars_nonzero[k].any():
            fig = plt.figure()
            fig.subplots_adjust(wspace=0.4)
            for i, ex in enumerate(exfiles):
                ax = fig.add_subplot(math.ceil(len(exfiles)/2), 2, i+1)
                ax.plot(jsp[runid]['XVEC1'][-1,:],
                        jsp[runid][var][-1,:], label='JETTO')
                for t in range(len(newexdata['TVEC1'])):
                    ax.plot(newexdata['XVEC1'][0], newexdata[var][t],
                            label=str(float(newexdata['TVEC1'][t]))+' s')
                    ax.set_xlabel(r'$\rho_{tor}$ []')
                if i == 0:
                    ax.set_title(newexdata['INFO'][var]['DESC'], fontsize=11)
                    ax.set_ylabel(newexdata['INFO'][var]['LABEL']+' ['+
                                  ('-' if newexdata['INFO'][var]['UNITS'] is None
                                   else newexdata['INFO'][var]['UNITS'])+']')
                    ax.legend()