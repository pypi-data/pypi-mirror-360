import logging
import os
import inspect
import argparse
from collections import OrderedDict
import itertools
from typing import Optional, List, Callable
from dataclasses import dataclass
from pathlib import Path
from ast import literal_eval

# Set up fancy logging already here
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    from idlelib.editor import EditorWindow
    # This import triggers module 'tkinter' has no attribute 'filedialog'
    from idlelib.pyshell import PyShellFileList
except ModuleNotFoundError:
    logger.error("Could not find idlelib build-in! This might indicate a broken"
                 " Python install. Try seaching for IDLE in your package"
                 " manager, e.g. `apt-get install idle` on Debian")
    raise
from cycler import cycler

import numpy as np
import xarray as xr

from jetto_tools.misc import dump_package_versions, get_repo_status, decode_catalog_path
from jetto_tools.classes import JETTO
from jetto_tools.tkinter_helpers import (
    fixed_map, throttle, _get_non_root_parent, _find_recursive_tree,
    _tkStringVar, SearchableComboBox, _tkDoubleVar, next_path
)

try:
    import matplotlib as mpl
    import matplotlib.style.core  # This loads the default library paths
    # Inject our own style file
    style_folder = Path(__file__).absolute().parent / 'templates'
    style_file = style_folder / 'jpyplot.mplstyle'
    if style_folder.is_dir():
        matplotlib.style.core.USER_LIBRARY_PATHS.append(style_folder.as_posix())
        matplotlib.style.core.reload_library()
    else:
        raise Exception('{!s} is not a folder, what happened?'.format(style_folder))
    # Now we can use it like this!
    if style_file.is_file():
        try:
            matplotlib.style.use('jpyplot')
            logger.info("Matplotlib style 'jpyplot' loaded")
        except OSError:
            logger.error(
                'Could not find jpyplot style file.  '
                'Falling back to default Matplotlib style'
            )
    else:
        raise Exception('{!s} is not a style file, what happened?'.format(style_file))

    # Let user file have precedence
    mpl.style.use(mpl.matplotlib_fname())
    logger.info("Current matplotlibrc loaded from {!s}".format(
        mpl.matplotlib_fname()))

    # Save the default jpyplot settings for later use
    from matplotlib import _rc_params_in_file
    jpyplot_style = _rc_params_in_file(str(style_file))

    import matplotlib.backends.backend_tkagg
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
    from matplotlib.backends.backend_agg import FigureCanvasAgg as NonInteractiveFigureCanvas
    import matplotlib.pyplot as plt

    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.filedialog
    import tkinter.font

    from tkcolorpicker import askcolor
    from tkfilebrowser import FileBrowser
except ImportError:
    logger.error(
        'Could not import TK libraries.'
        'Make sure jetto_tools were installed with the [gui] extra.'
    )
    raise

try:
    xr.Dataset.interp_like
except AttributeError:
    raise Exception('Xarray outdated, please update using `pip install xarray --user -U`')


my_version, my_dir = get_repo_status()
refresh_rate = 60  # Hz


def make_prop_cycler():
    cyc = mpl.rcParams['axes.prop_cycle']

    # We need a linestyle cycle, but the user might have overwritten it
    # Load it from our RC file
    if 'linestyle' not in cyc.keys:
        default_cyc = jpyplot_style['axes.prop_cycle']
        lss = []
        for default in default_cyc:
            lss.append(default['linestyle'])
        cyc += cycler(linestyle=lss)

    return cyc()


def uid_from_path(path):
    return str(Path(path).absolute())


def uid_to_pretty(uid):
    if 'seq#' in uid:
        # This is a 'catalogue' file. Split in its parts, a bit of guesswork!
        # Example path: ~/cmg/catalog/jetto/jet/92398/jun1620/seq#1/
        decoded = decode_catalog_path(uid)
        pretty = '{machine} {shotno} seq#{seqno}'.format_map(decoded)
    else:
        # This is a raw JETTO run dir
        # Example path: /common/cmg/kplass/jetto/runs/run92436_RAPTORbenchmark_v230519/
        pretty = os.path.split('/')[-1]

    return pretty


def uid_from_tree(tree, field):
    res = _find_recursive_tree(tree, 'path', item=field)
    if len(res) != 1:
        raise Exception('Unexpected result in finding path. Found {!s}'.format(res))
    path = list(res.keys())[0]
    run_uid = uid_from_path(path)
    return run_uid


def set_selector_values(selector, values):
    selector['values'] = values
    selector.set_combo_width_to_values()


class MainResultsWindow:
    """ This class provides to main plotting window
    """
    def __init__(self, window=None, headless=False, run_paths=None, file=None, xvar=None,
                 slicevar=None, sliceval=None, compvar=None, compfunc=None):
        """ Initialize the main plotting window

        This window contains all the user editable plot settings in
        the settings tree in `self.config_run` and the loaded runs
        in `self.run`

        kwargs:
            parent: The parent of the application. Usually None
            run_paths: Paths to JETTO runs to pre-load
        """
        dump_package_versions(log_func=logger.debug)
        self.root_window = window

        # Create contained widgets
        self.runs = OrderedDict()
        self.plot_settings = {}

        if file is None:
            xvec1_file = 'JSP'
            time_file = 'JST'
        else:
            xvec1_file = file
            time_file = file
        if xvar is None:
            xvec1_xvar = 'XRHO'
            time_xvar = 'time'
        else:
            xvec1_xvar = xvar
            time_xvar = xvar

        if not headless:
            self.create_window(window)

        self.radial_plot_tab = OneDPlotTab(
            self, 'xvec1', headless=headless, file=xvec1_file, xvar=xvec1_xvar,
            initial_sliceval=sliceval, slicevar=slicevar, compvar=compvar, compfunc=compfunc,
        )
        self.time_plot_tab = OneDPlotTab(
            self, 'time', headless=headless, file=time_file, xvar=time_xvar,
            slicevar=slicevar, compvar=compvar, compfunc=compfunc,
        )

        self.config_run = RunConfigurationFrame(self, headless=headless)

        if not headless:
            self.config_run.window.grid(sticky='wes')

            tabs = ttk.Notebook(self.window)
            tabs.grid(row=0, sticky='new', pady=3)
            tabs.add(self.radial_plot_tab.window, text='JSP Plot')
            tabs.add(self.time_plot_tab.window, text='JST Plot')

            tk.Button(
                self.window, text="QUIT", fg="red", command=self.quit_app,
            ).grid(pady=3, sticky='s')

        cyc = mpl.rcParams['axes.prop_cycle']
        # We need a linestyle cycle, but the user might have overwritten it
        # Load it from our RC file
        if 'linestyle' not in cyc.keys:
            default_cyc = jpyplot_style['axes.prop_cycle']
            lss = []
            for default in default_cyc:
                lss.append(default['linestyle'])
            cyc += cycler(linestyle=lss)
        self.default_prop_cycler = cyc()  # Start a matplotlib respecting color generator
        for path in run_paths:
            self._append_run(path)

        if not headless:
            self.config_run.init_tree()
            self.radial_plot_tab._set_file_values()
            self.time_plot_tab._set_file_values()

    def create_window(self, parent_window: tk.Frame):
        """Create the toplevel window."""
        window = self.window = tk.Frame(parent_window, padx=3,width=870,height=750)
        # Configure stretch and layout behaviour
        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=8,minsize=750)
        window.rowconfigure(1, weight=1)
        window.grid(sticky='nsew')

    def quit_app(self):
        self.root_window.destroy()

    @property
    def run_paths(self):
        return [run.run_path for run in self.runs.values()]

    def _append_run(self, path):
        """ Append a run to the runs and runSettings

        Warning! Does not take care of updating any GUI elements!
        """
        uid = uid_from_path(path)
        if uid in self.runs:
            print('Run with uid {!s} already loaded, ignoring'.format(uid))
            return
        try:
            run = self._load_jetto_file(path)
            settings = self._generate_plot_settings(path)
        except Exception as ee:
            print('ERROR: Reading {!s} raises:'.format(path))
            print('ERROR:', ee)
            print('ERROR: Are you sure this is a JETTO run? Ignoring..')
            return
        else:
            self.runs[uid] = run
            self.plot_settings[uid] = settings
            return uid

    def _load_jetto_file(self, path):
        run = JETTO(path, on_read_error='warn')
        if 'JSP' not in run:
            raise Exception('JETTO class has no JSP loaded!')
        return run

    def _generate_plot_settings(self, path):
        abspath = Path(path).absolute()
        props = next(self.default_prop_cycler)
        return OrderedDict(
            color=props['color'],
            linewidth=1.5,
            path=str(abspath),
            label=abspath.name,
            time_offset=0.0,
        )

    @property
    def _run_uids(self):
        return self.plot_settings.keys()


class RunConfigurationFrame:
    def __init__(self, parent=None, headless=False, run_paths=None):
        self.parent = parent

        if not headless:
            self.create_window(parent.window)

    @property
    def plot_settings(self):
        return self.parent.plot_settings

    def create_window(self, parent_window: tk.Frame) -> None:
        window = self.window = tk.Frame(parent_window,width=850,height=450)
        window.columnconfigure(1, weight=8,minsize=790)
        window.rowconfigure(0, weight=1)
        window.rowconfigure(1, weight=1,minsize=450)
        window.grid(row=2, sticky='nsew')
        #window.grid(column=1, sticky='nsew')

        tk.Button(
            window, text="add run", command=self.add_run,
        ).grid(row=0, column=0, sticky='sew', pady=3)
        tk.Button(
            window, text="del run", command=self.del_run,
        ).grid(row=1, column=0, sticky='new', pady=3)

        style = ttk.Style(window)
        # Fix for TK bug
        style.map(
            'Treeview',
            foreground=fixed_map(style, 'foreground'),
            background=fixed_map(style, 'background'),
        )

        tree = self.settings_tree = ttk.Treeview(
            window, columns=["one"])

        # Bind double-click to function to change cells
        tree.bind('<Double-1>', lambda event: treeview_set_cell_value(tree, self))
        tree.column("one", width=100)
        tree.heading("one", text="Value")
        tree.grid(row=0, column=1, sticky='nswe', rowspan=2)

    def init_tree(self):
        # Insert a new toplevel cell to the tree
        for uid, settings in self.plot_settings.items():
            self._append_tree(uid, settings)

    def _append_tree(self, uid, settings):
        tree = self.settings_tree
        cell_id = tree.insert('', 'end', text=settings['label'])
        # Add different settings for the run as children from the just created cell
        tree.insert(cell_id, 'end', text='path', values=settings['path'])
        tree.insert(cell_id, 'end', text='label', values=settings['label'])
        # Currently both the PLOT_HINTS and tree-like mechanisms are used, keep them in sync!
        color = settings['color']
        tree.insert(cell_id, 'end', text='color', values=color, tags=(color, ))
        tree.insert(cell_id, 'end', text='linewidth', values=settings['linewidth'])
        tree.insert(cell_id, 'end', text='time_offset', values=settings['time_offset'])
        # Check here if the user specified a color that matplotlib can use
        if not mpl.colors.is_color_like(color):
            print('Plot hint is not color-like, ignoring..')
        tree.tag_configure(color, background=mpl.colors.to_hex(color))

    def del_run(self, run_uids=None):
        """ Remove a run from the runs and runSettings """
        if run_uids is None:
            tree = self.settings_tree
            cur_sel = tree.selection()

            run_uids = []
            # Find the selected runs uids
            for selected_run in cur_sel:
                # Search for path recursively in selected entries
                run_uid = uid_from_tree(tree, selected_run)
                run_uids.append(run_uid)
                # Delete entry from Treeview
                tree.delete(selected_run)

        # Delete entries from runs and settings
        for uid in run_uids:
            del self.runs[uid]
            del self.plot_settings[uid]

    @property
    def runs(self):
        return self.parent.runs

    def add_run(self):
        cwd = os.getcwd()
        dialog = FileBrowser(self.window, mode="opendir", multiple_selection=True, initialdir=cwd)
        RUNS_HOME = os.getenv('RUNS_HOME')
        USER = os.getenv('USER')
        HOME = os.getenv('HOME')
        if RUNS_HOME is None:
            print("env variable RUNS_HOME undefined, not adding run dir")
            run_home = None
        else:
            run_home = os.path.abspath(os.path.join(RUNS_HOME, 'jetto/runs'))
            if os.path.isdir(run_home):
                dialog.left_tree.insert(
                    "", "0", iid=run_home, text="run dir", image=dialog.im_folder)
            else:
                print('Could not find {!s}, not adding to bookmarks'.format(run_home))
        if USER is None:
            print("env variable USER undefined, not adding common run dir")
        else:
            common_run_home = os.path.abspath(os.path.join('/common/cmg/', USER, 'jetto/runs'))
            if run_home != common_run_home:
                if os.path.isdir(common_run_home):
                    dialog.left_tree.insert(
                        "", "0", iid=common_run_home, text="common run dir", image=dialog.im_folder)
                else:
                    print('Could not find {!s}, not adding to bookmarks'.format(common_run_home))
        if HOME is None:
            print("env variable HOME undefined, not adding catalog dir")
        else:
            catalog = os.path.abspath(os.path.join(HOME, 'cmg/catalog/jetto'))
            if os.path.isdir(catalog):
                dialog.left_tree.insert("", "0", iid=catalog, text="catalog", image=dialog.im_folder)
            else:
                print('Could not find {!s}, not adding to bookmarks'.format(catalog))
        dialog.wait_window(dialog)
        selected = dialog.get_result()
        if not selected:  # type consistency: always return a tuple
            selected = ()
        for path in selected:
            run_uid = self.parent._append_run(path)
            if run_uid is not None:
                self._append_tree(run_uid, self.plot_settings[run_uid])


class FieldEditor(tk.Toplevel):
    def __init__(self, initial, *, parent=None):
        super().__init__(parent, padx=12)

        self.result = None

        entryedit = tk.Text(self, width=80, height=3)
        entryedit.grid(columnspan=2, pady=6)
        entryedit.focus()

        if initial:
            entryedit.insert('1.0', initial)

        def on_cancel(event=None):
            self.destroy()

        def on_ok(event=None):
            self.result = entryedit.get('1.0', 'end-1c').strip()
            self.destroy()

        self.attributes('-type', 'dialog')
        self.bind('<Return>', on_ok)
        self.bind('<Escape>', on_cancel)

        ttk.Button(
            self, text='Cancel', width=6, command=on_cancel,
        ).grid(row=1, column=0)
        ttk.Button(
            self, text='OK', width=6, command=on_ok,
        ).grid(row=1, column=1, pady=6)

    def wait_result(self) -> str:
        self.wait_window()
        return self.result


def treeview_set_cell_value(treeview: ttk.Treeview, parent):
    """Function attached to double click of `tkk.TreeView` that can modify the values of cells"""
    selection = treeview.selection()

    # On double click, only one field is selected. Check which run it is
    if len(selection) > 1:
        raise Exception('Unexpected! More than one item selected on double click')

    selected_root = _get_non_root_parent(treeview, selection)
    if selected_root == selection:
        return

    selected_key = treeview.item(selection)['text']

    # Do not allow changing of path
    if selected_key == 'path':
        return

    old_value = treeview.item(selection, 'values')[0]
    item = selection[0]

    if selected_key == 'color':
        # If the color field is being edited, open a colorpicker
        _, new_value = askcolor(old_value, parent.window)
        if new_value is None:
            return

        # If a color is chosen, set the runSettings and PLOT_HINTS accordingly
        # No need to do checking, the color picker always returns something matplotlib can use
        treeview.item(selection, tags=new_value)
        treeview.tag_configure(new_value, background=new_value)
    else:
        new_value = FieldEditor(
            old_value, parent=parent.window
        ).wait_result()
        if new_value is None:
            return

        treeview.set(item, column=0, value=new_value)

        # make sure linestyle is valid, will log an error
        if selected_key == 'linestyle':
            # try parsing it, will log an error on failure
            parse_linestyle(new_value)
        elif selected_key != 'label':
            # assume everythig else is a float
            float(new_value)

    treeview.set(item, column=0, value=new_value)

    run_uid = uid_from_tree(treeview, selected_root)
    parent.plot_settings[run_uid][selected_key] = new_value


def apply_variable_function(func, var, comp):
    return xr.DataArray(eval(func))


@dataclass
class VariableDefinition:
    var: str
    comp: str = ''
    func: str = ''
    label: str = ''

    def ui_description(self):
        if self.label:
            return self.label
        if self.comp or self.func:
            return f"var={self.var} comp={self.comp} fn={self.func}"
        return f"var={self.var}"

    def line_label(self, run: JETTO, file: str) -> str:
        if self.label:
            return self.label
        if self.comp and self.func:
            return f'{self.func}, where var={self.var!r} and comp={self.comp!r}'
        return run[file][self.var].attrs['description']

    def get_data(self, run: JETTO, file: str):
        if (self.comp is None) != (self.func is None):
            raise Exception('If yvar_comp is given, yvar_comp_func should be given too')

        try:
            runfile = run[file]
            yvariable = runfile[self.var]
            ycompvar = runfile.get(self.comp)
        except KeyError:
            return None

        if self.func and ycompvar is not None:
            bothvars = xr.merge([yvariable, ycompvar])
            compvar = interpolate_grids(bothvars, self.var, self.comp)
            compvar = compvar.drop_vars([c for c in compvar.coords if c not in compvar.dims])
            yvariable = apply_variable_function(self.func, compvar[self.var], compvar[self.comp])
            yvariable.attrs['description'] = '-'
            yvariable.attrs['units'] = '-'

        yvariable.name = 'y'
        return yvariable


def calc_nrows_ncols(naxes):
    nrows = int(round(np.sqrt(naxes)))
    ncols = (naxes + nrows-1) // nrows
    return nrows, ncols


def format_xaxis_label(variable):
    attrs = variable.attrs
    desc = attrs.get('description', '[ unknown ]')
    unit = attrs.get('units', '-')
    if unit == '-':
        return desc
    return f'{desc} [{unit}]'


def format_yaxis_label(variable):
    unit = variable.attrs['units']
    if unit == '-':
        return '[ unitless ]'
    return unit


def scale_range(mn, mx, delta):
    delta *= mx - mn
    delta2 = delta * 2
    # if zero is between the lower limit and a bit more than our
    # space, just use zero
    if mn - delta2 <= 0 <= mn:
        mn = 0
    else:
        mn = mn - delta
    # similar as above, but for upper limit
    if mx <= 0 <= mx + delta2:
        mx = 0
    else:
        mx = mx + delta
    return mn, mx


@dataclass
class RunSettings:
    run: JETTO
    label: str
    color: str
    linewidth: Optional[float] = None
    time_offset: float = 0.

    @property
    def path(self) -> str:
        return self.run.run_path

    def remap_and_merge(self, variables: List[xr.DataArray]) -> xr.Dataset:
        results = []

        # make sure coordinates reflect requested time offset
        for i, data in enumerate(variables):
            if 'time' in data.coords:
                newtime = data.coords['time'] + self.time_offset
                data = data.assign_coords({'time': newtime})

            results.append(data)

        return xr.merge(results)


@dataclass
class FigureSettings:
    runs: List[RunSettings]

    # file should be Literal['JST', 'JSP'] but it's not in Python 3.7
    file: str

    xvar: str
    yvars: List[VariableDefinition]
    zvar: str

    @classmethod
    def from_runs_and_settings(
            cls, runs, plot_settings, file: str,
            xvar: str, yvars: List[VariableDefinition], zvar: str,
    ):
        rs = []
        for run, settings in zip(runs.values(), plot_settings.values()):
            rs.append(RunSettings(
                run=run,
                label=settings['label'],
                color=settings['color'],
                linewidth=float(settings['linewidth']),
                time_offset=float(settings['time_offset']),
            ))

        return cls(
            runs=rs,
            file=file,
            xvar=xvar,
            yvars=yvars,
            zvar=zvar,
        )

    @property
    def output_basename(self):
        """should turn this into an attribute at some point

        filename without any directory or extension.
        """
        yvars = '_'.join(v.var for v in self.yvars)
        return f'{self.xvar}_vs_{yvars}'

    def _get_file_vars(self, *vars):
        file = self.file
        did_yield = False
        last_err = None
        for run in self.runs:
            try:
                runfile = run.run[file]
                yield tuple(runfile[var] for var in vars)
                did_yield = True
            except KeyError as err:
                last_err = err

        if not did_yield and last_err:
            raise last_err

    def get_var_range(self, var: str):
        values = []
        file = self.file
        for run in self.runs:
            try:
                data = run.run[file][var]
            except KeyError:
                raise KeyError("did not find var in run", var, file, run.path)

            if var == 'time':
                data = data + run.time_offset

            values.append(float(data.min()))
            values.append(float(data.max()))

        return min(values), max(values)

    def expand_sliceval(self, sliceval):
        if sliceval is None or sliceval == 'all':
            return None
        if sliceval == 'last':
            return self.get_var_range(self.zvar)[1]
        if sliceval == 'first':
            return self.get_var_range(self.zvar)[0]
        return sliceval

    def _get_var_comp_unit(self, var: VariableDefinition) -> str:
        datas = self._get_file_vars(var.var, var.comp)
        try:
            data, comp = next(datas)
        except (KeyError, StopIteration):
            # didn't find a file with the variables in
            return None

        # try and keep plots have similar derived units together
        units_data = data.attrs['units']
        units_comp = comp.attrs['units']
        return f'{units_data} {units_comp} {var.func}'

    def _get_var_unit(self, var: VariableDefinition) -> str:
        if var.comp and var.func:
            return self._get_var_comp_unit(var)

        datas = self._get_file_vars(var.var)
        try:
            data, = next(datas)
        except (KeyError, StopIteration):
            # didn't find a file with the variables in
            return None

        return data.attrs['units']

    def draw_yvar_on_axis(
            self, axes: mpl.axes.Axes, run: RunSettings,
            yvar: VariableDefinition, zval: Optional[float] = None,
    ) -> plt.Line2D:
        xvariable = self._grab_var(run, self.xvar, 'x')
        zvariable = self._grab_var(run, self.zvar, 'z')
        yvariable = yvar.get_data(run.run, self.file)

        if self.zvar and zvariable is None:
            logger.debug(f"unable to locate {self.zvar} in {run.path}")

        if xvariable is None:
            logger.info(f"unable to locate {self.xvar} in {run.path}")
            return

        if yvariable is None:
            logger.info(f"unable to locate {yvar.var} in {run.path}")
            return

        variables = [xvariable, yvariable]
        if zvariable is not None:
            variables.append(zvariable)

        # resample things to put them on a common scale
        plotvar = run.remap_and_merge(variables)
        plotvar = interpolate_grids(plotvar, 'x', 'y')
        plotvar = broadcast_grids(plotvar, 'x', 'y')

        if self.zvar:
            plotvar = grab_slice(plotvar, [self.zvar, zval])

        kwds = dict(
            color=run.color,
            linewidth=run.linewidth,
            label=run.label,
        )

        line, = axes.plot(plotvar['x'], plotvar['y'], **kwds)
        return line

    def build_figure(self, figure: plt.Figure) -> 'FigureDrawer':
        # more than two runs, just plot each variable seperately
        if len(self.runs) > 2:
            axes_yvars = [[yvar] for yvar in self.yvars]
        else:
            # group the axes together based on their unit
            axes_yvars = [
                list(yvars) for _, yvars in
                itertools.groupby(self.yvars, key=self._get_var_unit)
            ]

        # how many axes (i.e. plots) do we want in our figure
        naxes = len(axes_yvars)
        nrows, ncols = calc_nrows_ncols(naxes)

        # not working to make final figure bigger, but keeps spacing better
        figure.set_figheight(5+2*nrows)
        figure.set_figwidth(5*ncols)

        axes = figure.subplots(nrows=nrows, ncols=ncols, sharex=True, squeeze=False)
        flataxes = axes.flatten()

        # for keeping track of what we're doing
        xranges = []
        yranges = [[] for _ in self.yvars]
        legend_elems = [{} for _ in self.yvars]
        run_elems = []

        missing_yvars = {v.var for v in self.yvars}

        drawer = FigureDrawer(figure)

        for run in self.runs:
            legend_label = run.label
            # add a zero-width space character to avoid omission of legend labels starting with "_"
            if legend_label.startswith('_'):
                legend_label = chr(8203) + legend_label
            # for the legend of runs at the top
            run_elems.append(plt.Line2D(
                [], [], color=run.color, linewidth=run.linewidth, label=legend_label))

            # let the user know if we didn't find things we needed
            xvariable = self._grab_var(run, self.xvar, 'x')
            zvariable = self._grab_var(run, self.zvar, 'z')
            if self.zvar and zvariable is None:
                logger.debug(f"unable to locate {self.zvar} in {run.path}")

            if xvariable is None:
                logger.info(f"unable to locate {self.xvar} in {run.path}")
                continue

            xranges += [xvariable.min(), xvariable.max()]

            for i_axis, (axis, yvars) in enumerate(zip(flataxes, axes_yvars)):
                for yvar, props in zip(yvars, make_prop_cycler()):
                    yvariable = yvar.get_data(run.run, self.file)
                    if yvariable is None:
                        logger.info(f"unable to locate {yvar.var} in {run.path}")
                        continue

                    missing_yvars.discard(yvar.var)

                    variables = [xvariable, yvariable]
                    if zvariable is not None:
                        variables.append(zvariable)

                    # resample things to put them on a common scale
                    plotvar = run.remap_and_merge(variables)
                    plotvar = interpolate_grids(plotvar, 'x', 'y')
                    plotvar = broadcast_grids(plotvar, 'x', 'y')

                    # put a line into the axis. if we have a zvar then
                    # we need to set up the drawer so it's set when we
                    # have a z value set
                    kwds = dict(
                        color=run.color,
                        linewidth=float(run.linewidth),
                        linestyle=parse_linestyle(props['linestyle']),
                    )

                    if zvariable is None:
                        plotline, = axis.plot(plotvar['x'], plotvar['y'], **kwds)
                    else:
                        plotline, = axis.plot([], [], **kwds)
                        drawer._add_plot_line(run, plotvar, plotline)

                    drawer._add_axes_run_line(run, plotline)

                    # add to axes legend
                    label = yvar.line_label(run.run, self.file)
                    legend_elems[i_axis][label] = plt.Line2D(
                        [], [], color='k', linestyle=kwds['linestyle'], label=label)

                    # make sure the axes look nice
                    yranges[i_axis] += [plotvar['y'].min(), plotvar['y'].max()]
                    axis.set_ylabel(format_yaxis_label(yvariable))

        if not xranges:
            raise Exception("XVAR '{!s}' not found in run's file '{!s}'".format(
                self.xvar, self.file))

        if missing_yvars:
            raise Exception("YVAR '{!s}' not found in run's file '{!s}'".format(
                ' '.join(missing_yvars), self.file))

        # more making things look nice!
        xrange = scale_range(min(xranges), max(xranges), 0.03)
        for i in range(naxes):
            ax = flataxes[i]
            legend = ax.legend(handles=legend_elems[i].values(),loc='lower left')
            drawer._add_axes_legend(legend)
            ax.set_xlim(xrange)
            yrange = yranges[i]
            ax.set_ylim(scale_range(min(yrange), max(yrange), 0.03))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        # hide unused axes
        lastrow = (nrows-1) * ncols
        for i, ax in enumerate(axes[-1, :]):
            if i + lastrow >= naxes:
                ax.set_yticks([])
                for name, spine in ax.spines.items():
                    spine.set_visible(name == 'bottom')
            ax.set_xlabel(format_xaxis_label(xvariable))

        # label the runs
        plotleg = figure.legend(
            handles=run_elems, ncol=1,
            loc='upper center'
        )

        drawer._set_plot_legend(plotleg, self.runs)

        # give 0.1 units of space for the run legend at the top
        figure.tight_layout(rect=(0.01, 0.01, 0.99, 0.90))

        return drawer

    def _grab_var(self, run: RunSettings, var: str, name: str):
        if not var:
            return None

        try:
            data = run.run[self.file][var]
        except KeyError:
            return None

        if var == 'time':
            attrs = data.attrs
            data = data + run.time_offset
            data.attrs = attrs

        data.name = name
        return data


class FigureDrawer:
    def __init__(self, figure: plt.Figure):
        self.figure = figure
        self._plotters = []
        self._axes_legends = []
        self._axes_run_lines = []
        self._legend_runlines = {}

    def _add_axes_legend(self, legend: mpl.legend.Legend):
        self._axes_legends.append(legend)

    def _add_plot_line(self, run: RunSettings, plotvar, line: plt.Line2D):
        self._plotters.append(
            (run, plotvar, line)
        )

    def _set_plot_legend(self, legend: mpl.legend.Legend, runs: List[RunSettings]):
        leglines = legend.get_lines()
        assert len(runs) == len(leglines)
        self._plot_legend = legend
        self._legend_runlines = {
            legline: run for run, legline in zip(runs, leglines)
        }

    def _add_axes_run_line(self, run: RunSettings, plotline: plt.Line2D):
        self._axes_run_lines.append(
            (run, plotline)
        )

    def draw(self, zslice, run_filter: Optional[Callable[[RunSettings], bool]] = None):
        for run, plotvar, line in self._plotters:
            if run_filter and not run_filter(run):
                continue
            var = grab_slice(plotvar, zslice)
            line.set_data(var['x'], var['y'])

    def make_interactive(self):
        self._plot_legend.set_draggable(True)
        for leg in self._axes_legends:
            leg.set_draggable(True)

        tolerance = 5  # in pts
        for legline in self._legend_runlines.keys():
            legline.set_picker(tolerance)
            legline.set_alpha(1.0)

        self.figure.canvas.mpl_connect('pick_event', self._on_mpl_pick)

    def _on_mpl_pick(self, event):
        event_run = self._legend_runlines.get(event.artist)
        if event_run is None:
            return

        plot_legline: plt.Line2D = event.artist

        # the resulting visibility
        vis = not (plot_legline.get_alpha() > 0.5)

        plot_legline.set_alpha(1.0 if vis else 0.2)

        for run, plotline in self._axes_run_lines:
            if run is event_run:
                plotline.set_visible(vis)

        self.figure.canvas.draw()


def slice_plotter(
        ax, lines, runs, file, xvar, yvar, zslice=(None, None),
        plot_settings=None, yvar_comp=None, yvar_comp_func=None,
        verbosity=0, line_labels=None
):
    """ Function that plots a slice."""

    if verbosity >= 1:
        logger.setLevel(logging.DEBUG)
    elif verbosity >= 0:
        logger.setLevel(logging.INFO)
    logger.debug("Launching slice plotter")

    assert lines is None, "parameter only exists for compatibilty with old API"
    assert line_labels is None, "parameter only exists for compatibilty with old API"

    if plot_settings is None:
        plot_settings = {}

    yvar = VariableDefinition(yvar, yvar_comp, yvar_comp_func)
    settings = FigureSettings.from_runs_and_settings(
        runs, plot_settings, file,
        xvar=xvar, yvars=[yvar], zvar=zslice[0],
    )

    for run in settings.runs:
        settings.draw_yvar_on_axis(ax, run, yvar, zslice[1])


class OneDVariableSelector:
    """ Select a plot variable """
    def __init__(self, parent, name, headless, xvar, slicevar, compfunc, compvar, show_xvar=True):
        self.parent = parent
        self.name = name
        if name == 'xvec1':
            yvar = 'TE'
        elif name == 'time':
            yvar = 'TEAX'
        else:
            yvar = ''

        self.yvars = [
            VariableDefinition(var=yvar, comp=compvar, func=compfunc),
        ]

        # Note that the name has to be unique for the whole app!
        self.xvar = _tkStringVar(value=xvar, name=f'{name}_xvar', headless=headless)
        self.yvar = _tkStringVar(name=f'{name}_yvar', headless=headless)
        self.yvar_comp = _tkStringVar(name=f'{name}_yvar_comp', headless=headless)
        self.yvar_comp_func = _tkStringVar(name=f'{name}_yvar_comp_func', headless=headless)
        self.yvar_label = _tkStringVar(name=f'{name}_yvar_label', headless=headless)
        self.zvar = _tkStringVar(value=slicevar, name=f'{name}_zvar', headless=headless)

        if not headless:
            self.create_window(parent.window, show_xvar)
            self._update_plotparam_vars(0)
            self._add_traces()

    def _tk_plot_event_mutex(self):
        """helper to prevent our code from responding to an event sent
        in response to an event we generated
        """
        # bail if we're already handling an event
        if self._in_plot_event:
            return
        try:
            # set the flag and yield, to let the caller run
            self._in_plot_event = True
            yield None
        finally:
            # in a finally to make sure this gets reset
            self._in_plot_event = False

    def create_window(self, parent_window: tk.Frame, show_xvar):
        window = self.window = tk.Frame(parent_window,width=80)
        window.grid(row=0, columnspan=2, sticky='nsew')

        if show_xvar:
            # Initialize x-variable selector
            tk.Label(
                window, text="XVar", font=13
            ).grid(row=0, column=0, sticky='ne')

            v = self.x_selector = SearchableComboBox(
                window, textvariable=self.xvar._variable,
                postcommand=self._set_xvar_values)
            if self.zvar.get() == 'none':
                v.configure(state='disabled')
            v.grid(row=0, column=1, sticky='ew')

        # Initialize y-variable selector
        tk.Label(
            window, text="YVar", font=13
        ).grid(row=1, column=0, sticky='ne')

        w = self.y_selector = SearchableComboBox(
            window, textvariable=self.yvar._variable,
            postcommand=self._set_yvar_values)
        w.grid(row=1, column=1, sticky='ew')

        # Initialize comparison y-variable selector
        tk.Label(
            window, text="YComp", font=13
        ).grid(row=2, column=0, sticky='ne')

        y = self.y_comp_selector = SearchableComboBox(
            window, textvariable=self.yvar_comp._variable,
            postcommand=self._set_yvarcomp_values)
        y.grid(row=2, column=1, sticky='ew')

        tk.Label(window, text="YFunc", font=13).grid(
            row=3, column=0, sticky='ne'
        )

        comp_func = self.y_comp_func_select = tk.Entry(
            window, textvariable=self.yvar_comp_func._variable)
        comp_func.grid(row=3, column=1, sticky='ew')

        tk.Label(window, text="Label", font=13).grid(
            row=4, column=0, sticky='ne'
        )
        label = self.y_label = tk.Entry(
            window, textvariable=self.yvar_label._variable)
        label.grid(row=4, column=1, sticky='ew')

        plt_ctls = tk.Frame(window)
        tk.Label(plt_ctls, text="Plots", font=13).grid(sticky='ne')
        tk.Button(
            plt_ctls, text="add", command=self._plots_add
        ).grid(sticky='e', pady=3)
        tk.Button(
            plt_ctls, text="del", command=self._plots_del
        ).grid(sticky='e')
        plt_ctls.columnconfigure(0, weight=1)
        plt_ctls.grid(row=5, column=0, sticky='new')

        lb = self.plots = tk.Listbox(window)
        lb.config(selectmode=tk.SINGLE)
        lb.grid(row=5, column=1, sticky='sew')

        for var in self.yvars:
            lb.insert(tk.END, var.ui_description())

        self._plots_cursel = 0
        self._in_plot_event = False
        lb.bind('<<ListboxSelect>>', self._plots_selected)

    def set_variables(self, vars: List[VariableDefinition]):
        # make a copy for safety
        self.yvars = vars[:]

        # replace list with our new variables
        try:
            lb = self.plots
        except AttributeError:
            pass
        else:
            lb.delete(0, tk.END)
            for var in self.yvars:
                lb.insert(tk.END, var.ui_description())

        self._update_plotparam_vars(0)

    def _update_plotparam_vars(self, idx_to: int):
        params = self.yvars[idx_to]

        describe = self.parent._describe_variable
        self.yvar.set(describe(params.var))
        self.yvar_comp.set(describe(params.comp))
        self.yvar_comp_func.set(params.func)

        self._plot_cursel = idx_to

    def _plots_selected(self, event: tk.Event):
        for _ in self._tk_plot_event_mutex():
            cursel = self.plots.curselection()
            if cursel:
                self._update_plotparam_vars(cursel[0])

    def _plots_add(self):
        params = VariableDefinition("", "", "")
        for _ in self._tk_plot_event_mutex():
            self.plots.insert(tk.END, params.ui_description())
            self.yvars.append(params)
            idx = len(self.yvars) - 1
            self._update_plotparam_vars(idx)
            self.plots.selection_clear(0, tk.END)
            self.plots.selection_set(idx)

    def _plots_del(self):
        if len(self.yvars) <= 1:
            return

        for _ in self._tk_plot_event_mutex():
            idx = self._plot_cursel
            self.plots.delete(idx)
            del self.yvars[idx]

            self._update_plotparam_vars(min(idx, len(self.yvars) - 1))

    def _add_traces(self):
        def on_change(*args):
            for _ in self._tk_plot_event_mutex():
                idx = self._plot_cursel
                yvar = self.yvars[idx]

                yvar.var = self.yvar.get().split('-', 1)[0].strip()
                yvar.comp = self.yvar_comp.get().split('-', 1)[0].strip()
                yvar.func = self.yvar_comp_func.get()
                yvar.label = self.yvar_label.get()

                self.plots.delete(idx)
                self.plots.insert(idx, yvar.ui_description())
                self.plots.selection_clear(0, tk.END)
                self.plots.selection_set(idx)

        self.yvar._variable.trace_add('write', on_change)
        self.yvar_comp._variable.trace_add('write', on_change)
        self.yvar_comp_func._variable.trace_add('write', on_change)
        self.yvar_label._variable.trace_add('write', on_change)

    def _set_xvar_values(self):
        set_selector_values(
            self.x_selector, self.parent._get_descriptive_xvars())

    def _set_yvarcomp_values(self):
        set_selector_values(
            self.y_comp_selector, self.parent._get_descriptive_yvars())

    def _set_yvar_values(self):
        set_selector_values(
            self.y_selector, self.parent._get_descriptive_yvars())

    def _file_selected(self, variables):
        self.x_selector.delete(0, tk.END)
        self.y_selector.delete(0, tk.END)
        for var in ['XRHO', 'xvec1']:
            if var in variables:
                self.x_selector.insert(0, var)
                break
        self._set_xvar_values()
        self._set_yvar_values()


class OneDPlotTab:
    """ Tab from plots that depend on radius, e.g. one-D plots """
    def __init__(self, parent=None, style='xvec1', headless=False, file=None,
                 xvar=None, initial_sliceval=None, slicevar=None,
                 compfunc=None, compvar=None):
        self.parent = parent

        self.initial_sliceval = initial_sliceval
        plot_vs_time = False

        if style == 'xvec1':
            if file is None:
                file = 'JSP'
            if xvar is None:
                xvar = 'XRHO'
            if slicevar is None:
                slicevar = 'time'
            if compvar is None:
                compvar = ''
            if compfunc is None:
                compfunc = ''
            plot_vs_time = True
        elif style == 'time':
            if file is None:
                file = 'JST'
            if xvar is None:
                xvar = 'time'
            if slicevar is None:
                slicevar = 'none'
            if compvar is None:
                compvar = 'TIAX'
            if compfunc is None:
                compfunc = ''
        else:
            raise NotImplementedError('OndDPlotTab with style {!s}'.format(style))

        self.file = _tkStringVar(value=file, name=f'{style}_file', headless=headless)

        if not headless:
            self.create_window(parent.window, plot_vs_time)

        self.selector = OneDVariableSelector(
            self, style, headless, xvar, slicevar, compfunc, compvar)

    def create_window(self, parent_window: tk.Frame, plot_vs_time: bool):
        """Create the toplevel window."""
        window = self.window = tk.Frame(padx=3, pady=3)
        window.grid()

        # Initialize file selector
        tk.Label(
            window, text="File", font=13,
        ).grid(row=1, column=0)

        self.file_selector = SearchableComboBox(
            window, state="readonly", textvariable=self.file._variable,
            postcommand=self._set_file_values)
        self.file_selector.grid(row=1, column=1)
        self.file_selector.bind('<<ComboboxSelected>>', self._file_selected)

        self.plot_button = tk.Button(
            window, text="plot", command=self.create_plotwindow)
        self.plot_button.grid(row=5, column=0)
        if plot_vs_time:
            self.plot_vs_time_button = tk.Button(
                window, text="plot_vs_time", command=self.create_plotwindow_vs_time)
            self.plot_vs_time_button.grid(row=5, column=1)

    @staticmethod
    def _get_variables_from_file(file, runs):
        variables = set()
        for run_uid, run in runs.items():
            if file in run:
                ds = run[file]
                variables = variables.union(ds.data_vars)
                for var in ['xvec1', 'xvec2']:
                    if var in ds.dims:
                        variables.add(var)
        if any(',' in var for var in variables):
            raise Exception('Variables with commas! That is the list separator')
        if any('-' in var for var in variables):
            raise Exception('Variables with dashes! That is the name - description separator')
        return sorted(list(variables))

    def _get_variables(self):
        file = self.file_selector.get()
        return self._get_variables_from_file(file, self.runs)

    def _describe_variable(self, var):
        for run in self.runs.values():
            ds = run[self.file.get()]
            if var in ds:
                unit = ds[var].units
                desc = ds[var].description
                return f'{var:6s} - {desc} [{unit}]'
        return var

    def _get_descriptive_vars(self, favourite_vars):
        variables = self._get_variables()

        for var in reversed(favourite_vars):
            if var in variables:
                variables.insert(0, var)

        return [self._describe_variable(var) for var in variables]

    def _get_descriptive_xvars(self):
        return self._get_descriptive_vars(('XRHO', 'XVEC1'))

    def _get_descriptive_yvars(self):
        return self._get_descriptive_vars(('TE', 'TI', 'NE'))

    def _set_file_values(self):
        # Determine what kind of files to show based on our first zvar
        if self.selector.zvar.get() in ['none', 'xvec1']:
            self.file_selector['values'] = self._get_time_files(self.runs)
        else:
            self.file_selector['values'] = self._get_profile_files(self.runs)

    @staticmethod
    def _get_profile_files(runs):
        all_files = OneDPlotTab._get_available_files(runs)
        return [file for file in all_files if file.endswith('P') or file[:-1].endswith('P')]

    @staticmethod
    def _get_time_files(runs):
        all_files = OneDPlotTab._get_available_files(runs)
        return [file for file in all_files if file.endswith('T') or file[:-1].endswith('T')]

    @staticmethod
    def _get_available_files(runs):
        files = set()
        for run in runs.values():
            profile_files = [file for file in run.keys()]
            files = files.union(profile_files)
        if any(',' in var for var in files):
            raise Exception('Files with commas! That is the list separator')
        return sorted(list(files))

    def _file_selected(self, event):
        self.selector._file_selected(self._get_variables())

    def create_plotwindow_vs_time(self, headless=False):
        settings = self.collect_plot_settings()
        settings.xvar = 'time'
        settings.zvar = 'xvec1'
        PlotWindow(settings, self.initial_sliceval, headless=headless)

    def create_plotwindow(self, headless=False):
        PlotWindow(self.collect_plot_settings(), self.initial_sliceval, headless=headless)

    def collect_plot_settings(self):
        plotbase = self.parent
        selector = self.selector
        xvar = selector.xvar.get().split('-')[0].strip()
        zvar = selector.zvar.get().split('-')[0].strip()

        if zvar == 'none':
            zvar = None

        return FigureSettings.from_runs_and_settings(
            plotbase.runs, plotbase.plot_settings, file=self.file.get(),
            xvar=xvar, yvars=selector.yvars, zvar=zvar
        )

    @property
    def runs(self):
        return self.parent.runs

    @property
    def run_paths(self):
        return self.parent.run_paths

    @property
    def plot_settings(self):
        return self.parent.plot_settings


class PlotCodeWindow:
    """ Window to display code. Taken from IDLE"""
    def __init__(self, parent=None, headless=False):
        self.parent = parent

        if not headless:
            self.create_window(parent.window)

    def create_window(self, parent_window: tk.Frame):
        flist = PyShellFileList(self)
        window = self.window = EditorWindow(root=parent_window, flist=flist)
        window.menubar.delete("Run")  # native IDLE run not working
        runmenu = tk.Menu(window.menubar, tearoff=0)
        runmenu.add_command(label="Run Standalone", command=self._run_standalone_plotscript)
        window.menubar.add_cascade(label="Run", menu=runmenu)
        # TODO: Insert custom run command
        text = window.text
        text.insert(tk.INSERT, self._get_script())
        if len(window.text.grid_info()) == 0:
            text.pack(fill=tk.BOTH, expand=True)
        else:
            text.grid(row=1, column=1)

    def _get_script(self):
        preamble = """
from jetto_tools.classes import JETTO
import xarray as xr
import matplotlib.pyplot as plt
"""

        script = preamble

        script += inspect.getsource(slice_plotter) + '\n'

        script += inspect.getsource(run_list_to_runs) + '\n'

        script += inspect.getsource(uid_from_path) + '\n'

        xvar = self.parent.xvar
        yvar = self.parent.yvar
        time = self.parent.timeslice.get()
        run_paths = [os.path.abspath(path) for path in self.run_paths]
        xlim = self.parent.ax.get_xlim()
        ylim = self.parent.ax.get_ylim()
        plot_script = """
fig, ax = plt.subplots()
time = {time}
xvar = "{xvar}"
yvar = "{yvar}"
run_paths = {run_paths}
ax.set_xlim({xlim})
ax.set_ylim({ylim})

runs = run_list_to_runs(run_paths)
slice_plotter(ax, None, runs, 'JSP', time, xvar, yvar)
plt.show()
""".format(time=time, xvar=xvar, yvar=yvar, run_paths=run_paths, xlim=xlim, ylim=ylim)
        script += plot_script

        return script

    @property
    def run_paths(self):
        return self.parent.parent.run_paths

    def _run_standalone_plotscript(self):
        # TODO: Think about isolating this from the main program
        exec(self._get_script())

    def quit(self):
        pass  # Nothing to do. Squelch IDLE exception


def slider_step(slider, step):
    slider.set(slider.get() + step)


class PlotWindow:
    """ A window to display plots in. """
    def __init__(self, settings: FigureSettings, initial_sliceval: str, headless=False):
        self.settings = settings
        self.zvar = settings.zvar

        self.timeslice = _tkDoubleVar(headless=headless)

        sliceval = settings.expand_sliceval(initial_sliceval)
        if sliceval is not None:
            self.timeslice.set(sliceval)

        if not headless:
            self.create_window()
        else:
            fig = self.fig = plt.Figure(figsize=(5, 5), dpi=100)
            fig.canvas = NonInteractiveFigureCanvas(fig)

            drawer = self.drawer = self.settings.build_figure(fig)

            zslice = self.get_zslice()
            if zslice[1] is None:
                print('Warning! Could not find slice in {!s}, plotting all'.format(zslice[0]))
                zslice = (None, None)

            drawer.draw(zslice)

            path = next_path('fig%s-*', search_path=os.path.abspath(os.getcwd()))
            path = path.replace('*', self.settings.output_basename + '.png')

            if zslice[0] is not None:
                fig.suptitle('{!s} = {!s}'.format(*zslice))

            fig.tight_layout()
            fig.savefig(path)

    def create_window(self) -> None:
        window = self.window = tk.Toplevel()

        fig = self.fig = plt.Figure(figsize=(5, 5), dpi=100)
        canvas = FigureCanvas(fig, window)
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.drawer = self.settings.build_figure(fig)

        fig = self.fig
        canvas = fig.canvas

        NavigationToolbar(canvas, window)
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH)

        if self.zvar in {'time', 'xvec1'}:
            slider_min, slider_max = self.settings.get_var_range(self.zvar)
            slider = tk.Scale(
                window,
                variable=self.timeslice._variable,
                from_=slider_min, to=slider_max,
                resolution=0.01,
                orient=tk.HORIZONTAL,
                command=self.update_plot
            )
            slider.pack(side=tk.BOTTOM, fill=tk.X)

            *_, slider_resolution = slider.config('resolution')
            button_press_step = max((slider_max - slider_min) / 100, slider_resolution)

            window.bind('<Left>', lambda event: slider_step(slider, -button_press_step))
            window.bind('<Right>', lambda event: slider_step(slider, button_press_step))
        else:
            # not sure why this is needed, but matplotlib events
            # aren't delivered without it! i.e. method registered in
            # canvas.mpl_connect never get called without this
            tk.Scale(window, command=self.update_plot)

        self.drawer.draw(self.get_zslice())
        self.drawer.make_interactive()

        #self.fig.tight_layout()

    def get_zslice(self):
        if self.zvar is not None:
            zslice = (self.zvar, self.timeslice.get())
        else:
            zslice = (None, None)
        return zslice

    @throttle(milliseconds=int(1/refresh_rate)*1000)
    def update_plot(self, value, *args, **kwargs):
        self.drawer.draw(self.get_zslice())
        self.fig.canvas.draw()


def grab_slice(plotvar_in, zslice):
    plotvar = plotvar_in.copy()
    zvar, zval = zslice
    if zvar == 'time':
        # TODO: Check, some files have the last time index repeated?
        useless = True
        for var in plotvar.data_vars:
            if not (plotvar.isel(time=-1) == plotvar.isel(time=-2)).all():
                useless = False
                break
        if useless:
            # Drop last time element
            plotvar = plotvar.isel(time=slice(None, -1, None))
    if len(plotvar['z'].dims) > 1:
        raise Exception('Multi-dimensional z variable. How is slicing even defined like that?')
    plotvar = plotvar.swap_dims({plotvar['z'].dims[0]: 'z'})
    # find index by value to allow small time increments for coconut
    i = (np.abs(plotvar['z'].data - zval)).argmin()
    plotvar = plotvar.isel({'z':i})

    return plotvar


def interpolate_grids(plotvar_in, var1, var2):
    plotvar = plotvar_in.copy()
    non_matching_dims = sorted(set(plotvar[var1].dims).symmetric_difference(plotvar[var2].dims))
    extrapolate = {
        'fill_value': 'extrapolate'
    }
    for dim in non_matching_dims:
        # most common is to map xvec1 to xvec2
        if dim == 'xvec1' and 'xvec2' in plotvar:
            plotvar = plotvar.interp({'xvec2': plotvar['xvec1']}, kwargs=extrapolate)
        # Or map xvec2 to xvec1
        elif dim == 'xvec2' and 'xvec1' in plotvar:
            plotvar = plotvar.interp({'xvec1': plotvar['xvec2']}, kwargs=extrapolate)
    return plotvar


def broadcast_grids(plotvar_in, var1, var2):
    plotvar = plotvar_in.copy()
    non_matching_dims = sorted(set(plotvar[var1].dims).symmetric_difference(plotvar[var2].dims))
    for dim in non_matching_dims:
        if dim in {'time', 'xvec1', 'xvec2'}:
            # Just broadcast if a dim is missing even after interpolation
            plotvar[var1] = plotvar[var1].broadcast_like(plotvar[dim])
            plotvar[var2] = plotvar[var2].broadcast_like(plotvar[dim])
        # Other cases still need to be found
        else:
            raise NotImplementedError('Plotting data with dims {!s} vs data with dims {!s}'.format(
                plotvar[var1].dims, plotvar[var2].dims))
    return plotvar


def run_list_to_runs(run_list):
    """ Transform a list of paths to a list of JETTO runs """
    runs = OrderedDict()
    for run_path in run_list:
        path = Path(run_path)
        runs[uid_from_path(path)] = JETTO(path)
    return runs


def parse_linestyle(linestyle):
    if linestyle is None:
        return None

    line2d = plt.Line2D([0], [0])

    try:
        line2d.set_linestyle(linestyle)
        return linestyle
    except ValueError as err:
        orig_err = err

    # parse as python literal, providing support for styles like '(0,(3,10,1,15))'
    try:
        # originally described as "Workaround for matplotlib<3.3.0",
        # but versions 2.2.2, 3.0.2, 3.1.2, 3.2.2, 3.3.2, 3.4.3 and
        # all require a tuple to be passed
        parsed = literal_eval(linestyle)
    except ValueError:
        logger.warning(f'Given linestyle {linestyle!r} invalid: {orig_err}')
        return None

    try:
        line2d.set_linestyle(parsed)
    except ValueError as err:
        logger.warning(f'Given linestyle {linestyle!r} invalid: {err}')
        return None

    return parsed


def parse_args():
    parser = argparse.ArgumentParser(
        description='Plot JETTO output folders.',
    )
    parser.add_argument(
        'run_path',
        nargs='*',
        default=[os.path.abspath('.')],
        help='file to plot',
    )
    parser.add_argument(
        '--plot-vars',
        help='comma-separated list of variables to plot on startup',
    )
    parser.add_argument(
        '--no-multiplot', dest='multiplot', default=True, action='store_false',
        help='plot variables in individual figures',
    )
    parser.add_argument(
        '--xvar',
        help='Variable to use as x-axis in generated plots',
    )
    parser.add_argument(
        '--file',
        help='File the --plot-vars can be found in',
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='start HEADLESS mode: dump plot to file, bypassing GUI',
    )
    parser.add_argument(
        '--sliceval',
        help='Value in zvar (usually time or xvec1) to slice',
    )
    parser.add_argument(
        '--slicevar',
        help='Variable name (usually time or xvec1) to slice',
    )
    parser.add_argument(
        '--plot-vs-time',
        action='store_true',
        help='Use plot_vs_time button instead of plot',
    )
    parser.add_argument(
        '--compvar',
        help='DEVELOPER OPTION: Set the "comp var" for comparison plots',
    )
    parser.add_argument(
        '--compfunc',
        help='DEVELOPER OPTION: Set the "comp funtion" for comparison plots',
    )
    parser.add_argument(
        '--xkcd',
        action='store_true',
        help='Turn on xkcd sketch-style drawing mode',
    )
    parser.add_argument(
        '-v', action='count', dest='verbosity', default=0,
        help='Set verbosity of jpyplot',
    )
    parser.add_argument(
        '--version', action='store_true',
        help='Show versions of jpyplot and associated tools',
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbosity >= 1:
        logger.setLevel(logging.DEBUG)

    if args.version:
        dump_package_versions()
        exit()

    parsed_run_paths = [path.rstrip('/') for path in args.run_path]
    if args.plot_vars is not None:
        parsed_plot_vars = args.plot_vars.split(',')
    else:
        parsed_plot_vars = []

    if args.compvar and len(parsed_plot_vars) > 1:
        raise Exception('Multiple plotvars for compvar is not supported')

    if args.sliceval is None and not args.plot_vs_time:
        sliceval = 'last'
    elif args.sliceval is None:
        sliceval = 0.5
    else:
        sliceval = args.sliceval

    if args.xkcd:
        plt.xkcd()

    kwargs = {
        'run_paths': parsed_run_paths,
        'xvar': args.xvar,
        'sliceval': sliceval,
        'slicevar': args.slicevar,
        'compvar': args.compvar,
        'compfunc': args.compfunc,
    }

    if args.file not in {'JSP', 'JST'}:
        kwargs['file'] = args.file

    if args.headless:
        app = MainResultsWindow(headless=True, **kwargs)
    else:
        root = tk.Tk()
        root.title('jpyplot ({!s})'.format(my_version))
        root.geometry('{}x{}'.format(870, 790))
        app = MainResultsWindow(window=root, **kwargs)

        # allow window to be drawn so plots appear "on top"
        app.window.update()

    def plot(yvars):
        tab = app.radial_plot_tab
        if args.file == 'JST':
            tab = app.time_plot_tab

        tab.selector.set_variables([
            VariableDefinition(yvar, args.compvar, args.compfunc)
            for yvar in yvars
        ])

        if args.plot_vs_time:
            tab.create_plotwindow_vs_time(headless=args.headless)
        else:
            tab.create_plotwindow(headless=args.headless)

    if args.multiplot:
        if parsed_plot_vars:
            plot(parsed_plot_vars)
    else:
        for var in parsed_plot_vars:
            plot([var])

    if not args.headless:
        app.window.mainloop()


if __name__ == '__main__':
    main()
