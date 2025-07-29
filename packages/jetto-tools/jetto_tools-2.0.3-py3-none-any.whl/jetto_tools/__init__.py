# This file is part of jetto_tools
# You should have received the jetto_tools LICENSE file with this project.
import pkg_resources

# First thing for import, try to determine jetto_tools version
try:
    __version__ = pkg_resources.get_distribution("jetto_tools").version
except Exception:  # pylint: disable=broad-except
    # Try local wrongly install copy
    try:
        from version import __version__
    except Exception:  # pylint: disable=broad-except
        # Local copy or not installed with setuptools.
        # Disable minimum version checks on downstream libraries.
        __version__ = "0.0.0"

# Set up logging
import jetto_tools.setup_logging  # noqa: F401 Import with side effects

# Regular imports
import logging

root_logger = logging.getLogger('jetto_tools')
#root_logger.setLevel(logging.TRACE)

# Import all Python files as submodules
_core_modules = [
    '_utils',
    'common',
    'binary',
    'classes',
    'config',
    'catalog',
    #'jams_omas.py',  # WIP, not importable in this state
    'job',
    'jset',
    'lookup',
    'matlab',
    'misc',
    'namelist',
    'nested_dicts',
    'raptor',
    #'results_gui',  # WIP, not meant to be importable yet
    'run',
    #'settings',  # WIP, not meant to be importable yet
    #'setup_logging'  # We import this manually first to have fancy logging
    'template',
    #'tkinter_helpers', # imported conditionally below
    #'turb_analysis',  # Not importable in this state
    #'version'  # We import this manually first to have correct versions
]
__all__ = [str(path) for path in _core_modules]

_my_folder = __file__.rsplit('/', 1)[0]
_template_path = '/'.join([_my_folder, 'templates'])

# Hijack __all__ and * to import the core modules
from . import *  # noqa: F401, F403, E402

# Only available if OMAS is available
try:
    from . import jams
    HAS_JAMS = True
except ImportError:
    HAS_JAMS = False

# Only available if netCDF4 is available
try:
    from . import transp
    HAS_TRANSP = True
except ImportError:
    HAS_TRANSP = False

try:
    from . import tkinter_helpers
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
