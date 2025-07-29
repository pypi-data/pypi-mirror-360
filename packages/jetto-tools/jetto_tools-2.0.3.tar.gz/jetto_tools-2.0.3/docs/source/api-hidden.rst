.. Generate API reference pages, but don't display these in tables.
.. This extra page is a work around for sphinx not having any support for
.. hiding an autosummary table.

===============
API autosummary
===============

.. This folder should be documented differently jetto_tools.templates
.. Explicitly list submodules here
   jetto_tools.jset
.. autosummary::
   :toctree: generated/
   :recursive:
   :template: custom-module-template.rst

   jetto_tools.binary
   jetto_tools.classes
   jetto_tools.config
   jetto_tools.__init__
   jetto_tools.jams
   jetto_tools.job
   jetto_tools.lookup
   jetto_tools.mast_jetto_tools
   jetto_tools.matlab
   jetto_tools.misc
   jetto_tools.namelist
   jetto_tools.nested_dicts
   jetto_tools.raptor
   jetto_tools.results_gui
   jetto_tools.run
   jetto_tools.settings
   jetto_tools.setup_logging
   jetto_tools.template
   jetto_tools.tkinter_helpers
   jetto_tools.transp
   jetto_tools.turb_analysis
   jetto_tools._utils
   jetto_tools.version

