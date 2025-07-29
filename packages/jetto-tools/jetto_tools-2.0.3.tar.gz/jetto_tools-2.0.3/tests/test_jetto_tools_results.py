import pytest
import json
import yaml
import os
from unittest.mock import call

import numpy as np

from jetto_tools import results
import jetto_tools.config
import jetto_tools.job as job



class TestGrayResultHandling:
    def test_load_fort_604(self, pytestconfig):
        [file] = results.GrayFortFile.load(
            pytestconfig.rootdir / 'testdata/results/fort.604'
        )

        df = file.data

        # make sure basic string handling works
        assert file.get_value('iox') == '2'
        assert file.get_value('iox', category='ANT') == '2'

        with pytest.raises(KeyError):
            file.get_value('iox', category='DOES NOT EXIST')

        # check int and float handling
        assert file.get_int('nrayr') == 8
        assert file.get_int('nrayth') == 12

        assert file.get_float('power') == 1e-6

        assert df.shape == (1340, 26)
        assert 'rhot' in df.columns
        assert df.loc[4, 'sst'] == 0.01

    def test_load_eqdsk(self, pytestconfig):
        file = results.EqdskFile.load(
            pytestconfig.rootdir / 'testdata/results/jetto_600.100000.eqdsk'
        )

        nh = nw = 101
        nbdry, nlim = 162, 0

        assert file.nw == nw
        assert file.nh == nh
        assert file.nbdry == nbdry
        assert file.nlim == nlim

        assert file.psip_n.shape == (nw,)
        assert file.F.shape == (nw,)
        assert file.p.shape == (nw,)
        assert file.ffprime.shape == (nw,)
        assert file.pprime.shape == (nw,)
        assert file.qpsi.shape == (nw,)

        assert file.psirz.shape == (nh, nw)

        assert file.rbdry.shape == (nbdry,)
        assert file.zbdry.shape == (nbdry,)

        # Krassimir's code turns zero length arrays into an array
        # containing a zero...  not sure why!
        assert file.xlim.shape == (nlim or 1,)
        assert file.ylim.shape == (nlim or 1,)


@pytest.fixture()
def runs_home(tmpdir):
    dir = tmpdir.mkdir('common').mkdir('cmg').mkdir('user')

    return dir


@pytest.fixture()
def run_root(runs_home):
    dir = runs_home.mkdir('jetto').mkdir('runs')

    return dir


class TestSignalSummary:
    @pytest.fixture(autouse=True)
    def name(self):
        return 'CUR'

    @pytest.fixture(autouse=True)
    def signal(self):
        return np.random.rand(10)

    def test_has_expected_name(self, name, signal):
        summary = results.SignalSummary(name, signal)

        assert summary.name == name

    def test_has_expected_value(self, name, signal):
        summary = results.SignalSummary(name, signal)

        assert summary.value == signal[-1]

    @pytest.mark.parametrize('signal, std', [(np.ones(10), np.std(np.ones(2))),
                                             (np.arange(0, 10, 1), np.std(np.arange(8, 10, 1))),
                                             (np.arange(10, 0, -1), np.std(np.arange(2, 0, -1)))],
                             ids=[1, 2, 3])
    def test_has_expected_convergence(self, name, signal, std):
        summary = results.SignalSummary(name, signal)

        assert np.isclose(summary.convergence, std)


class TestRetrievePointSummary:
    @pytest.fixture(autouse=True)
    def rundir(self, tmpdir):
        return tmpdir.mkdir('rundir')

    @pytest.fixture(autouse=True)
    def serialisation(self, rundir):
        f = rundir.join('serialisation.json')

        d = {'parameters': {'foo': 1, 'bar': 2}}
        f.write(json.dumps(d))

        return f

    @pytest.fixture
    def jst_signals(self):
        return {
            'CUR': np.array([np.random.rand(10)]),
            'PFUS': np.array([np.random.rand(10)]),
            'QFUS': np.array([np.random.rand(10)])
        }

    @pytest.fixture(autouse=True)
    def jst(self, rundir):
        f = rundir.join('jetto.jst')
        f.write('')

        return f

    @pytest.fixture(autouse=True)
    def summary_signals(self):
        return ['CUR', 'PFUS']

    @pytest.fixture(autouse=True)
    def mock_read_binary(self, mocker, jst_signals):
        mock = mocker.patch('jetto_tools.results.read_binary_file')
        mock.return_value = jst_signals

        return mock

    def test_raises_if_rundir_not_found(self, rundir):
        rundir.remove()

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_point_summary(rundir.strpath)

    def test_raises_if_serialisation_not_found(self, rundir, serialisation):
        serialisation.remove()

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_point_summary(rundir.strpath)

    def test_raises_if_serialisation_cannot_be_parsed(self, rundir, serialisation):
        serialisation.write('foo')

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_point_summary(rundir.strpath)

    def test_raises_if_serialisation_does_not_contain_params(self, rundir, serialisation):
        d = json.loads(serialisation.read())
        del d['parameters']
        serialisation.write(json.dumps(d))

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_point_summary(rundir.strpath)

    def test_returned_params_are_those_of_serialisation(self, rundir, serialisation):
        expected_parameters = json.loads(serialisation.read())['parameters']

        actual_parameters = results.retrieve_point_summary(rundir.strpath).parameters

        assert actual_parameters == expected_parameters

    def test_raises_if_jst_file_not_found(self, rundir, jst):
        jst.remove()

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_point_summary(rundir.strpath)

    def test_calls_read_binary_file_on_jst(self, rundir, jst, mock_read_binary):
        _ = results.retrieve_point_summary(rundir.strpath)

        mock_read_binary.assert_called_once_with(jst.strpath)

    def test_returns_expected_signals_from_jst(self, rundir, jst_signals, summary_signals):
        summary = results.retrieve_point_summary(rundir.strpath, summary_signals)
        actual_signals = summary.signals

        expected_signals = {k: results.SignalSummary(k, jst_signals[k][0]) for k in summary_signals}

        assert all(expected_signals[k].name == actual_signals[k].name and
                   expected_signals[k].value == actual_signals[k].value and
                   expected_signals[k].convergence == actual_signals[k].convergence for k in expected_signals)

    def test_raises_if_expected_signal_not_found(self, rundir, jst_signals, summary_signals):
        del jst_signals['CUR']

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_point_summary(rundir.strpath, summary_signals)

    @pytest.mark.parametrize('status', [results.Status.SUCCESSFUL,
                                        results.Status.FAILED,
                                        results.Status.UNKNOWN],
                             ids=['Successful', 'Failed', 'Unknown'])
    def test_point_summary_job_status(self, rundir, status, summary_signals, mocker):
        mock = mocker.patch('jetto_tools.results.Job')
        mock.return_value.status.return_value = status

        summary = results.retrieve_point_summary(rundir, summary_signals)

        assert summary.status == status


class TestRetrieveScanSummary:
    @pytest.fixture
    def signals(self):
        return [
            'CUR',
            'PFUS'
        ]

    @pytest.fixture(autouse=True)
    def config(self):
        return {
            'parameters': {
                'scan1': jetto_tools.config.Scan(sorted(np.random.rand(5))),
                'scan2': jetto_tools.config.Scan(sorted(np.random.rand(10))),
                'scan3': jetto_tools.config._CoupledScan(sorted(np.random.rand(15)), ['scan4']),
                'scan4': jetto_tools.config._CoupledScan(sorted(np.random.rand(15)), ['scan3']),
                'foo': 1
            }
        }

    @pytest.fixture(autouse=True)
    def serialisation(self, run_root, config):
        f = run_root.join('serialisation.json')

        f.write(json.dumps(config, default=jetto_tools.config._CoupledScan.to_json))

        return f

    @pytest.fixture(autouse=True)
    def mock_point_summaries_to_scan_summary(self, mocker):
        mock = mocker.patch('jetto_tools.results._point_summaries_to_scan_summary')

        def _side_effect(signals, scans, point_summaries):
            return results.ScanSummary(params=list(scans), param_values=scans, signals=signals,
                                       signals_values=None, signals_convergences=None)

        mock.side_effect = _side_effect

        return mock

    @pytest.fixture(autouse=True)
    def pointdirs(self, run_root, config):
        n_pointdirs = len(config['parameters']['scan1']) * len(config['parameters']['scan2'])

        dirs = [run_root.mkdir('point_{:03d}'.format(i)) for i in range(n_pointdirs)]

        return dirs

    @pytest.fixture(autouse=True)
    def mock_retrieve_point_summary(self, mocker):
        return mocker.patch('jetto_tools.results.retrieve_point_summary')

    @pytest.fixture(autouse=True)
    def mock_retrieve_point_summary(self, mocker):
        return mocker.patch('jetto_tools.results.retrieve_point_summary')

    def test_raises_if_run_root_not_found(self, run_root):
        run_root.remove()

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_scan_summary(run_root.strpath)

    def test_raises_if_serialisation_not_found(self, run_root, serialisation):
        serialisation.remove()

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_scan_summary(run_root.strpath)

    def test_raises_if_no_parameters_in_serialisation(self, run_root, serialisation):
        serialisation_contents = json.loads(serialisation.read())
        del serialisation_contents['parameters']
        serialisation.write(json.dumps(serialisation_contents))

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_scan_summary(run_root.strpath)

    def test_raises_if_no_scans_in_serialisation(self, run_root, config):
        config['parameters'] = {
            k: v for k, v in config['parameters'].items() if not isinstance(v, jetto_tools.config.Scan)
        }
        with open(run_root / 'serialisation.json', 'w') as f:
            f.write(json.dumps(config, default=jetto_tools.config._CoupledScan.to_json))

        with pytest.raises(results.SummaryError):
            _ = results.retrieve_scan_summary(run_root.strpath)

    def test_summary_lists_scan_parameters(self, run_root):
        summary = results.retrieve_scan_summary(run_root.strpath)

        assert summary.params == [('scan1', ), ('scan2', ), ('scan3', 'scan4')]

    @pytest.mark.parametrize('param', ['scan1', 'scan2'])
    def test_summary_lists_uncoupled_scan_values(self, run_root, param, config):
        summary = results.retrieve_scan_summary(run_root.strpath)

        assert np.array_equal(summary.param_values[(param, )][0], np.sort(list(config['parameters'][param])))

    def test_summary_lists_coupled_scan_values(self, run_root, config):
        summary = results.retrieve_scan_summary(run_root.strpath)

        assert np.array_equal(summary.param_values[('scan3', 'scan4')][0], np.sort(list(config['parameters']['scan3']))) \
               and np.array_equal(summary.param_values[('scan3', 'scan4')][1], np.sort(list(config['parameters']['scan4'])))

    def test_summary_includes_signals(self, run_root, signals):
        summary = results.retrieve_scan_summary(run_root.strpath, signals=signals)

        assert summary.signals == signals

    def test_summary_allows_no_point_directories(self, run_root, signals, pointdirs):
        _ = [pointdir.remove() for pointdir in pointdirs]

        _ = results.retrieve_scan_summary(run_root.strpath, signals=signals)

    def test_summary_allows_point_directory_missing(self, run_root, signals, pointdirs):
        pointdirs[0].remove()

        _ = results.retrieve_scan_summary(run_root.strpath, signals=signals)


class TestTransform1DScanSummary:
    @pytest.fixture
    def signals(self):
        return [
            'CUR',
            'PFUS'
        ]

    @pytest.fixture
    def scans(self):
        return {
            ('param', ): (np.array([0, 1, 2, 3]), )
        }

    @pytest.fixture
    def signal_summary_generator(self, signals):
        def _generator():
            return {signal: results.SignalSummary(signal, np.random.rand(100)) for signal in signals}

        return _generator

    @pytest.fixture
    def point_summaries(self, signal_summary_generator, scans):
        return {
            'point_000': results.PointSummary(
                parameters={'param': scans[('param', )][0][0]}, signals=signal_summary_generator(),
                status=results.Status.SUCCESSFUL),
            'point_001': results.PointSummary(
                parameters={'param': scans[('param', )][0][1]}, signals=signal_summary_generator(),
                status=results.Status.SUCCESSFUL),
            'point_002': results.PointSummary(
                parameters={'param': scans[('param', )][0][2]}, signals=signal_summary_generator(),
                status=results.Status.SUCCESSFUL),
            'point_003': results.PointSummary(
                parameters={'param': scans[('param', )][0][3]}, signals=signal_summary_generator(),
                status=results.Status.SUCCESSFUL)
        }

    def test_summary_lists_scan_parameters(self, signals, scans, point_summaries):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert scan_summary.params == list(scans)

    def test_summary_lists_scan_values(self, signals, scans, point_summaries):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.param_values[('param', )], scans[('param', )])

    def test_summary_includes_signals(self, signals, scans, point_summaries):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert scan_summary.signals == signals

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_values_in_standard_order(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.signals_values[signal],
                              np.array([point_summaries['point_000'].signals[signal].value,
                                        point_summaries['point_001'].signals[signal].value,
                                        point_summaries['point_002'].signals[signal].value,
                                        point_summaries['point_003'].signals[signal].value]))

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_convergences_in_standard_order(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.signals_convergences[signal],
                              np.array([point_summaries['point_000'].signals[signal].convergence,
                                        point_summaries['point_001'].signals[signal].convergence,
                                        point_summaries['point_002'].signals[signal].convergence,
                                        point_summaries['point_003'].signals[signal].convergence]))

    @pytest.fixture
    def randomised_point_summaries(self, point_summaries):
        point_summaries['point_000'].parameters['param'], point_summaries['point_001'].parameters['param'] = \
            point_summaries['point_001'].parameters['param'], point_summaries['point_000'].parameters['param']

        point_summaries['point_002'].parameters['param'], point_summaries['point_003'].parameters['param'] = \
            point_summaries['point_003'].parameters['param'], point_summaries['point_002'].parameters['param']

        return point_summaries

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_values_in_random_order(self, signals, scans, randomised_point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, randomised_point_summaries)

        assert np.array_equal(scan_summary.signals_values[signal],
                              np.array([randomised_point_summaries['point_001'].signals[signal].value,
                                        randomised_point_summaries['point_000'].signals[signal].value,
                                        randomised_point_summaries['point_003'].signals[signal].value,
                                        randomised_point_summaries['point_002'].signals[signal].value]))

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_convergences_in_random_order(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.signals_convergences[signal],
                              np.array([point_summaries['point_000'].signals[signal].convergence,
                                        point_summaries['point_001'].signals[signal].convergence,
                                        point_summaries['point_002'].signals[signal].convergence,
                                        point_summaries['point_003'].signals[signal].convergence]))

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_no_points_masked(self, signals, scans, point_summaries, signal, attr):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert not getattr(scan_summary, attr)[signal].mask.any()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_all_points_masked_if_no_points(self, signals, scans, point_summaries, signal, attr):
        point_summaries = {}

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert getattr(scan_summary, attr)[signal].mask.all()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_point_masked_if_missing(self, signals, scans, point_summaries, signal, attr):
        del point_summaries['point_001']

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(np.ma.getmaskarray(getattr(scan_summary, attr)[signal]),
                              np.array([False, True, False, False]))

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    @pytest.mark.parametrize('status', [results.Status.FAILED, results.Status.UNKNOWN],
                             ids=['Failed', 'Unknown'])
    def test_all_points_masked_by_status(self, signals, scans, point_summaries, status, signal, attr):
        for summary in point_summaries:
            point_summaries[summary].status = status

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert getattr(scan_summary, attr)[signal].mask.all()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    @pytest.mark.parametrize('status', [results.Status.FAILED, results.Status.UNKNOWN],
                             ids=['Failed', 'Unknown'])
    def test_point_masked_by_status(self, signals, scans, point_summaries, status, signal, attr):
        point_summaries['point_001'].status = status

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(np.ma.getmaskarray(getattr(scan_summary, attr)[signal]),
                              np.array([False, True, False, False]))


class TestTransform2DScanSummary:
    @pytest.fixture
    def signals(self):
        return [
            'CUR',
            'PFUS'
        ]

    @pytest.fixture
    def scans(self):
        return {
            ('param1', ): (np.sort(np.random.rand(2)), ),
            ('param2', ): (np.sort(np.random.rand(3)), )
        }

    @pytest.fixture
    def signal_summary_generator(self, signals):
        def _generator():
            return {signal: results.SignalSummary(signal, np.random.rand(100)) for signal in signals}

        return _generator

    @pytest.fixture
    def point_summaries(self, signal_summary_generator, scans):
        return {
            'point_000': results.PointSummary(
                parameters={
                    'param1': scans[('param1', )][0][0],
                    'param2': scans[('param2', )][0][0]
                }, signals=signal_summary_generator(), status=results.Status.SUCCESSFUL),
            'point_001': results.PointSummary(
                parameters={
                    'param1': scans[('param1', )][0][0],
                    'param2': scans[('param2', )][0][1]
                }, signals=signal_summary_generator(), status=results.Status.SUCCESSFUL),
            'point_002': results.PointSummary(
                parameters={
                    'param1': scans[('param1', )][0][0],
                    'param2': scans[('param2', )][0][2]
                }, signals=signal_summary_generator(), status=results.Status.SUCCESSFUL),
            'point_003': results.PointSummary(
                parameters={
                    'param1': scans[('param1', )][0][1],
                    'param2': scans[('param2', )][0][0]
                }, signals=signal_summary_generator(), status=results.Status.SUCCESSFUL),
            'point_004': results.PointSummary(
                parameters={
                    'param1': scans[('param1', )][0][1],
                    'param2': scans[('param2', )][0][1]
                }, signals=signal_summary_generator(), status=results.Status.SUCCESSFUL),
            'point_005': results.PointSummary(
                parameters={
                    'param1': scans[('param1', )][0][1],
                    'param2': scans[('param2', )][0][2]
                }, signals=signal_summary_generator(), status=results.Status.SUCCESSFUL)
        }

    def test_summary_lists_scan_parameters(self, signals, scans, point_summaries):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert scan_summary.params == list(scans)

    @pytest.mark.parametrize('param', ['param1', 'param2'])
    def test_summary_lists_scan_values(self, signals, scans, point_summaries, param):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.param_values[(param, )], scans[(param, )])

    def test_summary_includes_signals(self, signals, scans, point_summaries):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert scan_summary.signals == signals

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_sizes(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.shape(scan_summary.signals_values[signal]) == (len(scans[('param1', )][0]),
                                                                 len(scans[('param2', )][0]))

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_values(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.signals_values[signal],
                              np.array([[point_summaries['point_000'].signals[signal].value,
                                         point_summaries['point_001'].signals[signal].value,
                                         point_summaries['point_002'].signals[signal].value],
                                        [point_summaries['point_003'].signals[signal].value,
                                         point_summaries['point_004'].signals[signal].value,
                                         point_summaries['point_005'].signals[signal].value]]))

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_convergence(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.signals_convergences[signal],
                              np.array([[point_summaries['point_000'].signals[signal].convergence,
                                         point_summaries['point_001'].signals[signal].convergence,
                                         point_summaries['point_002'].signals[signal].convergence],
                                        [point_summaries['point_003'].signals[signal].convergence,
                                         point_summaries['point_004'].signals[signal].convergence,
                                         point_summaries['point_005'].signals[signal].convergence]]))

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_no_points_masked(self, signals, scans, point_summaries, signal, attr):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert not getattr(scan_summary, attr)[signal].mask.any()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_all_points_masked_if_no_points(self, signals, scans, point_summaries, signal, attr):
        point_summaries = {}

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert getattr(scan_summary, attr)[signal].mask.all()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_points_masked_if_missing(self, signals, scans, point_summaries, signal, attr):
        del point_summaries['point_001']
        del point_summaries['point_005']

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(np.ma.getmaskarray(getattr(scan_summary, attr)[signal]),
                              np.array([[False, True, False],
                                        [False, False, True]]))

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    @pytest.mark.parametrize('status', [results.Status.FAILED, results.Status.UNKNOWN],
                             ids=['Failed', 'Unknown'])
    def test_all_points_masked_by_status(self, signals, scans, point_summaries, status, signal, attr):
        for summary in point_summaries:
            point_summaries[summary].status = status

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert getattr(scan_summary, attr)[signal].mask.all()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    @pytest.mark.parametrize('status', [results.Status.FAILED, results.Status.UNKNOWN],
                             ids=['Failed', 'Unknown'])
    def test_point_masked_by_status(self, signals, scans, point_summaries, status, signal, attr):
        point_summaries['point_001'].status = status
        point_summaries['point_005'].status = status

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(np.ma.getmaskarray(getattr(scan_summary, attr)[signal]),
                              np.array([[False, True, False],
                                        [False, False, True]]))


class TestTransformCoupledScanSummary:
    @pytest.fixture
    def signals(self):
        return [
            'CUR',
            'PFUS'
        ]

    @pytest.fixture
    def scans(self):
        return {
            ('param1', 'param2'): (np.sort(np.random.rand(2)), np.sort(np.random.rand(2)))
        }

    @pytest.fixture
    def signal_summary_generator(self, signals):
        def _generator():
            return {signal: results.SignalSummary(signal, np.random.rand(100)) for signal in signals}

        return _generator

    @pytest.fixture
    def point_summaries(self, signal_summary_generator, scans):
        index = ('param1', 'param2')
        return {
            'point_000': results.PointSummary(
                parameters={
                    'param1': scans[index][0][0],
                    'param2': scans[index][1][0]
                }, signals=signal_summary_generator(), status=results.Status.SUCCESSFUL),
            'point_001': results.PointSummary(
                parameters={
                    'param1': scans[index][0][1],
                    'param2': scans[index][1][1]
                }, signals=signal_summary_generator(), status=results.Status.SUCCESSFUL)
        }

    def test_summary_lists_scan_parameters(self, signals, scans, point_summaries):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert scan_summary.params == list(scans)

    @pytest.mark.parametrize('index', [0, 1], ids=['param1', 'param2'])
    def test_summary_lists_scan_values(self, signals, scans, point_summaries, index):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.param_values[('param1', 'param2')][index],
                              scans[('param1', 'param2')][index])

    def test_summary_includes_signals(self, signals, scans, point_summaries):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert scan_summary.signals == signals

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_sizes(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.shape(scan_summary.signals_values[signal]) == (len(scans[('param1', 'param2')][0]), )

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_values(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.signals_values[signal],
                              np.array([point_summaries['point_000'].signals[signal].value,
                                        point_summaries['point_001'].signals[signal].value]))

    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_signal_convergence(self, signals, scans, point_summaries, signal):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(scan_summary.signals_convergences[signal],
                              np.array([point_summaries['point_000'].signals[signal].convergence,
                                        point_summaries['point_001'].signals[signal].convergence]))

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_no_points_masked(self, signals, scans, point_summaries, signal, attr):
        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert not getattr(scan_summary, attr)[signal].mask.any()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_all_points_masked_if_no_points(self, signals, scans, point_summaries, signal, attr):
        point_summaries = {}

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert getattr(scan_summary, attr)[signal].mask.all()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    def test_points_masked_if_missing(self, signals, scans, point_summaries, signal, attr):
        del point_summaries['point_001']

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(np.ma.getmaskarray(getattr(scan_summary, attr)[signal]),
                              np.array([False, True]))

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    @pytest.mark.parametrize('status', [results.Status.FAILED, results.Status.UNKNOWN],
                             ids=['Failed', 'Unknown'])
    def test_all_points_masked_by_status(self, signals, scans, point_summaries, status, signal, attr):
        for summary in point_summaries:
            point_summaries[summary].status = status

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert getattr(scan_summary, attr)[signal].mask.all()

    @pytest.mark.parametrize('attr', ['signals_values', 'signals_convergences'])
    @pytest.mark.parametrize('signal', ['CUR', 'PFUS'])
    @pytest.mark.parametrize('status', [results.Status.FAILED, results.Status.UNKNOWN],
                             ids=['Failed', 'Unknown'])
    def test_point_masked_by_status(self, signals, scans, point_summaries, status, signal, attr):
        point_summaries['point_001'].status = status

        scan_summary = results._point_summaries_to_scan_summary(signals, scans, point_summaries)

        assert np.array_equal(np.ma.getmaskarray(getattr(scan_summary, attr)[signal]),
                              np.array([False, True]))


class TestScanIndexFromPoint:
    @pytest.fixture
    def scans(self):
        return {
            ('param1', ): (np.array([0.0, 1.0]), ),
            ('param2', ): (np.array([2.0, 3.0, 4.0]), )
        }

    @pytest.mark.parametrize('param1, param2, index',
                             [(0.0, 2.0, (0, 0)),
                              (1.0, 2.0, (1, 0)),
                              (0.0, 3.0, (0, 1)),
                              (1.0, 4.0, (1, 2))],
                             ids=range(4))
    def test_expected_index_is_returned(self, param1, param2, index, scans):
        point = {
            'param1': param1,
            'param2': param2
        }

        assert index == results._scan_index_from_point([('param1', ), ('param2', )], scans, point)

    @pytest.fixture
    def coupled_scans(self):
        return {
            ('coupled_param1', 'coupled_param2'): (np.array([0.0, 1.0]), np.array([2.0, 3.0])),
            ('param1', ): (np.array([4.0, 5.0, 6.0]), )
        }

    @pytest.mark.parametrize('coupled_param1, coupled_param2, param1, index',
                             [(0.0, 2.0, 4.0, (0, 0)),
                              (1.0, 3.0, 4.0, (1, 0)),
                              (0.0, 2.0, 5.0, (0, 1)),
                              (1.0, 3.0, 6.0, (1, 2))],
                             ids=range(4))
    def test_index_in_coupled_case(self, coupled_scans, coupled_param1, coupled_param2, param1, index):
        point = {
            'coupled_param1': coupled_param1,
            'coupled_param2': coupled_param2,
            'param1': param1
        }

        assert index == results._scan_index_from_point([('coupled_param1', 'coupled_param2'), ('param1', )],
                                                       coupled_scans, point)


class TestAggregateScans:
    @pytest.fixture
    def raw_scans(self):
        return {
            'param1': jetto_tools.config.Scan(np.random.rand(4)),
            'param2': jetto_tools.config._CoupledScan(np.random.rand(4), ['param3']),
            'param3': jetto_tools.config._CoupledScan(np.random.rand(4), ['param2']),
            'param4': jetto_tools.config._CoupledScan(np.random.rand(4), ['param5', 'param6']),
            'param5': jetto_tools.config._CoupledScan(np.random.rand(4), ['param4', 'param6']),
            'param6': jetto_tools.config._CoupledScan(np.random.rand(4), ['param4', 'param5']),
        }

    def test_noncoupled_scan_unchanged(self, raw_scans):
        aggregated_scans = results._aggregate_scans(raw_scans)

        assert aggregated_scans[('param1', )] == ((raw_scans['param1']), )

    def test_pair_of_coupled_scans(self, raw_scans):
        aggregated_scans = results._aggregate_scans(raw_scans)

        assert aggregated_scans[('param2', 'param3')] == (raw_scans['param2'], raw_scans['param3'])

    def test_triple_of_coupled_scans(self, raw_scans):
        aggregated_scans = results._aggregate_scans(raw_scans)

        assert aggregated_scans[('param4', 'param5', 'param6')] == (raw_scans['param4'], raw_scans['param5'], raw_scans['param6'])

    def test_raises_if_inconsistent_coupling(self, raw_scans):
        raw_scans['param3'] = jetto_tools.config._CoupledScan(raw_scans['param3'], ['param4'])

        with pytest.raises(results.SummaryError):
            aggregated_scans = results._aggregate_scans(raw_scans)


class TestLabelPoint:

    @pytest.fixture(autouse=True)
    def pointdir(self, tmpdir):
        return tmpdir.mkdir('point_000')

    @pytest.fixture(autouse=True)
    def config(self):
        return {
            'parameters': {
                'param_a': 0,
                'param_b': 1
            }
        }

    @pytest.fixture(autouse=True)
    def serialisation(self, pointdir, config):
        path = pointdir.join('serialisation.json')
        with open(path, 'w') as f:
            json.dump(config, f)

        return path

    def test_raises_if_pointdir_does_not_exist(self, pointdir):
        pointdir.remove()

        with pytest.raises(results.ResultsError):
            results.label_point(pointdir)

    def test_raises_if_serialisation_does_not_exist(self, pointdir, serialisation):
        serialisation.remove()

        with pytest.raises(results.ResultsError):
            results.label_point(pointdir)

    def test_creates_label_file(self, pointdir):
        results.label_point(pointdir)

        assert os.path.isfile(os.path.join(pointdir, 'labels.yaml'))

    def _read_labels_file(self, pointdir):
        with open(os.path.join(pointdir, 'labels.yaml')) as f:
            labels = yaml.safe_load(f)

        return labels

    def test_lists_values_of_scan_params(self, pointdir, config):
        results.label_point(pointdir, scan_params=['param_a', 'param_b'])

        labels = self._read_labels_file(pointdir)

        assert labels['scan-param-param_a'] == config['parameters']['param_a'] and \
               labels['scan-param-param_b'] == config['parameters']['param_b']

    def test_lists_no_values_of_scan_params(self, pointdir):
        results.label_point(pointdir, scan_params=[])

        labels = self._read_labels_file(pointdir)

        assert all(not label.startswith('scan-param-') for label in labels)

    def test_raises_if_scan_param_not_found(self, pointdir):
        with pytest.raises(results.ResultsError):
            results.label_point(pointdir, scan_params=['param_c'])

    @pytest.mark.parametrize('catalogue_id', [None, 'user/machine/88888/jan0101/seq-1'],
                             ids=['No id', 'An id'])
    def test_labels_contains_catalogue_id(self, pointdir, catalogue_id):
        results.label_point(pointdir, template=catalogue_id)

        labels = self._read_labels_file(pointdir)

        assert labels['template'] == catalogue_id

    @pytest.mark.parametrize('point_index', [None, 1], ids=['No index', 'An index'])
    def test_labels_contains_point_index(self, pointdir, point_index):
        results.label_point(pointdir, point_index=point_index)

        labels = self._read_labels_file(pointdir)

        assert labels['point-index'] == point_index

    @pytest.mark.parametrize('scan_label', [None, 'foo/bar'], ids=['No scan label', 'A scan label'])
    def test_labels_contains_scan_label(self, pointdir, scan_label):
        results.label_point(pointdir, scan_label=scan_label)

        labels = self._read_labels_file(pointdir)

        assert labels['scan-label'] == scan_label

    @pytest.mark.parametrize('run_status', [job.Status.SUCCESSFUL, job.Status.FAILED, job.Status.UNKNOWN])
    def test_labels_contain_run_status(self, pointdir, run_status, mocker):
        mock = mocker.patch('jetto_tools.job.Job.status')
        mock.return_value = run_status

        results.label_point(pointdir)
        labels = self._read_labels_file(pointdir)

        assert labels['run-status'] == jetto_tools.job.Status.to_string(run_status)


class TestLabelScan:

    @pytest.fixture(autouse=True)
    def scandir(self, tmpdir):
        return tmpdir.mkdir('myscan')

    @pytest.fixture(autouse=True)
    def config(self):
        return {
            'parameters': {
                'param_a': {
                    '__class__': 'Scan',
                    '__value__': [0, 1]
                },
                'param_b': {
                    '__class__': 'Scan',
                    '__value__': [2, 3]
                }
            }
        }

    @pytest.fixture(autouse=True)
    def serialisation(self, scandir, config):
        path = scandir.join('serialisation.json')
        with open(path, 'w') as f:
            json.dump(config, f)

        return path

    @pytest.fixture(autouse=True)
    def pointdirs(self, scandir):
        dirs = [scandir.mkdir('point_000'), scandir.mkdir('point_001'),
                scandir.mkdir('point_002'), scandir.mkdir('point_003')]

        return dirs

    @pytest.fixture(autouse=True)
    def mock_label_point(self, mocker):
        mock = mocker.patch('jetto_tools.results.label_point')

        return mock

    def test_raises_if_scandir_does_not_exist(self, scandir):
        scandir.remove()

        with pytest.raises(results.ResultsError):
            results.label_scan(scandir)

    def test_raises_if_serialisation_not_found(self, scandir, serialisation):
        serialisation.remove()

        with pytest.raises(results.ResultsError):
            results.label_scan(scandir)

    @pytest.mark.parametrize('point_index', range(0, 4))
    def test_calls_label_point(self, scandir, point_index, pointdirs, mock_label_point):
        results.label_scan(scandir, template='foo', scan_label='myscan')

        mock_label_point.assert_has_calls([call(pointdirs[point_index].strpath, template='foo',
                                                point_index=point_index, scan_params=['param_a', 'param_b'],
                                                scan_label='myscan')])

