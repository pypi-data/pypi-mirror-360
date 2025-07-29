.. _results-label:

==============
Results module
==============

Introduction
============

The ``results`` module provides support for reading and analysing the results of JETTO runs and scans.

Scan summary
============

The ``results`` module provides support for aggregating and analysing the results of a scan. The primary function of interest
is ``retrieve_scan_summary``. It takes the path to the root of the directory tree containing the scan results:

.. highlight:: python

>>> import jetto_tools.results
>>> summary = jetto_tools.results.retrieve_scan_summary('/home/user/jetto/runs/my_scan')

Note that if you have used the batch system to run your scan, the directory tree containing the scan results will simply
be that of the submitted point directories, typically under ``/home/user/jetto/runs``. If you are using PROMINENCE to
run your scan, the directory tree containing the scan results may be elsewhere, depending on the ``outdir`` you
selected when you :ref:`downloaded<prominence-download-label>` the PROMINENCE results .

In the example above, the returned ``summary`` object is of type ``ScanSummary``. It has a number of
attributes. The first is ``params``, which is a list of the parameters which were scanned e.g.

.. highlight:: python

>>> summary.params
[('e_bohm_coeff', ), ('e_gbohm_coeff', )]

In this case, the scan was 2D. Note that each element of the list is a tuple. In the case of simple n-dimensional scans,
each tuple only contains a single parameter. In the case of *coupled* scans, each scan in a souple is contained in the
same tuple. For example, if ``summary`` contained only a coupled scan between parameters ``e_bohm_coeff`` and
``e_gbohm_coeff``, then the ``params`` attribute would show:

.. highlight:: python

>>> summary.params
[('e_bohm_coeff', 'e_gbohm_coeff')]

The values of the scanned parameters can be obtained from the ``param_values``
attribute, which is a dictionary e.g.

.. highlight:: python

>>> summary.param_values[('e_bohm_coeff', )]
(array([1.92100000e-03, 2.86593137e-03, 3.84200000e-03, 6.37885349e-03,
       9.51658319e-03, 1.41977482e-02, 2.11815574e-02, 3.16006715e-02,
       4.71449014e-02, 7.03352689e-02, 1.04932875e-01, 1.56548890e-01,
       2.33554594e-01, 3.48439062e-01, 5.19834688e-01, 7.75539062e-01,
       1.15702328e+00, 1.72615789e+00, 2.57524730e+00, 3.84200000e+00]), )

The values of individual scanned parameters are always expressed as 1D ``numpy`` arrays. Within the array, the values
are stored in ascending order (irrespective of the order specified in the original scan configuration). Note that, in
a similar manner to the ``params`` attribute, all keys and values are tuples within the ``param_values`` dictionary,
and coupled scans are grouped together in the same tuple e.g.

>>> summary.param_values[('e_bohm_coeff', 'e_gbohm_coeff')]
(array([1.92100000e-03, 2.86593137e-03, 3.84200000e-03, 6.37885349e-03,
       9.51658319e-03, 1.41977482e-02, 2.11815574e-02, 3.16006715e-02,
       4.71449014e-02, 7.03352689e-02, 1.04932875e-01, 1.56548890e-01,
       2.33554594e-01, 3.48439062e-01, 5.19834688e-01, 7.75539062e-01,
       1.15702328e+00, 1.72615789e+00, 2.57524730e+00, 3.84200000e+00]),
array([1.92100000e-03, 2.86593137e-03, 3.84200000e-03, 6.37885349e-03,
       9.51658319e-03, 1.41977482e-02, 2.11815574e-02, 3.16006715e-02,
       4.71449014e-02, 7.03352689e-02, 1.04932875e-01, 1.56548890e-01,
       2.33554594e-01, 3.48439062e-01, 5.19834688e-01, 7.75539062e-01,
       1.15702328e+00, 1.72615789e+00, 2.57524730e+00, 3.84200000e+00]))


The signals retrieved in the call to ``retrieve_scan_summary`` are given by the ``signals`` attribute:

.. highlight:: python

>>> summary.signals
['CUR', 'CUBS', 'CUEB', 'PFUS', 'PEBW', 'PAUX', 'QFUS', 'H98Z', 'T98Z', 'T98Y', 'WTOT', 'BNTT', 'QMIN', 'LI', 'LI3', 'EMAX', 'BLST']

There is a default set of signals that are retrieved, which are defined in the ``DEFAULT_SUMMARY_SIGNALS`` attribute
of the ``results`` module. If you want to restrict the set of signals contained in the summary, or add others
not contained in the default list, you can optionally pass a list of signals in the call to ``retrieve_scan_summary``:

.. highlight:: python

>>> import jetto_tools.results
>>> summary = jetto_tools.results.retrieve_scan_summary('/home/user/jetto/runs/my_scan', signals=['CUR'])

The above example would restrict the ``summary`` to only contain the ``'CUR'`` signal.

In general, the ``summary`` will contain the values of each signal at each point in the scan, together with a measure
of the signal's convergence. To access the values of a particular signal, use the ``signals_values`` attribute:

.. highlight:: python

>>> summary.signals_values['CUR']
masked_array(
  data=[[17184710.0, 17203120.0, 17223334.0, 17246886.0, 17275122.0,
         17311052.0, 17371462.0, 17409184.0, 17476740.0, 17553624.0,
         17635090.0, 17694346.0, 17732198.0, 17755806.0, 17775076.0,
         17792324.0, 17805968.0, --, --, --],
        [17124664.0, 17148078.0, 17174714.0, 17204722.0, 17240066.0,
         17282008.0, 17351236.0, 17392694.0, 17464510.0, 17543972.0,
         17628720.0, 17689160.0, 17728018.0, 17752464.0, 17772658.0,
         17790576.0, --, --, --, --],
        ...

For any particular signal, the returned array will have the same number of dimensions as there are in the scan. Each
element of the array corresponds to a single point in the scan. The value of an element is the *last* value in the
signal's timeseries for that particular JETTO run.

Note further that the array is a *masked* array. If an element is masked, this means that the value of that element is
invalid. Elements of the ``signals_values`` array will be masked in the following situations:

* The point directory corresponding to that element was missing from the directory tree to which ``retrieve_scan_summary``
  was applied (e.g. because the run did not complete)
* The point directory corresponding to that element contained a JETTO run which reported a run failure in its
  ``jetto.status``
* The point directory was missing an essential file (e.g. ``serialisation.json``, or ``jetto.jst``)

Note that in the case of a multi-dimensional scan, the ``signals_values`` array will also be multi-dimensional. The
ordering of the indices in this array is assigned in line with the ordering of the parameters in the ``summary.params``
list. The first parameter corresponds to the first index of the ``signals_values`` array, the second parameter to the
second index, and so forth. So for example, given the scan parameters in the example above:

.. highlight:: python

>>> summary.params
[('e_bohm_coeff', ), ('e_gbohm_coeff', )]

the ``summary.signals_values['CUR']`` array's first index corresponds to fixed values of ``'e_bohm_coeff'``, and the
second index corresponds to fixed values of ``'e_gbohm_coeff'``. In other words, the ``'CURR'`` signal values for the
point corresponding to the ``ith`` element of  ``'e_bohm_coeff'`` and the ``jth`` element of ``'e_gbohm_coeff'`` is
located at

.. highlight:: python

>>> summary.signals_values['CUR'][i, j]
17174714.0

For higher-dimensional scans, the indexing would continue in the same manner. For coupled scans, the collection of
scans in a couple constitute a *single* dimension within the ``signals_values`` array.

Finally, each signal has a *convergence* value within the ``summary`` object. The convergence of a signal is defined
as the standard deviation of the signal over the final 20% of its timeseries:

.. highlight:: python

>>> summary.signals_convergences['CUR']
masked_array(
  data=[[50.262079582831916, 236.24327366877876, 65.41588564896217,
         53.1471239113214, 69.23423058579664, 38.31365954769275,
         77.69269074379737, 49.594455106637305, 513.0089088793383,
         138.15584876780585, 61.82397659187457, 20.282807750640274,
         48.085713342576085, 238.7734341053609, 60.51494821047193,
         49.91548412622635, 44.06324047318505, --, --, --],

The ``signals_convergences`` array is sized and indexed in exactly the same manner as the ``signals_values`` array.

Labelling
=========

As an aid to cataloguing JETTO runs, the ``results`` module provides a function which can automatically generate label
files for all of the points within a scan. To do this, call the ``label_scan`` function e.g.

.. highlight:: python

>>> results.label_scan('path/to/scandir')

The first argument is the path to the scan directory i.e. the directory containing all of the scan points.
Additionally, the function accepts a catalogue ID, if applicable, and a scan label e.g.

.. highlight:: python

>>> results.label_scan('path/to/scandir', template='user/jetto/machine/12345/jan0101/seq-1', scan_label='myscan')

The template should be the catalogue ID of the *template* used to generate the scan. The scan label is arbitrary, but should
meaningfully describe the scan in some way. Normally, it is the relative path to the scan directory from the user's JETTO
runs directory.

Note that the ``label_scan`` function duplicates the effect of ``config`` module's
:ref:`labelling of scan points <configlabelling-label>`, with the following differences:

* ``label_scan`` does not create a top-level label file in the root scan directory, only in point directories.
* ``label_scan`` adds an additional label to each label file, namely, ``run-status``. This label specifies whether the run succeeded or failed.
