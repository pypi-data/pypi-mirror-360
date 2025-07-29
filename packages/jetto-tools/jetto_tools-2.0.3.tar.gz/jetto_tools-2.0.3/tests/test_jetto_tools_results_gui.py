import collections

import pytest

matplotlib = pytest.importorskip("matplotlib", minversion="3.0.2")
tkfilebrowser = pytest.importorskip("tkfilebrowser")
tkcolorpicker = pytest.importorskip("tkcolorpicker")

DefaultPlotcase = collections.namedtuple('DefaultPlotcase', 'dir data script vars')

from jetto_tools import results_gui


def test_slice_plotter(request):
    run = request.fspath.join('../../testdata/jetto-sanco-pencil-esco-qlknn')

    runs = {
        'plot name': results_gui.JETTO(run),
    }

    import matplotlib.pyplot as plt
    ax = plt.subplot()
    results_gui.slice_plotter(ax, None, runs, 'JST', 'time', 'TEAX')


#####################
# CLI prerequisites #
#####################

def test_single_run_singleplot(request, tmpdir, run_in_shell_wrapper):
    test_root = request.fspath
    script = test_root.join('../../jetto_tools/results_gui.py')
    data = test_root.join('../../testdata/jetto-sanco-pencil-esco-qlknn')
    vars = 'TE'
    cmd = 'python {!s} {!s} --headless --plot-vars={!s}'.format(script, data, vars)
    with tmpdir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert len(tmpdir.listdir()) == 1


def test_single_run_multiplot(request, tmpdir, run_in_shell_wrapper):
    test_root = request.fspath
    script = test_root.join('../../jetto_tools/results_gui.py')
    data = test_root.join('../../testdata/jetto-sanco-pencil-esco-qlknn')
    vars = 'TE,TI'
    cmd = 'python {!s} {!s} --headless --plot-vars={!s}'.format(script, data, vars)
    with tmpdir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert len(tmpdir.listdir()) == 1


def test_multi_run_multiplot(request, tmpdir, run_in_shell_wrapper):
    test_root = request.fspath
    script = test_root.join('../../jetto_tools/results_gui.py')
    data = test_root.join('../../testdata/jetto-sanco-pencil-esco-qlknn')
    data2_name = 'jetto-sanco-pencil-esco-qlknn-copy'
    data2 = tmpdir.mkdir(data2_name)
    data.copy(data2)
    vars = 'TE,TI'
    cmd = 'python {!s} {!s} {!s} --headless --plot-vars={!s}'.format(script, data, data2, vars)
    with tmpdir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert len(tmpdir.listdir()) == 1 + 1


################
# CLI plotting #
################

@pytest.fixture()
def default_plotcase(request, tmpdir):
    test_root = request.fspath
    script = test_root.join('../../jetto_tools/results_gui.py')
    data = test_root.join('../../testdata/jetto-sanco-pencil-esco-qlknn')
    data2_name = 'jetto-sanco-pencil-esco-qlknn-copy'
    data2 = tmpdir.mkdir(data2_name)
    data.copy(data2)
    vars = 'TE,TI'
    case = DefaultPlotcase(tmpdir, [data, data2], script, vars)
    return case


def test_set_file_var_not_found(default_plotcase, run_in_shell_wrapper):
    cmd = 'python {!s} {!s} {!s} --headless --file SSP --plot-vars={!s}; exit 0'.format(
        default_plotcase.script, default_plotcase.data[0], default_plotcase.data[1], default_plotcase.vars)
    with default_plotcase.dir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert 'not found in run' in output.stderr
    assert len(default_plotcase.dir.listdir()) == 1


def test_set_file_and_vars(default_plotcase, run_in_shell_wrapper):
    cmd = 'python {!s} {!s} {!s} --headless --file SSP --plot-vars=GRP2 --xvar=xvec1'.format(
        default_plotcase.script, default_plotcase.data[0], default_plotcase.data[1] )
    with default_plotcase.dir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert len(default_plotcase.dir.listdir()) == 1 + 1


def test_plot_xvec2var_vs_time(default_plotcase, run_in_shell_wrapper):
    cmd = 'python {!s} {!s} {!s} --headless --file JSP --plot-vars=SH --plot-vs-time --slicevar=xvec2'.format(
        default_plotcase.script, default_plotcase.data[0], default_plotcase.data[1] )
    with default_plotcase.dir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert len(default_plotcase.dir.listdir()) == 1 + 1


def test_plot_compvar(default_plotcase, run_in_shell_wrapper):
    cmd = 'python {!s} {!s} {!s} --headless --file JSP --plot-vars=TE --compvar=TI --compfunc="comp / var"'.format(
        default_plotcase.script, default_plotcase.data[0], default_plotcase.data[1] )
    with default_plotcase.dir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert len(default_plotcase.dir.listdir()) == 1 + 1


def test_plot_compvar_with_xvar2vars(default_plotcase, run_in_shell_wrapper):
    cmd = 'python {!s} {!s} {!s} --headless --file JSP --plot-vars=TE --compvar=SH --compfunc="comp / var"'.format(
        default_plotcase.script, default_plotcase.data[0], default_plotcase.data[1] )
    with default_plotcase.dir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert len(default_plotcase.dir.listdir()) == 1 + 1


def test_plot_compvar_with_xvar2vars_vs_time(default_plotcase, run_in_shell_wrapper):
    cmd = 'python {!s} {!s} {!s} --headless --file JSP --plot-vars=TE --compvar=SH --compfunc="comp / var" --plot-vs-time'.format(
        default_plotcase.script, default_plotcase.data[0], default_plotcase.data[1] )
    with default_plotcase.dir.as_cwd():
        output = run_in_shell_wrapper(cmd)
    assert len(default_plotcase.dir.listdir()) == 1 + 1
