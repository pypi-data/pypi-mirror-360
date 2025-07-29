#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 14:26:17 2023

@author: zstancar

PURPOSE: reads in sequence of COCONUT/JETTO outputs and writes
time-dependent boundary condition files for JETTO input. Uses Savitzky-Golay
smoothing, linearly interpolates on a linear time vector of choice. If time
vector of JETTO simulation using boundary condition is longer than the time
interval of input simulations, the beginning and end smoothed boundary values
are used to fill the time array and are kept constant.
NOTE: the combination of run paths defined in jetto_output_finder function and
defined in list run might need to be changed depending on which cluster you use
the script on.
In addition more boundary condition quantities can be added in a similar manner.

INPUTS:
    run: list; list of string run paths
    plot: bool; switch for plotting
    boundary: dictionary; boundary variable names with bool switch for writing output,
              pointer to constructed values array, output file type, plot labels
    time_jetto: array; Define time interval of JETTO simulation that will be
                run with this boundary condition
    smoothing_window: int; Savitzky-Golay smoothing window
    smoothing_order: int; Savitzky-Golay smoothing order
    interp_step_num: int;Equidistant time grid for boundary file interpolation
    target_directory: str; path to output directory
    time_shift: float; Time delay to boundary file if reference simulation is not using same time vector (seconds)
OUTPUT:
    written set of boundary files in target directory
"""
 
import matplotlib.pyplot as plt
import numpy as np
from jetto_tools import binary
import os
from scipy import interpolate
 
################################ JETTO OUTPUT FIND FUNCTION
 
def jetto_output_finder(runid):
    jsp_tmp = []
    jst_tmp = []
    paths = '/home/' + runid
    if os.path.exists(paths+'/jetto.jsp') \
        and os.path.exists(paths+'/jetto.jst'):
        print(f'Run {runid} found in catalogue\n')
        jsp_tmp = binary.read_binary_file(paths+'/jetto.jsp')
        jst_tmp = binary.read_binary_file(paths+'/jetto.jst')
    else:
        print(f'Run {runid} does not exist\n')
    return jsp_tmp, jst_tmp

################################ SMOOTHING FUNCTION

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    from math import factorial
    
    window_size = np.abs(np.int(window_size))
    order = np.abs(np.int(order))
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

################################ READ JETTO OUTPUT & EQUILIBRIUM

plot = True # Plot summary of interpolation?

run = ['list_of_string_paths'] # Location of jetto.jst and jetto.jsp files
 
# Read profiles
jsp = {}
jsp_rho = {}
jsp_time = {}
jst = {}
NIH = {}
TE = {}
TI = {}

TIME = np.array([])
NIB = np.array([])
TEB = np.array([])
TIB = np.array([])

for i, runid in enumerate(run):
    jsp[runid], jst[runid] = jetto_output_finder(runid)
    # PROFILES
    jsp_rho[runid] = jsp[runid]['XVEC1'][0,:]
    jsp_time[runid] = jsp[runid]['TIME'][:,0,0]
    TIME=np.append(TIME,jsp_time[runid])
    NIH[runid] = jsp[runid]['NI']
    NIB=np.append(NIB,NIH[runid][:,-1])
    TE[runid] = jsp[runid]['TE']
    TEB=np.append(TEB,TE[runid][:,-1])
    TI[runid] = jsp[runid]['TI']
    TIB=np.append(TIB,TI[runid][:,-1])

TIME_sort = np.argsort(TIME)

boundary = {'NI' : [True,NIB,'ni1p','m$^{-3}$'], # Which boundary files are you writing?
            'TE' : [True,TEB,'tep','eV'],
            'TI' : [True,TIB,'tip','eV']}
time_jetto = ([275.0, 285.0])
smoothing_window = 3
smoothing_order = 3
interp_step_num = 15
target_directory = 'path_to_output_files'
time_shift = -2.5

# Looping over boundary constrained parameters and writing output files
for bound in boundary:
    if boundary[bound][0]:
        smooth = savitzky_golay(boundary[bound][1][TIME_sort],
                                int(len(TIME[TIME_sort])/smoothing_window),
                                smoothing_order)
        interp = interpolate.interp1d(TIME[TIME_sort],smooth,
                                bounds_error=False,
                                fill_value=(smooth[0],smooth[-1]))
        interp_time = np.linspace(np.min(time_jetto)-time_shift,
                                  np.max(time_jetto)-time_shift,
                                  num=interp_step_num, endpoint=True)
        interp_array = interp(interp_time)
        out=open(target_directory+f'{bound}.{boundary[bound][2]}','w')
        for j in range(len(interp_array)):
            out.write(
                    f'{interp_time[j]+time_shift:.3f} {interp_array[j]:.3f}\n'
                    )
        out.close()
        
        if plot:
            plt.figure()
            plt.plot(TIME[TIME_sort]+time_shift,boundary[bound][1][TIME_sort],
                     color='r',label='simulation')
            plt.plot(TIME[TIME_sort]+time_shift,smooth,
                     color='b',label='smoothing')
            plt.plot(interp_time+time_shift,interp_array,
                     color='g',label=f'interpolation #{interp_step_num}')
            plt.xlabel('Time [s]')
            plt.ylabel(fr'{bound} [{boundary[bound][3]}]')
            plt.xlim(time_jetto)
            plt.title(f'Time shift = {time_shift}s')
            plt.legend()