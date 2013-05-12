# -*- coding: utf-8 -*-

import os
import sys
import pkgutil

try:  # Py3k
    from urllib.parse import quote
    assert quote
except ImportError:  # Py2
    from urllib import quote

from tornado.escape import to_unicode


UNQUOTE = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' \
          '0123456789' \
          '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'


def smart_quote(url):
    """
    Like urllib.parse.quote, but quote non-ascii words only.

    Example ::
        smart_quote("http://whouz.com")  # http://whouz.com
        smart_quote("喵.com")  # %E5%96%B5.com
    """
    l = [s if s in UNQUOTE else quote(s) for s in url]
    return ''.join(l)


class ObjectDict(dict):
    """
    Makes a dictionary behave like an object, with attribute-style access ::

        foo = ObjectDict()
        foo['bar'] = 42
        assert foo.bar == 42

    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


def get_root_path(import_name):
    """
    Returns the path to a package or cwd if that cannot be found.  This
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


class cached_property(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, None)
        if value is None:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
