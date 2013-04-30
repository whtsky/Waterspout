__all__ = ['Application', 'App']

import os
import inspect

import tornado.web
import tornado.options
from tornado.options import define, options

define('address', default='127.0.0.1', help='listen on the given address', type=str)
define('port', default=8888, help='run on the given port', type=int)
define('settings', default='', help='path to the settings file', type=str)

from jinja2 import Environment, FileSystemLoader
from .utils import get_root_path


class Application(object):
    """
    The main Waterspout Application.
    """
    def __init__(self, import_name=None, handlers=None, **settings):
        if handlers is None:
            handlers = []
        if import_name is not None:
            self.root_path = get_root_path(import_name)
        else:
            caller = inspect.stack()[1]
            caller_module = inspect.getmodule(caller[0])
            self.root_path = os.path.dirname(os.path.abspath(caller_module.__file__))

        self.handlers = handlers

        if "static_path" not in settings:
            settings["static_path"] = os.path.join(self.root_path, "static")
        self.settings = settings
        template_path = settings.get("template_path", None)
        if not (template_path and isinstance(template_path, str)):
            self.template_paths = [os.path.join(self.root_path, "templates")]
        else:
            self.template_paths = [template_path]

        self.filters = {}

    def filter(self, f):
        """
        Decorator to add a filter to Waterspout Application.

        Add your filter like ::

            application = Application()

            @application.filter
            def sort(l):
                return l.sort()

        And use it in your template ::

            {{ [1, 4, 5, 3, 2] | sort }}

        :param f: function to add as a filter.
        """
        self.filters[f.__name__] = f
        return f

    def add_handler(self, pattern, handler_class, kwargs=None, name=None):
        """
        Add a handler_class to App.

        :param pattern:
          Regular expression to be matched.  Any groups in the regex
          will be passed in to the handler's get/post/etc methods as
          arguments.
        :param handler_class: RequestHandler subclass to be invoked.
        :param kwargs:
          (optional) A dictionary of additional arguments to be passed
          to the handler's constructor.
        :param name:
          (optional) A name for this handler.  Used by
          Application.reverse_url.
        """
        urlspec = [pattern, handler_class]
        if kwargs:
            urlspec.append(kwargs)
        if name:
            urlspec.append(name)
        self.handlers.append(urlspec)

    def register_app(self, app, prefix=''):
        """
        Register an app to Application.

        :param app: A Waterspout app.
        :param prefix:
          URL prefix for this app.
          Will be ``/<app_name>`` by default
        """
        if app.application is not None:
            print("%s has been registered before." % app)
            return
        if not prefix:
            prefix = '/%s' % app.name
        self.template_paths.append(app.template_path)
        if prefix == '/':
            self.handlers += app.handlers
        else:
            for handler_class in app.handlers:
                url = '%s%s' % (prefix, handler_class[0])
                new_handler_class = [url] + list(handler_class[1:])
                self.handlers.append(tuple(new_handler_class))
        self.filters.update(app.filters)
        app.application = self

    @property
    def application(self):
        application = tornado.web.Application(
            handlers=self.handlers,
            **self.settings
        )
        if "autoescape" in self.settings:
            autoescape = self.settings["autoescape"]
        else:
            def guess_autoescape(template_name):
                if template_name is None or '.' not in template_name:
                    return False
                ext = template_name.rsplit('.', 1)[1]
                return ext in ('html', 'htm', 'xml')
            autoescape = guess_autoescape
        env = Environment(
            autoescape=autoescape,
            loader=FileSystemLoader(self.template_paths)
        )
        env.filters = self.filters
        application.env = env
        return application

    def run(self):
        """
        Run your Waterspout application.
        """
        from tornado.httpserver import HTTPServer
        import tornado.ioloop
        application = self.application
        tornado.options.parse_command_line()
        if options.settings:
            tornado.options.parse_config_file(options.settings)
        http_server = HTTPServer(application)
        http_server.listen(options.port, options.address)
        import logging
        logging.info("Start serving at %s:%s" % (options.address, options.port))
        tornado.ioloop.IOLoop.instance().start()


class App(object):
    """
    The App in Waterspout is just like the App in Django. A Waterspout Application consists of plenty of Apps.

    The minimal App ::

        from waterspout.app import App
        from waterspout.web import RequestHandler


        class Foo(RequestHandler):
            def get(self):
                self.write('This is foo app.')

        handlers = [
            ('/', Foo)
        ]

        app = App('app name', __name__, handlers)
    """
    def __init__(self, name, import_name=None, handlers=None):
        self.name = name
        if import_name is not None:
            self.root_path = get_root_path(import_name)
        else:
            caller = inspect.stack()[1]
            caller_module = inspect.getmodule(caller[0])
            self.root_path = os.path.dirname(os.path.abspath(caller_module.__file__))
        self.template_path = os.path.join(self.root_path, "templates")
        if handlers is None:
            handlers = []
        self.handlers = handlers
        self.application = None
        self.filters = {}

    def filter(self, f):
        """
        Decorator to add a filter to Waterspout App.

        Add your filter like ::

            app = App('test')

            @app.filter
            def sort(l):
                return l.sort()

        And use it in your template ::

            {{ [1, 4, 5, 3, 2] | sort }}

        :param f: function to add as a filter.
        """
        self.filters[f.__name__] = f
        if self.application is not None:
            self.application.filters.update(self.filters)
        return f

    def add_handler(self, pattern, handler_class, kwargs=None, name=None):
        """
        Add a handler_class to App.

        :param pattern:
          Regular expression to be matched.  Any groups in the regex
          will be passed in to the handler's get/post/etc methods as
          arguments.
        :param handler_class: RequestHandler subclass to be invoked.
        :param kwargs:
          (optional) A dictionary of additional arguments to be passed
          to the handler's constructor.
        :param name:
          (optional) A name for this handler.  Used by
          Application.reverse_url.
        """
        urlspec = [pattern, handler_class]
        if kwargs:
            urlspec.append(kwargs)
        if name:
            urlspec.append(name)
        self.handlers.append(urlspec)

    def __repr__(self):
        return '<App %s>' % self.name
