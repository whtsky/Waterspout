import os
import pkgutil
from tornado.util import ObjectDict


def get_root_path(import_name):
    """Returns the path to a package or cwd if that cannot be found.  This
    returns the path of a package or the folder that contains a module.

    Not to be confused with the package path returned by :func:`find_package`.
    """
    loader = pkgutil.get_loader(import_name)
    if loader is None or import_name == '__main__':
        # import name is not found, or interactive/main module
        return os.getcwd()
    # For .egg, zipimporter does not have get_filename until Python 2.7.
    if hasattr(loader, 'get_filename'):
        filepath = loader.get_filename(import_name)
    else:
        # Fall back to imports.
        __import__(import_name)
        filepath = sys.modules[import_name].__file__
    # filepath is import_name.py for a module, or __init__.py for a package.
    return os.path.dirname(os.path.abspath(filepath))
