.. _lookup-label:

=============
Lookup module
=============

Introduction
============

Lookup files are used to relate JAMS JSET files to the namelist files used by JETTO. Normally, JAMS configures a namelist
file based on its internal data model, which can be edited by the user via the JAMS GUI panels. Since JAMS also produces
a corresponding JSET file, the JSET file and namelist file(s) are consistent with each other.

In order to use the scan API to manipulate JSET and namelist files, it is necessary to have a *lookup* file which relates
the contents of the JSET file to the contents of the namelist file(s). The lookup file allows the scan API to modify the
JSET and namelist files in a way which retains consistency between all of them. It also facilitates easy modification
of the JETTO configuration by the user.

Note: Only **parameters which are intended to be modified** via the
scan API are required to appear in the lookup file: all other
parameters can be omitted. Additionally, GRAY parameters don't use
JSET or namelist files and therefore do not need to be listed in the
lookup file.

This module is primarily intended to be used by other library code in the ``jetto-pythontools`` package for configuring
JETTO runs and scans. However, with care, it can be used by any client application to perform low-level manipulation of
JETTO lookup files.

Lookup files and terminology
============================

A lookup file is written in JSON format. The file is divided into *parameters*: each parameter's description has an identical
format, called a *schema*. An example of the description of a parameter is:

::

    "param" : {
        "jset_id" : "PanelName.ParameterName",
        "nml_id" : {
            "namelist" : "NLIST1",
            "field" : "FIELD1"
        },
        "type" : "int",
        "dimension" : "scalar"
    }

The field ``param`` is the *short name* of the parameter: it is the identifier which the client will use when configuring
a parameter for a JETTO run (e.g. setting the parameter's value, or scanning over a range of values).

Each parameter must contain a fixed set of individual items. These are:

* ``jset_id``: The identifier of the parameter within a JSET file. Typically a name of the form ``PanelName.ParameterName``.
  Must be a string, unless it is ``null`` (see below).
* ``nml_id``: The identifier of the parameter within one of the namelist files (JETTO or SANCO). In this case, the
  identifier is made of two parts: the *namelist name* and the *field name*.
* ``type``: Can be ``int`` or ``real``. This field controls the format with which updated values are written to the JSET
  and namelist files, and also places restrictions on what values the user can set for the parameter.
* ``dimension``: Can be ``scalar`` or ``vector``. Note that parameters of dimension ``vector`` are only supported by the
  scan API if they appear in the JSET file's extra namelists (JETTO or SANCO). Vectors in other parts of the JSET file
  are not supported for modification.

Each of the fields above is required to be present by the schema. With the exception of the ``jset_id``, which is allowed
to have the value ``null``, all fields must have string values and be non-empty.

A value of ``null`` for the ``jset_id`` indicates that it is an *extra namelists* item. These are fields set from the
Extra Namelist panels in JAMS (either the JETTO extra namelists panel at ``Go->Extra namelist output``, or the SANCO
extra namelists panel at ``Impurities->Options->Settings->Extra Namelist Output``). The extra namelist parameters are
optional fields that the user can add to the namelist. They are stored in the JSET file by index, rather than by name,
so they do not have a ``jset_id``. Note that ``null`` is the JSON representation of the Python ``None`` value. When a
lookup file with a parameter having a ``jset_id`` with value ``null`` is loaded into Python, the ``jset_id`` will have
the value ``None``.

Basic usage
===========

The ``lookup`` module is primarily concerned with validation of lookup files, but it includes a number of helper functions
to simplify the use of the lookups.

To read in a lookup map from a file, use the ``from_file`` function. For example, given a file ``lookup.json``
containing the lookup map:

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
        "bcintrhon": {
            "jset_id": null,
            "nml_id": {
                "namelist": "NLIST1",
                "field": "BCINTRHON"
            },
            "type": "real",
            "dimension": "scalar"
        },
        "ipraux": {
            "jset_id": null,
            "nml_id": {
                "namelist": "INESCO",
                "field": "IPRAUX"
            },
            "type": "real",
            "dimension": "scalar"
        },
        "fcxmul": {
            "jset_id": null,
            "nml_id": {
                "namelist": "JSANC",
                "field": "FCXMUL"
            },
            "type": "real",
            "dimension": "scalar"
        },
        "rcntren": {
            "jset_id": null,
            "nml_id": {
                "namelist": "INNBI",
                "field": "RCNTREN"
            },
            "type": "real",
            "dimension": "vector"
        }
    }

It can be read in using the ``from_file`` function. It returns the map as a dictionary:

.. highlight:: python

>>> import jetto_tools.lookup as lookup
>>> l = lookup.from_file('lookup.json')
>>> l
{'bound_ellip': {'jset_id': 'EquilEscoRef.dshEllipticity', ...}

The map can be written out using the ``to_file`` function:

.. highlight:: python

>>> import pathlib
>>> lookup.to_file(l, pathlib.Path('new_lookup.json'))
>>> lookup.to_file(l, pathlib.Path('new_lookup.json'))

if the user simply wishes to read the lookup map directly from a JSON string, they can instead use the ``from_json``
function:

.. highlight:: python

>>> print(map_json)
{
    'bound_ellip': {
        'jset_id': 'EquilEscoRef.dshEllipticity',
...
>>> l = lookup.from_json(map_json)
>>> l
{'bound_ellip': {'jset_id': 'EquilEscoRef.dshEllipticity' ...

Similarly, there is a ``to_json`` function which performs the reverse operation.

In all cases, when reading or writing a lookup map, the map is validated after reading or before writing. Validation is
performed using the `cerberus <https://docs.python-cerberus.org/en/stable/>`_ module, and is done against the schema
described above. If validation fails, the relevant function will raise a ``ValidationError`` exception. The exception
message will include a description of where in the map the failure occurred.

Advanced Use Case: Multiple jset_ids
====================================

Multiple jset_ids can be linked together if needed, for this you can use the optional ``jset_flex_id`` field in 
the ``lookup.json`` file:

::

    {
      "shot_in": {
        "jset_id": "SetUpPanel.idsIMASDBShot",
        "jset_flex_id": [
          "AdvancedPanel.catShotID",
          "AdvancedPanel.catShotID_R"],
        "nml_id": {
          "namelist": "INESCO",
          "field": "NPULSE"
        },
        "type": "int",
        "dimension": "scalar"
      }
    }
  
.. note::
  When specifying the ``jset_flex_id`` used in combinations with a :ref:`RunConfig <config-label>` an assignment will cause all the underlying
  fields ( ``jset_id``, ``jset_flex_id``, ``nml_id`` ) to be assigned that value:

  .. highlight:: python

  >>> config['shot_in'] = 59085

  However when reading the value, the ``jset_flex_id`` is ignored and the value is read from either ``jset_id`` or ``nml_id``:

  .. highlight:: python

  >>> shot_in = config['shot_in']


API Reference
=============

.. autofunction:: jetto_tools.lookup.from_file
.. autofunction:: jetto_tools.lookup.to_file
.. autofunction:: jetto_tools.lookup.from_json
.. autofunction:: jetto_tools.lookup.to_json
.. autofunction:: jetto_tools.lookup.validate
.. autoexception:: jetto_tools.lookup.ParseError
.. autoexception:: jetto_tools.lookup.ValidationError
