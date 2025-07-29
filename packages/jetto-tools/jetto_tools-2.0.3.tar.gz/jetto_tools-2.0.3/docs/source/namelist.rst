.. _nml-label:

===============
Namelist module
===============

Introduction
============

Namelist files are used to supply configuration information at runtime to a Fortran executable. JAMS produces a namelist
file as part of configuring a JETTO run. This ``namelist`` module allows a client application to read,
modify and write a namelist file. The module attempts to maintain compatibility with the JAMS application to the extent
possible, producing a namelist file in a similar format.

This module does not support creation of a namelist file *ab initio*: a template file must be provided, in which all of
the settings that the client wishes to modify are already present. A ``Namelist`` object can be created from this file,
and the client can modify the namelist file using the interface provided by this object.

This module is primarily intended to be used by other library code in the ``jetto-pythontools`` package for configuring
JETTO runs and scans. However, with care, it can be used by any client application to perform low-level manipulation of
namelist files.

The bulk of the module is contained in the ``Namelist`` class; however, the module also provides two convenience functions,
``read`` and ``write``, which can be used to quickly read in and write out ``Namelist`` objects from and to namelist files.

Namelist files and terminology
==============================

JAMS produces namelist files in a particular format, adding a header to the file and to the individual namelists. A
typical example is:

::

    ================================================================================
                                 CODE INPUT NAMELIST FILE
    ================================================================================

    Application                    : JETTO
    JAMS Version                   : v060619
    Date                           : 08/07/2019
    Time                           : 16:43:37

    JAMS GIT information:-

    Current GIT repository         : /home/sim/cmg/jams/v060619/java
    Current GIT release tag        : Release-v060619
    Current GIT branch             : master
    Last commit SHA1-key           : 638c06e07629f5d100da166aac3e2d2da5727631
    Repository status              : Clean


    --------------------------------------------------------------------------------
     Namelist : NLIST1
    --------------------------------------------------------------------------------

     &NLIST1
      BCINTRHON=  0.7      ,
      ...
     &END

    --------------------------------------------------------------------------------
     Namelist : NLIST2
    --------------------------------------------------------------------------------

     &NLIST2
      ISYNTHDIAG=  0        ,
      ...
     &END

In the above file, everything prior to the first namelist is the *namelist file header*. Each namelist within the file
is delimited by a start marker ``&NAME`` and an end marker ``&END``. Each namelist has its own *namelist header* e.g.

::

    --------------------------------------------------------------------------------
     Namelist : NLIST1
    --------------------------------------------------------------------------------

Note that the file header and namelist headers are ignored by the Fortran application at runtime.

An individual namelist consists of a set of fields and values. Any field in the namelist file is then uniquely identified
by the namelist and the field name. An example namelist is:

::

    &INNBI
        BMASS3   =  2.0      ,
        ENERG3   =  80000.0  ,
        JPINI3   =  1        ,  0        ,  0        ,  0        ,  0        ,
                    0        ,  0        ,  0        ,  0        ,  0        ,
                    0        ,  0        ,
        NBREF3   =  40       ,
        PFRAC3   =  0.5      ,  0.3      ,  0.2      ,
    &END

The above format is that produced by JAMS: the format produced when writing a file using the ``namelist`` module is
cosmetically different, but contains the same content:

::

    &INNBI
        BMASS3 = 2.0,
        ENERG3 = 80000.0,
        JPINI3 = 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        NBREF3 = 40,
        PFRAC3 = 0.5, 0.3, 0.2,
    &END

Basic usage
===========

Reading namelist files
----------------------

A namelist file can be read by calling the ``read`` function of the ``namelist`` module: a ``Namelist`` object is returned:

.. highlight:: python

>>> from pathlib import Path
>>> from jetto_tools.namelist import read
>>> nml = read(Path('/path/to/namelist.in'))

The ``namelist`` module is flexible in the format of the files it will accept. If the namelist file contains a header,
the module will attempt to parse it and extract the contents. If any expected field in the header is omitted from the file,
the module will fill in the missing field with a default value. Any unrecognised header fields will be ignored and discarded.

Writing namelist files
----------------------

A namelist file can be written to the file system by calling the ``write`` function of the ``namelist`` module:

.. highlight:: python

>>> from jetto_tool.namelist import write
>>> write(nml, Path('/path/to/namelist.in'))

Note that a call to the write function will automatically set the date and time in the written namelist file header to
the current date and time.

The ``write`` function writes files in the format defined above, with the exception that it does not support production
of the individual namelist headers. Since these are presumed to be purely an aid to readability, this is not considered significant.

An alternative approach is to use the ``str`` built-in: this will give the string representation of the namelist file:

::

    >>> print(str(nml))
    ================================================================================
                                 CODE INPUT NAMELIST FILE
    ================================================================================

    Application                    : JETTO
    JAMS Version                   : v060619
    Date                           : 08/07/2019
    Time                           : 16:43:37

    JAMS GIT information:-

    Current GIT repository         : /home/sim/cmg/jams/v060619/java
    Current GIT release tag        : Release-v060619
    Current GIT branch             : master
    Last commit SHA1-key           : 638c06e07629f5d100da166aac3e2d2da5727631
    Repository status              : Clean


    &NLIST1
        BCINTRHON = 0.7,
        BTIN = 4.5, 4.5,
    ...

Note however, that this will not cause any setting of the date and time fields in the header: they will retain their
previously set values.

Accessing and modifying namelist files
--------------------------------------

As noted above, a ``Namelist`` object can be created by calling the ``namelist.read`` function and passing the appropriate
path. Alternatively, an object can be created directly by passing the contents of a namelist file:

.. highlight:: python

>>> with open('/path/to/jetto.in', 'r') as f:
...   s = f.read()
>>> nml = namelist.Namelist(s)

The namelist file header fields can be accessed via the attributes of the ``Namelist`` class. These are:

=========================  =================  =================
  Header Field              Attribute                Type
=========================  =================  =================
Application                 ``application``         ``str``
JAMS Version                ``version``             ``str``
Date                        ``date``          ``datetime.date``
Time                        ``time``          ``datetime.time``
Current GIT Repository      ``repo``                ``str``
Current GIT release tag     ``tag``                 ``str``
Current GIT branch          ``branch``              ``str``
Last commit SHA-1 key       ``sha``                 ``str``
Repository status           ``repo``                ``str``
=========================  =================  =================

For example:

.. highlight:: python

>>> nml.branch
'master'
>>> nml.branch = 'development'
>>> nml.branch
'development'


The namelists within the file can be accessed and modified using the ``Namelist`` API. To check if a given field exists
in the namelist file, use the ``exists`` function:

.. highlight:: python

>>> nml.exists('INNBI', 'BMASS3')
True
>>> nml.exists('INNBI', 'bar')
False
>>> nml.exists('foo', 'bar')
False

To get the value of a field within the namelists file, use the ``get_field`` function:

.. highlight:: python

>>> nml.get_field('INNBI', 'BMASS3')
2.0

If you attempt to get a field which does not exist, a ``NamelistError`` will be raised.

Similarly, to set the value of a field within the namelists file, use the ``set_field`` function:

.. highlight:: python

>>> nml.get_field('INNBI', 'BMASS3')
2.0
>>> nml.set_field('INNBI', 'BMASS3', 3.0)
>>> nml.get_field('INNBI', 'BMASS3')
3.0

Like ``get_field``, ``set_field`` will raise a ``NamelistError`` if you try to set the value of a field which does not
exist.

Note that no type-checking is performed when setting the value of a field: it is up to the client to provide the correct
type when setting a field value.

API Reference
=============

.. autofunction:: jetto_tools.namelist.read
.. autofunction:: jetto_tools.namelist.write

.. autoclass:: jetto_tools.namelist.Namelist
    :members: exists, get_field, set_field

.. autoexception:: jetto_tools.namelist.NamelistError

