.. _config-label:

=============
Config module
=============

Introduction
============

The ``config`` module provides a means of configuring a JETTO run from a Python client application. This provides an
alternative to using the JAMS application, which only has a graphical interface.

This module does not support creation of a JETTO configuration *ab initio*: a template run must be provided (either
from an existing run directory or from a catalogued case). The template run must already contain all of the settings
that the user wishes to modify. A ``RunConfig`` object can be created from the template, and the user can modify the
configuration using the interface provided by the ``RunConfig`` class.

The ``RunConfig`` class supports viewing and setting of scalar and vector parameter values, extra namelist arrays, and
also supports performing scans over selected parameters. In addition, a variety of other specific operations can be
performed, including selection of the JETTO binary to use, setting of time ranges, number of processors, swapping of
exfiles etc.

Creating a template
===================

To configure JETTO, you start by creating a template. The :ref:`template <template-label>` module documentation
describes what templates are and how they are created. A simple example of creating a template from the files of an
existing JETTO run directory (at example path ``~/jetto/runs/myrun``) is as follows:

.. highlight:: python

>>> import jetto_tools.template
>>> template = jetto_tools.template.from_directory('~/jetto/runs/myrun')

The :ref:`template <template-label>` module supports a variety of methods for creating a template from existing JETTO
files. See the module's documentation for more information.

Changing the configuration
==========================

Once you have a template, you can then create a ``RunConfig`` object:

.. highlight:: python

>>> import jetto_tools.config
>>> config = jetto_tools.config.RunConfig(template)

The ``RunConfig`` class is the primary means of configuring a JETTO run.

Setting parameter values
------------------------

Parameter values can be set via the parameter IDs which are provided in the template lookup file. See the
:ref:`lookup <lookup-label>` module documentation for more details on the contents of lookup files. For example, given
the following parameters in the template lookup file:

::

    'bound_ellip': {
        'jset_id': 'EquilEscoRef.dshEllipticity',
        'nml_id': {
            'namelist': 'NLIST1',
            'field': 'ELONG'
        },
        'type': 'real',
        'dimension': 'scalar'
    },
    'bcintrhon': {
        'jset_id': null,
        'nml_id': {
            'namelist': 'NLIST1',
            'field': 'BCINTRHON'
        },
        'type': 'real',
        'dimension': 'scalar'
    },
    'ipraux': {
        'jset_id': null,
        'nml_id': {
            'namelist': 'INESCO',
            'field': 'IPRAUX'
        },
        'type': 'real',
        'dimension': 'scalar'
    },
    'rcntren': {
        'jset_id': null,
        'nml_id': {
            'namelist': 'INNBI',
            'field': 'RCNTREN'
        },
        'type': 'real',
        'dimension': 'vector'
    }

We can then view or set the value of the parameter in the run configuration using standard dictionary syntax:

.. highlight:: python

>>> config['bound_ellip']
1
>>> config['bound_ellip'] = 2
>>> config['bound_ellip']
2
>>> config['rcntren']
[10.1, 10.2]
>>> config['rcntren'] = [10.3, 10.4]

In general, parameters can be set to integers, reals, or (for extra namelist arrays) lists, but the value provided must
be compatible with the ``type`` and ``dimension`` values specified in the lookup dictionary. For example, given a
parameter with type ``"int"``, its value can be set to ``1`` or ``1.0``, since the latter is trivially convertible to
an integer. However, it cannot be set to the value ``1.5``, and attempting to do so will raise a ``RunConfigError``
exception e.g.

.. highlight:: python

>>> config['bound_ellip'] = 1.5
Traceback (most recent call last):
...
jetto_tools.config.RunConfigError: Unable to convert value 1.5 to integer

At the present, only setting of scalar values (ints and reals), and extra namelists array values are supported by the
``RunConfig`` class. Setting of general JSET array parameters and more complicated types (e.g. time polygons) is not
yet supported.

Note that although JSET fields are allowed to have empty values (represented by value ``None`` in Python), all parameters
listed in the lookup file must have valid values in the template: they cannot be empty, as this would introduce
ambiguity when updating the namelist file at configuration export.


Setting GRAY parameter values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When used, the GRAY ECRH module is configured by a pair of
configuration files ``gray.data`` and ``graybeam.data``. With the
latter of these containing values that can be scanned over
meaningfully. These are prefixed by ``GRAY:`` and are preconfigured
within the tool so do not need to be defined in the lookup file. This
is in contrast to JETTO parameters were all parameters need entries in
the lookup, see :ref:`lookup <lookup-label>` module for more info.

Scanning over beam frequency is supported via:

.. highlight:: python

>>> config['GRAY:B1.fghz'] = [180.0 200.0]

Note that beam ``B1`` must already exist in the file, and the
attribute name ``fghz`` comes from the GRAY source code along with
other attribute names (e.g. ``alphast``) below.

Scanning over the launch mode is specified via:

.. highlight:: python

>>> config['GRAY:B1.iox'] = 1

Scanning over beam grid parmaters is specified as:

.. highlight:: python

>>> config['GRAY:B1[1].alphast'] = -40.0
>>> config['GRAY:B1[1].betast'] = 30.0

for specifying Z coordinates;

.. highlight:: python

>>> config['GRAY:B1[1].x00'] = 2500.0
>>> config['GRAY:B1[1].y00'] = 0.0
>>> config['GRAY:B1[1].z00'] = 0.0

for the launching positions;

.. highlight:: python

>>> config['GRAY:B1[1].waist1'] = 100.0
>>> config['GRAY:B1[1].waist2'] = 100.0

for the minimium beam cross section along the x- and y-axis
respectively;

.. highlight:: python

>>> config['GRAY:B1[1].rci1'] = 1e-6
>>> config['GRAY:B1[1].rci2'] = 1e-6

for the radius of the wavefront, note that this approaches planar as
this approaches zero;

.. highlight:: python

>>> config['GRAY:B1[1].phi1'] = 0.0
>>> config['GRAY:B1[1].phi2'] = 0.0

for setting Phi.

It is not currently possible to change the number of beams nor grid
points within a beam from the scan API, please edit the
``graybeam.data`` file manually in this case.


Scanning over parameters
------------------------

Instead of setting the value of a parameter, it is also possible to perform scans over parameters. This is done by setting
the value of a parameter to be a ``jetto_tools.config.Scan`` object. Scans can be created based on any simple iterable of
numeric values (such as a list) e.g.

.. highlight:: python

>>> scan = jetto_tools.config.Scan([0, 1, 2, 3, 4])

We can then scan over parameter ``bound_ellip`` using the same dictionary interface that we use to set its value:

.. highlight:: python

>>> config['bound_ellip'] = scan

The points within a scan are subject to the same rules that apply when setting parameters to have single values. Each
point in the scan must be of the type specified in the lookup file (or must be trivially convertible to that type).

A ``Scan`` object can be initialised from any iterable in Python, which makes it easy to generate scans based on
arithmetic progressions. For example, if we want to scan over each integer from 1 to 1000, we can do it using Python's
``range`` built-in function:

.. highlight:: python

>>> config['bound_ellip'] = jetto_tools.config.Scan(range(1000))

The ``RunConfig`` class also supports multi-dimensional scans, where scans are performed over multiple parameters.

.. highlight:: python

>>> config['bound_ellip'] = jetto_tools.config.Scan([1, 2, 3])
>>> config['ipraux'] = jetto_tools.config.Scan([4, 5, 6])

The points in the scan will then be the cartesian product of the arrays comprising the individual scans e.g. the above
configuration will scan over the points `(1, 4), (1, 5), (1, 6), (2, 4), (2, 5), ...`

In order to limit the total number of points in a JETTO scan, a number of safety limits are enforced when configuring scans.
These are:

- The scan configuration can be at most **3-dimensional** i.e. only three distinct parameters can be scanned over in a
  single run configuration
- A single scan dimension can be at most **100** points in length
- The total number of points in a multi-dimensional scan configuration can be at most **500**

A ``RunConfigError`` will be raised if the user attempts an operation which breaches the above limits e.g.

.. highlight:: python

>>> config = jetto_tools.config.RunConfig(template)
>>> config['ipraux'] = jetto_tools.config.Scan(range(5))
>>> config['bcintrhon'] = jetto_tools.config.Scan(range(100))
>>> config['bound_ellip'] = jetto_tools.config.Scan(range(2))
Traceback (most recent call last):
...
jetto_tools.config.RunConfigError: Total number of scan points cannot exceed 500

Coupled Scans
-------------

In addition to creation a scan over a single parameter, it is possible to couple together scans over two or more parameters.
Coupled scans can be created by passing a dictionary mapping each parameter to a scan object, to the
``create_coupled_scan`` function e.g.

.. highlight:: python

>>> config.create_coupled_scan({'bound_ellip': Scan([0.0, 1.1, 2.2]), 'bcintrhon': Scan([0.7, 0.75, 0.8])})

This would couple together the scans over ``bound_ellip`` and ``bcintrhon``. This effectively produces a one-dimensional
scan wherein the parameters successively take on the pairs of values ``(0.0, 0.7)``, ``(1.1, 0.75)``, and ``(2.2, 0.8)``.

Each scan in the coupling is subject to the normal rules that apply when creating regular scans. In addition,
the following rules apply:

- Each scan being coupled together must be of the same length
- A coupled scan must contain at least two parameters
- You cannot couple a parameter that is already a member of another coupled scan
- You cannot set the value of a parameter that is already a member of a coupled scan

From the point of view of counting the number of scan dimensions in a configuration, a coupled scan counts as a single
dimension. Therefore, you could couple three parameters together in a single coupled scan and also have two regular scans over single
parameters, resulting in a three-dimensional scan. Coupled scans also support vector values, provided that the relevant
parameter is of ``vector`` type.

The below example illustrates a possible configuration involving the above:

.. highlight:: python

>>> config.create_coupled_scan({'curti': Scan([1.9, 2.8]), 'rcntren': Scan([[2.5, 3.0], [2.6, 3.1]]), 'ipraux': Scan([0.3, 0.4])})
>>> config['bound_ellip'] = Scan([0.0, 1.1, 2.2])
>>> config['bcintrhon'] = Scan([0.7, 0.75, 0.8])

The above configuration would be a three-dimensional scan: one dimension for the coupled scan, and one dimension each for
the ``bound_ellip`` and ``bcintrhon`` parameters.

Iterating over parameters
-------------------------

The ``RunConfig`` class supports iteration over all of its parameters e.g.

.. highlight:: python

>>> for p in config:
...   print(p, config[p])
...
bound_ellip 1.5
bcintrhon 0.7
ipraux 2

It also supports chcking if a parameter exists:

.. highlight:: python

>>> 'bound_ellip' in config
True
>>> 'foo' in config
False

Setting the exfile
------------------

The ``RunConfig`` class provides an attribute for modifying the JETTO exfile:

.. highlight:: python

>>> config.exfile = '/path/to/jetto.ex'

If the ex-file is not specified by the user, it will remain at whatever value is specified in the original template
JSET. If the template contains the ex-file as one of its extra files, it will be assumed by the ``RunConfig`` class that
this file is equivalent to the one specified in the template JSET.

Note that it is not possible to updated the location of a *cataloged* ex-file; only a private one. Any update of the
ex-file will switch the ex-file source in the exported JSET from ``'Cataloged'`` to ``'Private'``.

Setting the JETTO load module
-----------------------------

The JETTO load module is specified by a combination of the user and the binary version number. There are attributes
provided by the ``RunConfig`` class for both of these:

.. highlight:: python

>>> config.binary = 'v060619'
>>> config.userid = 'sim'

These attributes are used to populate the JSET and batchfile when the configuration is exported. If they are not set by
the user, they retain whatever values are specified in the original template JSET.

Setting the number of processors
--------------------------------

The number of processors to be used when running the configuration can be specified. There is an attribute provided by
the ``RunConfig`` class for this:

.. highlight:: python

>>> config.processors = 4

This attribute is used to populate the JSET and batchfile when the configuration is exported. If it is not set by the
user, it retains whatever value was specified in the original template JSET.

Setting the walltime
--------------------

The walltime controlling how long the JETTO run should last can be specified. There is an attribute provided by the
``RunConfig`` class for this, which specifies the walltime in hours:

.. highlight:: python

>>> config.walltime = 4

This attribute is used to populate the JSET when the configuration is exported. If it is not set by the user, it
retains whatever value was specified in the original template JSET.

Setting time ranges and intervals
---------------------------------

The start and end times for the JETTO run can be set via the ``start_time`` and ``end_time`` attributes provided by the
``RunConfig`` class e.g.

.. highlight:: python

>>> config.start_time = 100.0
>>> config.end_time = 101.0

The initial values of these attributes are taken from the ``SetUpPanel.startTime`` and ``SetUpPanel.endTime`` fields in
the template JSET.

The number of ESCO time steps can be set via the ``esco_timesteps`` attribute; and the number of output profile timesteps
can be set via the ``profile_timesteps`` attribute:

.. highlight:: python

>>> config.esco_timesteps = 10
>>> config.profile_timesteps = 10

On export of the configuration, the start time, end time, and number of ESCO and profile timesteps will be used to
consistently update multiple parameters in the exported JSET and namelist files (see below).

Setting the IMAS configuration
------------------------------

Assuming that your template was an IMAS case, the ``RunConfig`` class allows access to and modification of a number of
IMAS settings. To the extent possible, these settings mimic the corresponding settings in the JAMS ``Setup`` and
``Job process`` panels.

Firstly, to see if you case **is** an IMAS configuration, use the ``driver`` property:

.. highlight ::

>>> config.driver
<Driver.IMAS: 'IMAS(Python), native + IDS I/O'>

**Note that it is not possible to switch a case from using the standard driver to the IMAS driver, or vice-versa.**

To view or set if the configuration reads from input IDS files, use the ``read_from_ids`` property:

.. highlight:: python

>>> config.read_from_ids
True
>>> config.read_from_ids = False

To view or set if the configuration writes to output IDS files, use the ``create_output_ids`` property:

.. highlight:: python

>>> config.create_output_ids
False
>>> config.create_output_ids = True

Assuming that the configuration reads from input IDS files, you can modify the source of the input IDS files by using
the ``input_ids_source`` property:

.. highlight:: python

>>> config.input_ids_source
CatalogueId(owner='jdoe', code='jetto', machine='iter', shot=12345, date='feb0120', seq=1)

Note that the ``input_ids_source`` returns an instance of ``CatalogueId`` if the input IDS files are taken from a
catalogued case (this will always be true if the template was retrieved from the catalogue). If the input IDS files
come from a private case on the local file system, it will instead return an instance of ``IMASDB``:

>>> config.input_ids_source
IMASDB('user', 'mast', 98765, 1)

You can use the ``input_ids_source`` property to set a different source for input IDS files:

>>> config.input_ids_source = IMASDB(user='jdoe', machine='tcv', shot=22222, run=2)

Note that only setting the input IDS files from a *private* case is supported: setting the input IDS files from a
*catalogued* case is not:

.. highlight :: python

>>> c.input_ids_source = CatalogueId(owner='jdoe', code='jetto', machine='iter', shot=12345, date='feb0120', seq=1)
...
jetto_tools.config.RunConfigError: Cannot set input IDS source from catalogued case

Exporting a configuration
=========================

Once the desired settings have been applied to the configuration, it can be exported. Exporting the configuration
generates the set of files on disk which JETTO will use at run-time, and which can also subsequently be imported into JAMS.

To export the configuration, call the ``export`` method of the ``RunConfig`` class, providing the path to the export
directory:

.. highlight:: python

>>> config.export('~/jetto/runs/my_new_run')

This will generate the following set of files in the ``export`` directory. This example assumes that there is only a
single point in the configuration, and therefore there is only a single set of JETTO configuration files. For clarity,
only a minimal set of JETTO files is shown, but the export will include all files specified in the original template:

::

    my_new_run
    ├── jetto.ex
    ├── jetto.in
    ├── jetto.jset
    ├── serialisation.json
    ├── ...
    └── _template
         ├── jetto.in
         ├── jetto.jset
         ├── lookup.json
         └── ...

If on the other hand there are scans in the configuration, it will contain multiple points. In that case, the export
will consist of a set of directories, one per scan point, each of which contains the same collection of files as the
single-point case above. So, for example, if we have a scan with three points:

.. highlight:: python

>>> config['bcintrhon'] = jetto_tools.config.Scan([1.1, 2.2, 3.3])

then the file/directory layout in the export directory would be:

::

    my_new_run
    ├── point_000
    │   ├── jetto.ex
    │   ├── jetto.in
    │   ├── jetto.jset
    │   ├── serialisation.json
    │   ├── _template
    │   └── ...
    ├── point_001
    │   ├── jetto.ex
    │   ├── jetto.in
    │   ├── jetto.jset
    │   ├── serialisation.json
    │   ├── _template
    │   └── ...
    ├── point_002
    │   ├── jetto.ex
    │   ├── jetto.in
    │   ├── jetto.jset
    │   ├── serialisation.json
    │   ├── _template
    │   └── ...
    ├── serialisation.json
    └── _template
        ├── jetto.in
        ├── jetto.jset
        ├── lookup.json
        └── ...

Note that in addition to the ``serialisation.json`` file for each point in the scan, there is also a top-level
``serialisation.json`` file which represents the serialisation of the entire scan.

Note further that each point directory also contains a ``_template`` directory. For points, this directory is simply a
symbolic link to the top-level ``_template`` directory in the export directory.

The ``export`` method has an optional argument, ``rundir``, which can be used to provide the run directory name i.e.
the relative path to the run directory from the JETTO run root. This is used to populate the
``JobProcessingPanel.runDirName`` field in the exported JSET.

Template files
--------------

The exported template files, found in the top-level ``_template`` directory, are essentially copies of the original
template files supplied to the run configuration. At a minimum, the ``_template`` directory will include the original
JSET, namelist and lookup files. If the template included any other files (e.g. SANCO namelists, ex-file etc.) copies of
these will also be included in the ``_template`` directory.

JSET
----

The exported JSETs have the following edits to the ``File Details`` section applied to them, with respect to the template:

- The ``Creation Name`` is set to the path to the exported file
- The ``Creation Date`` and ``Creation Time`` are set to the date and time at export
- The ``Version`` is set to the version number provided by the ``jetto_tools.version`` module

The exported JSETs has the following edits to the ``Settings`` section applied to it, with respect to the template:

- For each parameter in the lookup, the configured value of the parameter is applied to the corresponding field within
  the JSET
- The same applies to extra namelist items in the JSET (note however that extra namelist items are not guaranteed to be
  exported in the same order in which they appeared in the original template JSET)
- For any JSET parameter which is not in the lookup, it will simply be written in the exported file identically to its
  value in the original template JSET
- If the location of the ex-file has been set by the user, the ``SetUpPanel.exFileName``, ``SetUpPanel.exFilePrvDir``,
  and the ``SetUpPanel.exFileSource`` fields will be updated accordingly.
- If the JETTO binary has been set by the user, the fields ``JobProcessingPanel.name`` and ``JobProcessingPanel.userid``
  will be updated accordingly.

For the start and end times and time intervals, the following changes are applied to the exported JSET:

- The ``SetUpPanel.startTime``, ``EquilEscoRefPanel.tvalue.tinterval.startRange``, and ``OutputStdPanel.profileRangeStart``
  parameters are updated with the value of ``start_time``.
- The ``SetUpPanel.endTime``, ``EquilEscoRefPanel.tvalue.tinterval.endRange``, and ``OutputStdPanel.profileRangeEnd``
  parameters are updated with the value of ``end_time``.
- The ``EquilEscoRefPanel.tvalue.tinterval.numRange`` parameter is updated with the value of ``esco_timesteps``.
- The ``OutputStdPanel.numOfProfileRangeTimes`` parameter is updated the value of ``profile_timesteps``.
- If ``start_time`` and/or ``end_time`` differ from the corresponding values in the template JSET, the
  ``OutputStdPanel.profileFixedTimes`` array is cleared (this differs from JAMS, where the fixed times are supported in
  *addition* to the range times).

In any case, if none of the ``start_time``, ``end_time``, ``esco_timesteps`` or ``profile_timesteps`` are changed in
the configuration, no alteration si made to any of the time fields in the JSET, and the values present in the template
are retained.

JETTO Namelist
--------------

The exported JETTO namelist files (``jetto.in``) have the following edits to the file header, with respect to the
original template:

- The ``JAMS Version`` field is set to the version number provided by the ``jetto_tools`` package
- ``Date`` and ``Time`` fields are set to the date and time at export
- The fields underneath ``JAMS GIT information`` (e.g. ``Current GIT repository``) are all set to ``n/a``, as they are
  less applicable when the namelist file has been generated from a Python client application

The exported namelist files have the following edits to the individual namelists applied, with respect to the template:

- For each parameter in the lookup, the configured value of the parameter is applied to the corresponding namelist field
  within the namelists file
- The same applies to extra namelist items in the JSET
- For cases (e.g. ``CURTI`` and ``BTIN``) where scalar JSET parameters are mapped to namelist arrays, each element of
  the namelists array is updated identically with the new parameter value.
- For any namelist parameter which is not in the lookup, it will simply be written in the exported file identically to its
  value in the original template namelists file
- If the template JSET is configured for restart, the ``IRESTR`` field is set to 1; otherwise it is set to 0.

Additionally, for the start and end times and time intervals, the following changes are applied to the exported namelist:

- The ``TBEG`` and ``TIMEQU(1)`` parameters parameters are updated with the value of ``start_time``.
- The ``TMAX`` and ``TIMEQU(2)`` parameters are updated with the value of ``end_time``.
- The ``TIMEQU(3)`` parameter is updated with the ESCO interval, given by ``(end_time - start_time) /  (esco_timesteps - 1)``.
  Note that this is only done if the ESCO time values are set to ``Interval`` in the template JSET. If they are set to
  ``'Discrete'``, an exception is raised, as this option is not supported. Note further that if ``esco_timesteps`` has the
  value ``1``, then the ``TIMEQU(3)`` parameter is set to the value ``1.0e30`` (reproducing JAMS behaviour).

The following changes to the exported namelist are applied *only if* (a) either the ``start_time`` or ``end_time`` were
altered in the configuration and (b) output profiles are selected in the template JSET. If this is not the case, the
values of ``TPRINT`` and ``NTPR`` in the template namelist are retained.

- The ``TPRINT`` array is updated with the time series of output profile time points i.e. an array starting at ``start_time``,
  ending at ``end_time``, and containing ``profile_timesteps - 2`` points (since JETTO will include the start and end
  times in the output points regardless. This is only done if Profiles were selected in the template JSET.
- The ``NTPR`` parameter is updated to the value of ``profile_timesteps - 2``, or ``0`` if Profiles were not selected in
  the template JSET.

Note that, unlike JAMS, the ``TPRINT`` parameter in the exported namelist will not incorporate the *fixed* profile times
from the JSET (excepting the case where the original value of ``TPRINT`` is retained).

SANCO namelist
--------------

If a SANCO namelist was provided in the template *and* SANCO is enabled in the template JSET (see the
:ref:`template <template-label>` module and :ref:`jset <jset-label>` module for more information), then a SANCO namelist
file will be included in the export.

The SANCO namelist file is called ``jetto.sin``. It has the same updates applied to it at export that are described in
respect of the main namelist file above.

Ex-file
-------

The exported ex-file is simply copied into the export point directory from whatever location has been configured by the
user (or from the location listed in the template JSET if no update has been performed). If no file can be found at the
configured ex-file path, then the export will terminate with an exception:

.. highlight:: python

>>> config.exfile = 'blah'
>>> config.export('./export')
Traceback (most recent call last):
...
jetto_tools.config.RunConfigError: Cannot find exfile at 'blah'

Serialisation
-------------

On export, a *serialisation* will be generated for the configuration, and also for each individual point in the
configuration. The exported file is called ``serialisation.json``. It has the following format:

::

    {
        "loadmodule": {
            "binary": "v060619",
            "userid": "sim"
        },
        "parameters": {
            "bound_ellip": 1.5,
            "bcintrhon": 0.7,
            "ipraux": 2,
            "rcntren": [10.1, 10.2]
        },
        "files": {
            "jetto.ex": "/path/to.jetto.ex",
            ...
        },
        "processors": 2,
        "start_time": 10.0,
        "end_time": 20.0,
        "esco_timesteps": 100,
        "profile_timesteps": 100
    }

The serialisation is a JSON string containing a dictionary. The items in the dictionary are:

- ``files``: The paths to each of the extra files. Since the ``jetto.ex`` file is required for each JETTO run, the
  ``files`` will always contain ``jetto.ex``; other files will appear if they were specified in the original template
- ``loadmodule``: The configured JETTO binary version number and user ID
- ``parameters``: The configured value of each parameter in the template lookup
- ``processors``: The configured number of processors to use for the JETTO run
- ``start_time``: The configured start time for the JETTO run
- ``end_time``: The configured end time for the JETTO run
- ``esco_timesteps``: The number of ESCO time values
- ``profile_timesteps``: The number of output profile time intervals

Note that the serialisation for the current configuration can be generated at any time by calling the ``serialise()``
method of the ``RunConfig`` class.

If the configuration contains a scan e.g.

.. highlight:: python

>>> config['bcintrhon'] = jetto_tools.config.Scan([0.0, 1.0, 2.0])

then the top-level serialisation will store the scan values using a custom JSON serialisation:

::

    $ cat export/serialisation.json
    {
        ...
        "parameters": {
            "bound_ellip": 1.5,
            "bcintrhon": {
                "__class__": "Scan",
                "__value__": [
                    0.0,
                    1.0,
                    2.0
                ]
            },
            "ipraux": 2,
            "rcntren": [10.1, 10.2]
        },
        ...
    }

However, the serialisation for each individual point will just contain the value of the parameter *for that point* e.g.:

::

    $ cat export/point_001/serialisation.json
    {
        ...
        "parameters": {
            "bound_ellip": 1.5,
            "bcintrhon": 1.0,
            "ipraux": 2,
            "rcntren": [10.1, 10.2]
        },
        ...

    }

If the configuration contains a *coupled scan* e.g.

.. highlight:: python

>>> config.create_coupled_scan({'bound_ellip': Scan([0.0, 1.1, 2.2]), 'bcintrhon': Scan([0.7, 0.75, 0.8])})

then the serialisation will look as follows:

::

    $ cat export/serialisation.json
    {
        ...
        "parameters": {
            "bound_ellip": {
                '__class__': '_CoupledScan',
                '__value__': [0.0, 1.1, 2.2],
                '__coupled_with__': ['bcintrhon']
            },
            "bcintrhon": {
                '__class__': '_CoupledScan',
                '__value__': [0.7, 0.75, 0.8],
                '__coupled_with__': ['bound_ellip']
            },
            ...
        },
        ...
    }

The serialisation now lists not only the values that the parameter takes within the scan, but also the parameter(s)
to which it is coupled.

Extra files
-----------

For all extra files defined in the original template, they are copied unmodified to the export directory.

.. _configlabelling-label:

Labels
------

On export, a *label* file will be generated for the configuration, and also for each individual point in the
configuration. The exported file is called ``labels.yaml``. It has the following format:

::

    scan-label: <Label>
    template: <Template catalogue ID>
    point-index: <Index>
    scan-param-<Param>: <Value>

The YAML file is a simple (flat) dictionary. The items in the dictionary are:

- ``scan-label``: A label describing the scan. This is taken from the name of the run directory for the scan.
- ``template``: The identifier of the catalogue entry from which the template was taken (if applicable)
- ``point-index``: The index of the point in the scan
- ``scan-param-<Param>``: The value of each scanned parameter (named <Param>)

The top-level ``labels.yaml`` omits the ``point-index`` and ``scan-param-<Param>`` fields.

Example configurations
======================

This section lists a few complete programs, demonstrating the use of the ``config`` API for a couple of different
use cases.

Each example assumes that the current working directory of the script contains template ``jetto.jset``, ``jetto.in``,
and ``lookup.json`` files. The JSET and namelist files are assumed to have been produced from a JAMS run and are
consistent with each other.

Modifying a JETTO parameter
---------------------------

**Goal:** We want to modify the Boundary Ellipticity (found in the Plasma Geometry->Equilibrium tab in JAMS). We want
to change it from its template value of 1.5, to 1.6. We want to export the resulting configuration to directory
``export``, with respect to the current working directory.

Firstly, the ``lookup.json`` file must contain a specification for the parameter we want to modify. If it doesn't
already exist, the following will do:

::

    {
        "bound_ellip": {
            "jset_id": "EquilEscoRef.dshEllipticity",
            "nml_id": {
                "namelist": "NLIST1",
                "field": "ELONG"
            },
            "type": "real",
            "dimension": "scalar"
        },
        ...
    }

In this parameter specification, ``bound_ellip`` is an arbitrary short name that we use to make manipulating the
parameter via the ``config`` API more straightforward.

Once we've modified the lookup file to include the specification of the parameter we want to modify, the following
Python program will make and export the configuration files that we require:

.. code-block:: python

    import jetto_tools.config
    import jetto_tools.template
    template = jetto_tools.template.from_directory('.')
    config = jetto_tools.config.RunConfig(template)
    config['bound_ellip'] = 1.6
    config.export('./export')

Modifying a JETTO extra namelist scalar parameter
-------------------------------------------------

**Goal:** We want to modify the NLIST1/BCINTRHON parameter (found in the Go->Extra namelist output tab in JAMS). We want
to change it from its template value of 0.7, to 0.8. As before, we want to export the resulting configuration to
directory ``export``, with respect to the current working directory.

As before, the the ``lookup.json`` file must contain a specification for the parameter we want to modify. If it doesn't
already exist, the following will do:

::

    {
        "bcintrhon": {
            "jset_id": null,
            "nml_id": {
                "namelist": "NLIST1",
                "field": "BCINTRHON"
            },
            "type": "real",
            "dimension": "scalar"
        },
        ...
    }

Since extra namelist parameters don't have distinct names in the JSET file, the ``jset_id`` field is set to ``null``
(note that ``null`` is the JSON representation corresponding to the Python ``None`` value). Otherwise, this parameter
specification is similar to what we've seen before.

Once we've modified the lookup file to include the specification of the parameter we want to modify, the Python program
we need is practically identical to the last example, since the lookup file allows the ``config`` API to treat JETTO
parameters in a unified way:

.. code-block:: python

    import jetto_tools.config
    import jetto_tools.template
    template = jetto_tools.template.from_directory('.')
    config = jetto_tools.config.RunConfig(template)
    config['bcintrhon'] = 0.8
    config.export('./export')

Modifying a JETTO extra namelist array parameter
------------------------------------------------

**Goal:** We want to modify the INNBI/RCNTREN parameter (found in the Go->Extra namelist output tab in JAMS). We want
to change it from its template value of [10.1, 10.2], to [10.3, 10.4]. As before, we want to export the resulting
configuration to directory ``export``, with respect to the current working directory.

As before, the the ``lookup.json`` file must contain a specification for the parameter we want to modify. If it doesn't
already exist, the following will do:

::

    {
        'rcntren': {
            'jset_id': null,
            'nml_id': {
                'namelist': 'INNBI',
                'field': 'RCNTREN'
            },
            'type': 'real',
            'dimension': 'vector'
        }
        ...
    }

Since extra namelist parameters don't have distinct names in the JSET file, the ``jset_id`` field is set to ``null``
(note that ``null`` is the JSON representation corresponding to the Python ``None`` value). Otherwise, this parameter
specification is similar to what we've seen before.

Once we've modified the lookup file to include the specification of the parameter we want to modify, the Python program
we need is practically identical to the last example, since the lookup file allows the ``config`` API to treat JETTO
parameters in a unified way:

.. code-block:: python

    import jetto_tools.config
    import jetto_tools.template
    template = jetto_tools.template.from_directory('.')
    config = jetto_tools.config.RunConfig(template)
    config['rcntren'] = [10.3, 10.4]
    config.export('./export')

Replace the JETTO ex-file
-------------------------

**Goal:** We want to replace the ex-file specified in the template JSET with one at path ``/home/user/jetto.ex``.

This requires a straightforward use of the ``exfile`` property provided by the ``RunConfig`` class:

.. code-block:: python

    import jetto_tools.config
    import jetto_tools.template
    template = jetto_tools.template.from_directory('.')
    config = jetto_tools.config.RunConfig(template)
    config.exfile = '/home/user/jetto.ex'
    config.export('./export')

Swap the JETTO load module
--------------------------

**Goal:** We want to replace the JETTO load module specified in the template JSET with version 'v010120' compiled by
user 'sim'.

This requires use of the ``binary`` and ``userid`` properties provided by the ``RunConfig`` class:

.. code-block:: python

    import jetto_tools.config
    import jetto_tools.template
    template = jetto_tools.template.from_directory('.')
    config = jetto_tools.config.RunConfig(template)
    config.binary = 'v010120'
    config.userid = 'sim'
    config.export('./export')

Scan over a JETTO parameter
---------------------------

**Goal:** We want to scan  over the Boundary Ellipticity parameter, with values  [1.0, 1.2, 1.4, 1.6, 1.8, 2.0].

As before, the ``lookup.json`` file must contain a specification for the parameter we want to modify.

The following Python program will generate the configuration we require and export it:

.. code-block:: python

    import jetto_tools.config
    import jetto_tools.template
    template = jetto_tools.template.from_directory('.')
    config = jetto_tools.config.RunConfig(template)
    config['bound_ellip'] = jetto_tools.config.Scan([1.0, 1.2, 1.4, 1.6, 1.8, 2.0])
    config.export('./export')

Modifying a SANCO parameter
---------------------------

**Goal:** We want to modify the SANCO temperature decay length parameter. We want to change it from its template value
2.0 cm to 3.0 cm.

As before, the ``lookup.json`` file must contain a specification for the parameter we want to modify e.g.:

::

    {
        'tlam':  {
            'jset_id': 'SancoSOLPanel.TemperatureDecayLength',
            'nml_id': {
                'namelist': 'PHYSIC',
                'field': 'TLAM'
            },
            'type': 'real',
            'dimension': 'scalar'
        },
        ...
    }

We assume that in addition to the standard template files, the current working directory also contains a template
SANCO namelist file ``jetto.sin``, and further that SANCO is enabled as the impurities source in the template JSET file.

The following Python program will generate the configuration we require and export it:

.. code-block:: python

    import jetto_tools.config
    import jetto_tools.template
    template = jetto_tools.template.from_directory('.')
    config = jetto_tools.config.RunConfig(template)
    config.['tlam'] = 3.0
    config.export('./export')

Modification of SANCO extra namelist parameters works in the same manner as for JETTO extra namelist parameters (see
above).

API Reference
=============

.. automodule:: jetto_tools.config

.. autoclass:: jetto_tools.config.RunConfig
    :members: __init__, exfile, binary, userid, serialise, processors, export, __getitem__, __setitem__, walltime, start_time, end_time, esco_timesteps, profile_timesteps, ids_in, ids_out, driver, read_from_ids, create_output_ids, input_id_source
.. autoexception:: jetto_tools.config.RunConfigError

.. autoclass:: jetto_tools.config.Scan
    :members: __init__, __len__, __iter__, __getitem__, __setitem__, __repr__, __eq__, __ne__, to_json
.. autoclass:: jetto_tools.config.ScanError

