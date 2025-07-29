import datetime
import matplotlib
import matplotlib.pyplot           as plt
import matplotlib.figure           as matfigure
import matplotlib.axes             as mataxes
import matplotlib.patches          as mpatches
import numpy                       as np
import plotly.plotly               as py
import plotly.graph_objs           as go
import os
import pickle
import math

from matplotlib                    import gridspec, cycler
from matplotlib.colors             import BoundaryNorm
from matplotlib.ticker             import MaxNLocator
from matplotlib.widgets            import Button
from matplotlib.transforms         import Bbox
from mpl_toolkits.mplot3d          import Axes3D
from pylab                         import *
from scipy.optimize                import curve_fit
from scipy.interpolate             import interp1d
from scipy.interpolate             import UnivariateSpline
from scipy.ndimage.filters         import gaussian_filter
from matplotlib                    import cm
from mpl_toolkits.mplot3d          import Axes3D
from plot_data                     import *
from plotly.tools                  import FigureFactory  as  FF
from discrete_slider import DiscreteSlider

from jetto_analysis_functions      import *


# Plot profiles (first identifier determines x- & y-label)
# mult and divide probably do the same thing. Should correct
def plot_gam_ome_slice_rho(username, run_name, gam_or_ome = 'gam', rho_min = 0, rho_max = 1, time_min = 0, time_max = 100, catalogued = False, fontx = 12, fonty = 12):

    # Read data
    if catalogued:
        path = run_name
    else:
        path = "/common/cmg/" + username + "/jetto/runs/" + run_name + "/"

    if catalogued:
        if gam_or_ome == 'gam':
            gam_GB = np.loadtxt(path + 'gam_GB.qlk.gz')
        if gam_or_ome == 'ome':
            gam_GB = np.loadtxt(path + 'ome_GB.qlk.gz')
    else:
        if gam_or_ome == 'gam':
            gam_GB = np.loadtxt(path + 'gam_GB.qlk')
        if gam_or_ome == 'ome':
            gam_GB = np.loadtxt(path + 'ome_GB.qlk')


    dimn = int(np.loadtxt(path + 'dimn.qlk'))
    dimx = int(np.loadtxt(path + 'dimx.qlk'))
    numsols = int(np.loadtxt(path + 'numsols.qlk'))
    ktheta = np.loadtxt(path + 'kthetarhos.qlk')
    rho = np.loadtxt(path + 'rho.qlk')

    file_object  = open(path + 'jetto.out', 'r')
    times = []
    delta_ts = []

    previous_line = []
    bad_lines_mask = []

#   read reverse to clean the times when Jetto for some reason repeats the step

    for line in reversed(list(file_object)):
        if line[0:5] == ' STEP' and line[7:13] != previous_line[7:13]:
            bad_lines_mask.append(True)
            times.append(float(line[20:28]))
            delta_ts.append(float(line[33:41]))
            previous_line = line
        else:
            if line[0:5] == ' STEP':
                bad_lines_mask.append(False)

    times.reverse()
    delta_ts.reverse()
    bad_lines_mask.reverse()

#   if the times are the same in the file look at the timestep to sum them up

    file_object.close()

    sum_delta_t = 0
    start_time = 100

    for index in range(1, len(times)-1):
        if times[index-1] == times[index] or times[index] == start_time:
            if times[index-1] == times[index]:
                start_time = times[index-1]

            sum_delta_t = sum_delta_t + delta_ts[index]
            times[index] = start_time + sum_delta_t
        if times[index+1] != start_time:
            sum_delta_t = 0

#   add a time in between every two QLK times.

    times_double = []

    for time_index, time in enumerate(times):
        times_double.append(time)
        try:
            times_double.append(times[time_index] + (times[time_index+1]-times[time_index])/2)
        except IndexError:
            times_double.append(times[time_index] + (times[time_index]-times[time_index-1])/2)


#   delete bad gammas and reorganize

    mask = []

    for mask_index, single_mask in enumerate(bad_lines_mask):
        if single_mask == True:
            for sol in range(numsols):
                for xrho in range(dimx):
                    for i in range(2):
                        mask.append(True)
        else:
            for sol in range(numsols):
                for xrho in range(dimx):
                    for i in range(2):
                        mask.append(False)


    gam_GB = gam_GB[mask]
    gam_GB = gam_GB.reshape([len(times)*2, numsols, dimx, dimn])
            

#   there is still some machine level error in the rounding and the array is not monotone. Will just force it.

    times = np.sort(times_double)
    rho_min_index = min(range(len(rho)), key = lambda i: abs(rho[i]-rho_min))
    rho_max_index = min(range(len(rho)), key = lambda i: abs(rho[i]-rho_max))

    time_min_index = min(range(len(times)), key = lambda i: abs(times[i]-time_min))
    time_max_index = min(range(len(times)), key = lambda i: abs(times[i]-time_max))

    rho = rho[rho_min_index:(rho_max_index+1)]
    times = times[time_min_index:time_max_index]
    gam_GB = gam_GB[time_min_index:time_max_index,:,rho_min_index:(rho_max_index+1),:]


    fig = plt.figure()

    def full_extent(axis, pad = 0.0):

        items = axis.get_xticklabels() + axis.get_yticklabels()
        items += [axis, axis.xaxis.label, axis.yaxis.label]
        bbox = Bbox.union([item.get_window_extent() for item in items])

        return bbox.expanded(1.0 + pad, 1.0 + pad)

    def join_double_axis(axis1, axis2, pad = 0.0):

        items_pre_filter, items = axis1.get_xticklabels() + axis1.get_yticklabels() + axis2.get_xticklabels() + axis2.get_yticklabels(), []

        for item in items_pre_filter:
            if all([i >= 0 for i in np.array((item.get_window_extent().get_points())).flatten().tolist()]):
                items.append(item)

        items += [axis1, axis1.xaxis.label, axis1.yaxis.label, axis2, axis2.xaxis.label, axis2.yaxis.label]

        bbox = Bbox.union([item.get_window_extent() for item in items])

        return bbox.expanded(1.0 + pad, 1.0 + pad)

    def join_quadruple_axis(axis1, axis2, axis3, axis4, pad = 0.0):

        items_pre_filter, items = axis1.get_xticklabels() + axis1.get_yticklabels() + axis2.get_xticklabels() + axis2.get_yticklabels() + axis3.get_xticklabels() + axis3.get_yticklabels() + axis4.get_xticklabels() + axis4.get_yticklabels(), []

        for item in items_pre_filter:
            if all([i >= 0 for i in np.array((item.get_window_extent().get_points())).flatten().tolist()]):
                items.append(item)

        items += [axis1, axis1.xaxis.label, axis1.yaxis.label, axis2, axis2.xaxis.label, axis2.yaxis.label, axis3, axis3.xaxis.label, axis3.yaxis.label, axis4, axis4.xaxis.label, axis4.yaxis.label]

        bbox = Bbox.union([item.get_window_extent() for item in items])

        return bbox.expanded(1.0 + pad, 1.0 + pad)



    class TurbFigure:

        gs = gridspec.GridSpec(16, 21, wspace=0.5, hspace=0.05, left=0.05, right=0.95, bottom=0.05, top=0.95)
        axes = {
            'turb ITG': plt.subplot(gs[2:-3,2:9]),
                'colorbar ITG': plt.subplot(gs[2:-3,9]),
            'turb ETG' : plt.subplot(gs[2:-3,13:-1]),
                'colorbar ETG': plt.subplot(gs[2:-3,-1]),
            'slide time button': plt.subplot(gs[0,:2]),
            'slide ktheta button': plt.subplot(gs[0,3:5]),
            'slide rho button': plt.subplot(gs[0,6:8]),
            'change figure': plt.subplot(gs[0,9:11]),
            'smooth data': plt.subplot(gs[0,12:14]),
            'save figure': plt.subplot(gs[0,16:18]),
            'save figure ITG': plt.subplot(gs[0,15:16]),
            'save figure ETG': plt.subplot(gs[0,18:19]),
            'slider': plt.subplot(gs[-1,:-1])
        }

        def __init__(self, fig, ktheta, rho, times, gam_GB, fontx, fonty):

            self.ktheta = ktheta
            self.rho = rho
            self.times = times
            self.gam_GB = copy(gam_GB)
            self.gam_GB_unsmoothed = copy(gam_GB)
            self.smoothed_data = False
            self.val_rho = rho[0]
            self.val_time = times[0]
            self.val_ktheta = ktheta[0]
            self.fig = fig


            self.fugure3d, self.sliding_rho, self.sliding_ktheta, self.sliding_time = False, True, False, False

            self.y = self.ktheta
            self.ITG_ETG = min(range(len(self.y)), key = lambda i: abs(self.ktheta[i]-1))

            self.y_ITG = self.y[0:self.ITG_ETG]
            self.y_ETG = self.y[self.ITG_ETG:-1]
 
            self.z_ITG = self.gam_GB[:,0,0,0:self.ITG_ETG]
            self.z_ETG = self.gam_GB[:,0,0,self.ITG_ETG:-1]

            self.cmap = cm.get_cmap('plasma', 256)

            # add levels and norm with ITG and ETG

            self.levels_ITG = MaxNLocator(nbins=20).tick_values(self.z_ITG.min(), self.z_ITG.max())
            self.levels_ETG = MaxNLocator(nbins=20).tick_values(self.z_ETG.min(), self.z_ETG.max())
            self.norm_ITG = BoundaryNorm(self.levels_ITG, ncolors=self.cmap.N)
            self.norm_ETG = BoundaryNorm(self.levels_ETG, ncolors=self.cmap.N, clip=True)

            self.countour_axis_ITG = self.axes['turb ITG']
            self.countour_axis_ETG = self.axes['turb ETG']
            self.countour_axis_ITG.set_xlabel(r'$ k_{\theta} $ [-]', fontsize = fontx)
            self.countour_axis_ITG.set_ylabel(r'time [s]', fontsize = fonty)
            self.countour_axis_ETG.set_xlabel(r'$ k_{\theta} $ [-]', fontsize = fontx)
            self.countour_axis_ETG.set_ylabel(r'time [s]', fontsize = fonty)

            self.cf_ITG = self.countour_axis_ITG.contourf(self.y_ITG, self.times, self.z_ITG, cmap=self.cmap, levels = self.levels_ITG)
            self.cf_ETG = self.countour_axis_ETG.contourf(self.y_ETG, self.times, self.z_ETG, cmap=self.cmap, levels = self.levels_ETG)

            self.cb_ITG = fig.colorbar(self.cf_ITG, norm = self.norm_ITG, cax = self.axes['colorbar ITG'], cmap = self.cmap, values = self.levels_ETG)
            self.cb_ETG = fig.colorbar(self.cf_ETG, norm = self.norm_ETG, cax = self.axes['colorbar ETG'], cmap = self.cmap, values = self.levels_ETG)

            # Initialize dimx slider

            self.slider_axis = self.axes['slider']
            self.slider = DiscreteSlider(self.slider_axis, 'dimx', rho[0], rho[-1], allowed_vals=rho, valinit=rho[0])
            self.slide = self.slider.on_changed(self.update_grow_rho)


            # Using the double layer of save buttons could be possible redifining the gs subplots. Do it at some points when I have some time


        def slide_time(self):

            current = copy(self.sliding_time)
            self.sliding_rho, self.sliding_ktheta, self.sliding_time = False, False, True

            self.axes['turb ITG'] = plt.subplot(self.gs[2:-3,2:9])
            self.axes['colorbar ITG'] = plt.subplot(self.gs[2:-3,9])
            self.axes['turb ETG'] = plt.subplot(self.gs[2:-3,13:-1])
            self.axes['colorbar ETG'] = plt.subplot(self.gs[2:-3,-1])

            self.y = self.ktheta

            self.ITG_ETG = min(range(len(self.y)), key = lambda i: abs(ktheta[i]-1))

            self.z_ITG = self.gam_GB[0,0,:,0:self.ITG_ETG]
            self.z_ETG = self.gam_GB[0,0,:,self.ITG_ETG:-1]

            self.y_ITG = self.y[0:self.ITG_ETG]
            self.y_ETG = self.y[self.ITG_ETG:-1]

            # add levels and norm with ITG and ETG

            self.levels_ITG = MaxNLocator(nbins=20).tick_values(self.z_ITG.min(), self.z_ITG.max())
            self.levels_ETG = MaxNLocator(nbins=20).tick_values(self.z_ETG.min(), self.z_ETG.max())
            self.norm_ITG = BoundaryNorm(self.levels_ITG, ncolors=self.cmap.N, clip=True)
            self.norm_ETG = BoundaryNorm(self.levels_ETG, ncolors=self.cmap.N, clip=True)

            self.axes['colorbar ETG'].cla()
            self.axes['colorbar ITG'].cla()

            self.countour_axis_ITG = self.axes['turb ITG']
            self.countour_axis_ETG = self.axes['turb ETG']

            self.countour_axis_ITG.cla()
            self.countour_axis_ETG.cla()

            if self.fugure3d == False:

                self.countour_axis_ITG = self.axes['turb ITG']
                self.countour_axis_ETG = self.axes['turb ETG']

                self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:9])
                self.countour_axis_ETG = fig.add_subplot(self.gs[2:-3,13:-1])

                self.cf_ITG = self.countour_axis_ITG.contourf(self.y_ITG, self.rho, self.z_ITG, cmap=self.cmap, levels = self.levels_ITG)
                self.cf_ETG = self.countour_axis_ETG.contourf(self.y_ETG, self.rho, self.z_ETG, cmap=self.cmap, levels = self.levels_ETG)

            else:

                 self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:9], projection = '3d')
                 self.countour_axis_ETG = fig.add_subplot(self.gs[2:-3,13:-1], projection = '3d')

                 x_ITG, y_ITG = np.meshgrid(self.y_ITG, self.rho)
                 x_ETG, y_ETG = np.meshgrid(self.y_ETG, self.rho)

                 self.cf_ITG = self.countour_axis_ITG.plot_surface(y_ITG, x_ITG, self.z_ITG, cmap=self.cmap)
                 self.cf_ETG = self.countour_axis_ETG.plot_surface(y_ETG, x_ETG, self.z_ETG, cmap=self.cmap)

            self.countour_axis_ITG.set_xlabel(r'$ \rho $ [-]', fontsize = fontx)
            self.countour_axis_ITG.set_ylabel(r'$ k_{\theta} $ [-]', fontsize = fonty)
            self.countour_axis_ETG.set_xlabel(r'$ \rho $ [-]', fontsize = fontx)
            self.countour_axis_ETG.set_ylabel(r'$ k_{\theta} $ [-]', fontsize = fonty)

            self.cb_ITG = fig.colorbar(self.cf_ITG, norm = self.norm_ITG, cax = self.axes['colorbar ITG'], cmap = self.cmap, values = self.levels_ETG)
            self.cb_ETG = fig.colorbar(self.cf_ETG, norm = self.norm_ETG, cax = self.axes['colorbar ETG'], cmap = self.cmap, values = self.levels_ETG)

            self.slider_axis = self.axes['slider']
            if current != self.sliding_time:
                self.slider_axis.clear()
                self.slider.disconnect(self.slide)
                self.slider = DiscreteSlider(self.slider_axis, 'time', times[0], times[-1], allowed_vals=times, valinit=times[0])
            else:
                self.update_grow_time(self.val_time)

            self.slide = self.slider.on_changed(self.update_grow_time)

#            fig.canvas.draw_idle()
            self.fig.canvas.draw_idle()

        def slide_ktheta(self):

            current = copy(self.sliding_ktheta)
            self.sliding_rho, self.sliding_ktheta, self.sliding_time = False, True, False

            self.axes['turb ITG'] = plt.subplot(self.gs[2:-3,2:-1])
            self.axes['colorbar ITG'] = plt.subplot(self.gs[2:-3,-1])

            self.y = self.rho

            self.z_ITG = self.gam_GB[:,0,:,0]

            # add levels and norm with ITG and ETG

            self.levels_ITG = MaxNLocator(nbins=20).tick_values(self.z_ITG.min(), self.z_ITG.max())
            self.norm_ITG = BoundaryNorm(self.levels_ITG, ncolors=self.cmap.N, clip=True)

            self.axes['colorbar ITG'].cla()

            self.countour_axis_ITG = self.axes['turb ITG']
            self.countour_axis_ITG.set_xlabel(r'time [s]', fontsize = fontx)
            self.countour_axis_ITG.set_ylabel(r'$ \rho $ [-]', fontsize = fonty)
 
            self.countour_axis_ITG.cla()

            if self.fugure3d == False:

                self.countour_axis_ITG = self.axes['turb ITG']
                self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:-1])
                self.cf_ITG = self.countour_axis_ITG.contourf(self.y, self.times, self.z_ITG, cmap=self.cmap, levels = self.levels_ITG)

            else:

                 self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:-1], projection = '3d')
                 x_ITG, y_ITG = np.meshgrid(self.y, self.times)
                 self.cf_ITG = self.countour_axis_ITG.plot_surface(y_ITG, x_ITG, self.z_ITG, cmap=self.cmap)

            self.cb_ITG = fig.colorbar(self.cf_ITG, norm = self.norm_ITG, cax = self.axes['colorbar ITG'], cmap = self.cmap, values = self.levels_ITG)

            self.slider_axis = self.axes['slider']
            if current != self.sliding_ktheta:
                self.slider_axis.clear()
                self.slider.disconnect(self.slide)
                self.slider = DiscreteSlider(self.slider_axis, 'ktheta', ktheta[0], ktheta[-1], allowed_vals=ktheta, valinit=ktheta[0])

            self.update_grow_ktheta(self.val_ktheta)
            self.slide = self.slider.on_changed(self.update_grow_ktheta)

            self.fig.canvas.draw_idle()
#            fig.canvas.draw_idle()

        def slide_rho(self):

            current = copy(self.sliding_rho)
            self.sliding_rho, self.sliding_ktheta, self.sliding_time = True, False, False

            self.axes['turb ITG'] = plt.subplot(self.gs[2:-3,2:9])
            self.axes['colorbar ITG'] = plt.subplot(self.gs[2:-3,9])
            self.axes['turb ETG'] = plt.subplot(self.gs[2:-3,13:-1])
            self.axes['colorbar ETG'] = plt.subplot(self.gs[2:-3,-1])

            self.y = self.ktheta

            self.ITG_ETG = min(range(len(self.y)), key = lambda i: abs(ktheta[i]-1))

            self.y_ITG = self.y[0:self.ITG_ETG]
            self.y_ETG = self.y[self.ITG_ETG:-1]

            self.z_ITG = self.gam_GB[:,0,0,0:self.ITG_ETG]
            self.z_ETG = self.gam_GB[:,0,0,self.ITG_ETG:-1]

            # add levels and norm with ITG and ETG

            self.levels_ITG = MaxNLocator(nbins=20).tick_values(self.z_ITG.min(), self.z_ITG.max())
            self.levels_ETG = MaxNLocator(nbins=20).tick_values(self.z_ETG.min(), self.z_ETG.max())
            self.norm_ITG = BoundaryNorm(self.levels_ITG, ncolors=self.cmap.N, clip=True)
            self.norm_ETG = BoundaryNorm(self.levels_ETG, ncolors=self.cmap.N, clip=True)

            self.axes['colorbar ETG'].cla()
            self.axes['colorbar ITG'].cla()

            self.countour_axis_ITG = self.axes['turb ITG']
            self.countour_axis_ETG = self.axes['turb ETG']

            self.countour_axis_ITG.cla()
            self.countour_axis_ETG.cla()

            if self.fugure3d == False:

                self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:9])
                self.countour_axis_ETG = fig.add_subplot(self.gs[2:-3,13:-1])

                self.cf_ITG = self.countour_axis_ITG.contourf(self.y_ITG, self.times, self.z_ITG, cmap=self.cmap, levels = self.levels_ITG)
                self.cf_ETG = self.countour_axis_ETG.contourf(self.y_ETG, self.times, self.z_ETG, cmap=self.cmap, levels = self.levels_ETG)

            else:

                 self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:9], projection = '3d')
                 self.countour_axis_ETG = fig.add_subplot(self.gs[2:-3,13:-1], projection = '3d')

                 x_ITG, y_ITG = np.meshgrid(self.y_ITG, times)
                 x_ETG, y_ETG = np.meshgrid(self.y_ETG, times)

                 self.cf_ITG = self.countour_axis_ITG.plot_surface(y_ITG, x_ITG, self.z_ITG, cmap=self.cmap)
                 self.cf_ETG = self.countour_axis_ETG.plot_surface(y_ETG, x_ETG, self.z_ETG, cmap=self.cmap)

            self.countour_axis_ITG.set_xlabel(r'$ k_{\theta} $ [-]', fontsize = fontx)
            self.countour_axis_ITG.set_ylabel(r'time [s]', fontsize = fonty)
            self.countour_axis_ETG.set_xlabel(r'$ k_{\theta} $ [-]', fontsize = fontx)
            self.countour_axis_ETG.set_ylabel(r'time [s]', fontsize = fonty)


            self.cb_ITG = fig.colorbar(self.cf_ITG, norm = self.norm_ITG, cax = self.axes['colorbar ITG'], cmap = self.cmap, values = self.levels_ITG)
            self.cb_ETG = fig.colorbar(self.cf_ETG, norm = self.norm_ETG, cax = self.axes['colorbar ETG'], cmap = self.cmap, values = self.levels_ETG)

            # Initialize dimx slider

            self.slider_axis = self.axes['slider']

            # Need to specify which slider I am using to let him know what to update in the GUI when I slide

            if current != self.sliding_rho:
                self.slider_axis.clear()
                self.slider.disconnect(self.slide)
                self.slider = DiscreteSlider(self.slider_axis, 'dimx', rho[0], rho[-1], allowed_vals=rho, valinit=rho[0])
            else:
                self.update_grow_rho(self.val_rho)
            self.slide = self.slider.on_changed(self.update_grow_rho)

            self.fig.canvas.draw_idle()
#            fig.canvas.draw_idle()

        # Define the event triggered by slider update
        def update_grow_rho(self, val_rho):

        # Find the value in rho that correspond to the val and substitute the data with those

            self.val_rho = copy(val_rho)
            rho_index = int(np.where(rho == val_rho)[0])

            self.z_ITG = self.gam_GB[:,0,rho_index,0:self.ITG_ETG]
            self.z_ETG = self.gam_GB[:,0,rho_index,self.ITG_ETG:-1]

            self.levels_ITG = MaxNLocator(nbins=20).tick_values(self.z_ITG.min(), self.z_ITG.max())
            self.levels_ETG = MaxNLocator(nbins=20).tick_values(self.z_ETG.min(), self.z_ETG.max())
            self.norm_ITG = BoundaryNorm(self.levels_ITG, ncolors=self.cmap.N, clip=True)
            self.norm_ETG = BoundaryNorm(self.levels_ETG, ncolors=self.cmap.N, clip=True)

            self.countour_axis_ITG = self.axes['turb ITG']
            self.countour_axis_ETG = self.axes['turb ETG']

            self.countour_axis_ITG.cla()
            self.countour_axis_ETG.cla()

            if self.fugure3d == False:

                self.countour_axis_ITG = self.axes['turb ITG']
                self.countour_axis_ETG = self.axes['turb ETG']

                self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:9])
                self.countour_axis_ETG = fig.add_subplot(self.gs[2:-3,13:-1])

                self.cf_ITG = self.countour_axis_ITG.contourf(self.y_ITG, self.times, self.z_ITG, cmap=self.cmap, levels = self.levels_ITG)
                self.cf_ETG = self.countour_axis_ETG.contourf(self.y_ETG, self.times, self.z_ETG, cmap=self.cmap, levels = self.levels_ETG)

            else:

                 self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:9], projection = '3d')
                 self.countour_axis_ETG = fig.add_subplot(self.gs[2:-3,13:-1], projection = '3d')

                 x_ITG, y_ITG = np.meshgrid(self.y_ITG, self.times)
                 x_ETG, y_ETG = np.meshgrid(self.y_ETG, self.times)

                 self.cf_ITG = self.countour_axis_ITG.plot_surface(y_ITG, x_ITG, self.z_ITG, cmap=self.cmap)
                 self.cf_ETG = self.countour_axis_ETG.plot_surface(y_ETG, x_ETG, self.z_ETG, cmap=self.cmap)


            self.cb_ITG = fig.colorbar(self.cf_ITG, norm = self.norm_ITG, cax = self.axes['colorbar ITG'], cmap = self.cmap, values = self.levels_ITG)
            self.cb_ETG = fig.colorbar(self.cf_ETG, norm = self.norm_ETG, cax = self.axes['colorbar ETG'], cmap = self.cmap, values = self.levels_ETG)

            self.countour_axis_ITG.set_xlabel(r'$ k_{\theta} $ [-]', fontsize = fontx)
            self.countour_axis_ITG.set_ylabel(r'time [s]', fontsize = fonty)
            self.countour_axis_ETG.set_xlabel(r'$ k_{\theta} $ [-]', fontsize = fontx)
            self.countour_axis_ETG.set_ylabel(r'time [s]', fontsize = fonty)

            self.axes['turb ITG'].autoscale(axis='y')
            self.axes['turb ETG'].autoscale(axis='y')

            self.fig.canvas.draw_idle()
#            fig.canvas.draw_idle()

        def update_grow_time(self, val_time):

        # Find the value in time that correspond to the val and substitute the data with those
            self.val_time = copy(val_time)
            time_index = int(np.where(self.times == val_time)[0])

            self.z_ITG = self.gam_GB[time_index,0,:,0:self.ITG_ETG]
            self.z_ETG = self.gam_GB[time_index,0,:,self.ITG_ETG:-1]

            self.levels_ITG = MaxNLocator(nbins=20).tick_values(self.z_ITG.min(), self.z_ITG.max())
            self.levels_ETG = MaxNLocator(nbins=20).tick_values(self.z_ETG.min(), self.z_ETG.max())
            self.norm_ITG = BoundaryNorm(self.levels_ITG, ncolors=self.cmap.N, clip=True)
            self.norm_ETG = BoundaryNorm(self.levels_ETG, ncolors=self.cmap.N, clip=True)

            self.countour_axis_ITG = self.axes['turb ITG']
            self.countour_axis_ETG = self.axes['turb ETG']
            self.countour_axis_ITG.set_xlabel(r'$ \rho $ [-]', fontsize = fontx)
            self.countour_axis_ITG.set_ylabel(r'$ k_{\theta} $ [-]', fontsize = fonty)
            self.countour_axis_ETG.set_xlabel(r'$ \rho $ [-]', fontsize = fontx)
            self.countour_axis_ETG.set_ylabel(r'$ k_{\theta} $ [-]', fontsize = fonty)


            self.countour_axis_ITG.cla()
            self.countour_axis_ETG.cla()

            if self.fugure3d == False:

                self.countour_axis_ITG = self.axes['turb ITG']
                self.countour_axis_ETG = self.axes['turb ETG']

                self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:9])
                self.countour_axis_ETG = fig.add_subplot(self.gs[2:-3,13:-1])

                self.cf_ITG = self.countour_axis_ITG.contourf(self.y_ITG, self.rho, self.z_ITG, cmap=self.cmap, levels = self.levels_ITG)
                self.cf_ETG = self.countour_axis_ETG.contourf(self.y_ETG, self.rho, self.z_ETG, cmap=self.cmap, levels = self.levels_ETG)

            else:

                 self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:9], projection = '3d')
                 self.countour_axis_ETG = fig.add_subplot(self.gs[2:-3,13:-1], projection = '3d')

                 x_ITG, y_ITG = np.meshgrid(self.y_ITG, self.rho)
                 x_ETG, y_ETG = np.meshgrid(self.y_ETG, self.rho)

                 self.cf_ITG = self.countour_axis_ITG.plot_surface(y_ITG, x_ITG, self.z_ITG, cmap=self.cmap)
                 self.cf_ETG = self.countour_axis_ETG.plot_surface(y_ETG, x_ETG, self.z_ETG, cmap=self.cmap)

            self.cb_ITG = fig.colorbar(self.cf_ITG, norm = self.norm_ITG, cax = self.axes['colorbar ITG'], cmap = self.cmap, values = self.levels_ITG)
            self.cb_ETG = fig.colorbar(self.cf_ETG, norm = self.norm_ETG, cax = self.axes['colorbar ETG'], cmap = self.cmap, values = self.levels_ETG)

            self.axes['turb ITG'].autoscale(axis='y')
            self.axes['turb ETG'].autoscale(axis='y')

            self.fig.canvas.draw_idle()
#            fig.canvas.draw_idle()

        def update_grow_ktheta(self, val_ktheta):

        # Find the value in rho that correspond to the val and substitute the data with those
            self.val_ktheta = copy(val_ktheta)
            k_index = int(np.where(self.ktheta == val_ktheta)[0])

            self.z_ITG = self.gam_GB[:,0,:,k_index]

            self.levels_ITG = MaxNLocator(nbins=15).tick_values(self.z_ITG.min(), self.z_ITG.max())
            self.norm_ITG = BoundaryNorm(self.levels_ITG, ncolors=self.cmap.N, clip=True)

            self.countour_axis_ITG = self.axes['turb ITG']
            self.countour_axis_ITG.cla()

            if self.fugure3d == False:

                self.countour_axis_ITG = self.axes['turb ITG']
                self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:-1])
                self.cf_ITG = self.countour_axis_ITG.contourf(self.y, self.times, self.z_ITG, cmap=self.cmap, levels = self.levels_ITG)

            else:

                 self.countour_axis_ITG = fig.add_subplot(self.gs[2:-3,2:-1], projection = '3d')
                 x_ITG, y_ITG = np.meshgrid(self.y, self.times)
                 self.cf_ITG = self.countour_axis_ITG.plot_surface(y_ITG, x_ITG, self.z_ITG, cmap=self.cmap)

            self.countour_axis_ITG.set_xlabel(r'$ \rho $ [-]', fontsize = fontx)
            self.countour_axis_ITG.set_ylabel('time [s]', fontsize = fonty)

            self.cb_ITG = fig.colorbar(self.cf_ITG, norm = self.norm_ITG, cax = self.axes['colorbar ITG'], cmap = self.cmap, values = self.levels_ITG)

            self.countour_axis_ITG.autoscale(axis='y')

#            fig.canvas.draw_idle()
            self.fig.canvas.draw_idle()

        def change_figure(self):

            if self.fugure3d == True:
                self.fugure3d = False
            else:
                self.fugure3d = True

            if self.sliding_time == True:
                self.slide_time()

            if self.sliding_ktheta == True:
                self.slide_ktheta()

            if self.sliding_rho == True:
                self.slide_rho()

        def smooth_data(self):

            if self.smoothed_data == True:
                self.smoothed_data = False
                self.gam_GB = copy(self.gam_GB_unsmoothed)
            else:
                self.smoothed_data = True
                self.gam_GB = copy(gaussian_filter(gam_GB, 0.6))

            if self.sliding_time == True:
                self.slide_time()

            if self.sliding_ktheta == True:
                self.slide_ktheta()

            if self.sliding_rho == True:
                self.slide_rho()


        def save_figure(self):

            self.extent = join_quadruple_axis(self.countour_axis_ITG, self.axes['colorbar ITG'], self.countour_axis_ETG, self.axes['colorbar ETG'], pad = 0.04).transformed(self.fig.dpi_scale_trans.inverted())
            self.fig.savefig('turb_plot.png', bbox_inches=self.extent, dpi = 100)

        def save_figure_ITG(self):

            self.extent_ITG = join_double_axis(self.countour_axis_ITG, self.axes['colorbar ITG'], pad = 0.04).transformed(self.fig.dpi_scale_trans.inverted())
            self.fig.savefig('ITG_turb_plot.png', bbox_inches=self.extent_ITG, dpi = 100)

        def save_figure_ETG(self):

            self.extent_ETG = join_double_axis(self.countour_axis_ETG, self.axes['colorbar ETG'], pad = 0.04).transformed(self.fig.dpi_scale_trans.inverted())
            self.fig.savefig('ETG_turb_plot.png', bbox_inches=self.extent_ETG, dpi = 100)


#   Buttons definition

    class SliderButtonTime(object):

        def __init__(self, turb_analysis):
            self.turb_analysis = turb_analysis
        def slide_time(self, event):
            self.turb_analysis.slide_time()


    class SliderButtonKtheta(object):

        def __init__(self, turb_analysis):
            self.turb_analysis = turb_analysis
        def slide_ktheta(self, event):
            self.turb_analysis.slide_ktheta()


    class SliderButtonRho(object):

        def __init__(self, turb_analysis):
            self.turb_analysis = turb_analysis
        def slide_rho(self, event):
            self.turb_analysis.slide_rho()

    class ChangeFigureButton(object):

        def __init__(self, turb_analysis):
            self.turb_analysis = turb_analysis
        def change_figure(self, event):
            self.turb_analysis.change_figure()


    class SmoothDataButton(object):

        def __init__(self, turb_analysis):
            self.turb_analysis = turb_analysis
        def smooth_data(self, event):
            self.turb_analysis.smooth_data()


    class SaveFigureButton(object):

        def __init__(self, turb_analysis):
            self.turb_analysis = turb_analysis
        def save_figure(self, event):
            self.turb_analysis.save_figure()


    class SaveFigureITGButton(object):

        def __init__(self, turb_analysis):
            self.turb_analysis = turb_analysis
        def save_figure_ITG(self, event):
            self.turb_analysis.save_figure_ITG()


    class SaveFigureETGButton(object):

        def __init__(self, turb_analysis):
            self.turb_analysis = turb_analysis
        def save_figure_ETG(self, event):
            self.turb_analysis.save_figure_ETG()


    turb_analysis = TurbFigure(fig, ktheta, rho, times, gam_GB, fontx, fonty)

    callback_time = SliderButtonTime(turb_analysis)
    callback_ktheta = SliderButtonKtheta(turb_analysis)
    callback_rho = SliderButtonRho(turb_analysis)
    callback_change_figure = ChangeFigureButton(turb_analysis)
    callback_smooth_data = SmoothDataButton(turb_analysis)
    callback_save_figure = SaveFigureButton(turb_analysis)
    callback_save_figure_ITG = SaveFigureITGButton(turb_analysis)
    callback_save_figure_ETG = SaveFigureETGButton(turb_analysis)



    bslider_time = Button(turb_analysis.axes['slide time button'], 'Slide time')
    bslider_ktheta = Button(turb_analysis.axes['slide ktheta button'], 'Slide ktheta')
    bslider_rho = Button(turb_analysis.axes['slide rho button'], 'Slide rho')
    bchange_figure = Button(turb_analysis.axes['change figure'], 'Change figure')
    bsmooth_data = Button(turb_analysis.axes['smooth data'], 'Smooth data')
    bsave_figure = Button(turb_analysis.axes['save figure'], 'Save figure')
    bsave_figure_ITG = Button(turb_analysis.axes['save figure ITG'], 'ITG')
    bsave_figure_ETG = Button(turb_analysis.axes['save figure ETG'], 'ETG')



    bslider_time.on_clicked(callback_time.slide_time)
    bslider_ktheta.on_clicked(callback_ktheta.slide_ktheta)
    bslider_rho.on_clicked(callback_rho.slide_rho)
    bchange_figure.on_clicked(callback_change_figure.change_figure)
    bsmooth_data.on_clicked(callback_smooth_data.smooth_data)
    bsave_figure.on_clicked(callback_save_figure.save_figure)
    bsave_figure_ITG.on_clicked(callback_save_figure_ITG.save_figure_ITG)
    bsave_figure_ETG.on_clicked(callback_save_figure_ETG.save_figure_ETG)


    plt.show()

