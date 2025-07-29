from pathlib import Path
import logging

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

import jetto_tools.setup_logging  # noqa: F401 Import with side effects
from jetto_tools.classes import JETTO, OODS
from jetto_tools.results_gui import run_list_to_runs, slice_plotter, uid_to_pretty

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    import pyuda
except ImportError:
    logger.warning("Python module 'pyuda' not found. Submodule 'mast_jetto_tools' needs it")
    raise

from IPython import embed


class MastJetto:
    def __init__(self,shot=None,time=None,file=None):
        self.jetto_load  = False
        self.mast_load = False
        if file is not None:
            self.load_jetto(file)
        if shot is not None:
            self.load_shot(shot)
        self.time = time
        
    def load_jetto(self,file):
        run_list=[file]
        self.runs = run_list_to_runs(run_list)
        self.jetto_load=True
        
    def load_shot(self,shot):


        client = pyuda.Client()
        # Thomson scattering
        temp = client.get('ayc_te',shot)        
        dens = client.get('ayc_ne',shot)        
        rmaj = client.get('ayc_r',shot)        
        core = client.get('ayc_te_core',shot)        
        self.ayc = {"Te":temp.data,
                    "ne":dens.data,
                    "time":temp.time.data,
                    "rmaj":rmaj.data,
                    "Teax":core.data}
        
        #Plasma current
        curr = client.get('efm_plasma_curr(x)',shot)
        self.ip = {"Ip":curr.data,
                   "time":curr.time.data}

       # CXRS temperature
        cxrs = client.get("act_ss_temperature",shot)
        self.cxrs = {"Ti":cxrs.data,
                     "rmaj":cxrs.dims[1].data,
                     "time":cxrs.time.data}
        self.mast_load = True
        
    def plot_trace(self):
        if self.jetto_load and self.mast_load:
            file='JST'
            fig,axes = plt.subplots(2)
            ax0,ax1 = axes
            xvar='time'
            for ax,yvar in zip(axes,['TEAX','CUR']):
                slice_plotter(ax,None,self.runs,file,xvar,yvar,verbosity=1)
                if yvar == 'TEAX':
                    ax.plot(self.ayc['time'],self.ayc['Teax'],label='MAST')
                if yvar == 'CUR':
                    ax.plot(self.ip['time'],self.ip['Ip'],label='MAST')

                ax.legend()

            plt.show()
           

    def plot_profile(self,time=None):
        if time is None:
            time = self.time
            
        if self.jetto_load and self.mast_load:
            file='JSP'
            fig,axes = plt.subplots(3)
            ax0,ax1,ax2 = axes
            xvar='R'
            tidx_ayc = np.abs(self.ayc['time'] - time).argmin()
            tidx_cxr = np.abs(self.cxrs['time'] - time).argmin()
            labels = []
            for run_uid in self.runs.keys():
                pretty = uid_to_pretty(run_uid)
                pretty += f' t={time}'
                labels.append(pretty)
            for ax,yvar in zip(axes,['TE','NE','TI']):
                slice_plotter(ax,None,self.runs,file,xvar,yvar,zslice=('time',time),verbosity=1, line_labels=labels)
                if yvar == 'NE':
                    ax.plot(self.ayc['rmaj'][tidx_ayc,:],self.ayc['ne'][tidx_ayc,:],label='MAST t='+str(self.ayc['time'][tidx_ayc]))
                if yvar == 'TE':
                    ax.plot(self.ayc['rmaj'][tidx_ayc,:],self.ayc['Te'][tidx_ayc,:],label='MAST t='+str(self.ayc['time'][tidx_ayc]))
                if yvar == 'TI':
                    ax.plot(self.cxrs['rmaj'],self.cxrs['Ti'][tidx_cxr,:],label='MAST t='+str(self.ayc['time'][tidx_ayc]))
                ax.legend()

            plt.show()

            
