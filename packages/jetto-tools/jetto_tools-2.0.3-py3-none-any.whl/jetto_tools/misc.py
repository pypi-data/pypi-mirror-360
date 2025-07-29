from pathlib import Path
import importlib

from IPython import embed

def dump_package_versions(modules=None, log_func=print):
    """ Print package versions to terminal

    Kwargs:
      - modules: modules to check. Leave empty for common modules
      - log_func: Function with signature func(str) that displays the string
    """
    versions = get_package_versions(modules=modules)
    for name, (version, path) in versions.items():
        if version is None:
            log_func('{!s} not found'.format(name))
        else:
            log_func('{!s} is version "{!s}" at "{!s}"'.format(name, version, path))

def get_package_versions(modules=None):
    """ Grab version and folder of importable packages

    Kwargs:
      - modules: modules to check. Leave empty for common modules

    Returns:
      - versions: Dictionairy with keys module names and values tuple
                  with version and path to installed module
    """
    if modules is None:
        # By default, check the modules that often give trouble
        modules = ['matplotlib', 'numpy', 'pandas', 'tables', 'xarray', 'netCDF4', 'dask']

    versions = {}
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            versions[module_name] = (None, None)
        else:
            versions[module_name] = (module.__version__,
                                     Path(module.__path__[0]))

    versions['jetto_tools'] = get_repo_status()
    return versions

def get_repo_status():
    """ Grab version and folder of installed jetto_tools
    """
    this_file = Path(__file__)
    this_file_folder = this_file.parent
    module_name = 'jetto_tools'
    jetto_tools = importlib.import_module(module_name)
    jetto_tools_path = Path(jetto_tools.__path__[0])

    # Not sure if this can even happen
    if not this_file_folder.samefile(jetto_tools_path):
        raise Exception("Importing {!r} results in different path than where this file lives".format(module_name))

    return jetto_tools.__version__, jetto_tools_path


def decode_catalog_path(path: str):
    """ Decode a path to a catalog file into parts

    Args:
        path: Path to the catalog file

    Returns:
        A dictionary with the decoded parts of the catalog path, currently:
        - seqno: Sequence number [int]
        - date: Month and year catalog was generated [str]
        - shotno: Shot number [int]
        - machine: Machine code was run for [str]
        - code: Name of code that was run [str]
        - user: Name of the user storing the catalog [str]
    """
    path = str(Path(path).resolve())
    split = path.split('/')
    seq = split[-1]
    decoded = {
            'seqno': int(seq.split('#')[1]),
            'date': split[-2],
            'shotno': int(split[-3]),
            'machine': split[-4],
            'code': split[-5],
            'user': split[-8],
    }
    return decoded
