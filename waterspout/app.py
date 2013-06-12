__all__ = ['Waterspout', 'App']

import os
import inspect

import tornado.web
import tornado.options

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .utils import get_root_path

from tornado.options import define, options

define('config', default='', help='path to the config file', type=str)


class Waterspout(object):
    """
    """
    def __init__(self, import_name=None, handlers=None, **config):
        if handlers is None:
            handlers = []
        if import_name is not None:
            self.root_path = get_root_path(import_name)
        else:
            caller = inspect.stack()[1]
            caller_module = inspect.getmodule(caller[0])
            caller_path = os.path.abspath(caller_module.__file__)
            self.root_path = os.path.dirname(caller_path)

        self.handlers = handlers

        if "static_path" not in config:
            config["static_path"] = os.path.join(self.root_path, "static")
        if "static_handler_class" not in config:
            from .web import StaticFileHandler
            config["static_handler_class"] = StaticFileHandler
        if "xsrf_cookies" not in config:
            config["xsrf_cookies"] = True
        template_path = config.get("template_path", None)
        if not (template_path and isinstance(template_path, str)):
            self.template_paths = [os.path.join(self.root_path, "templates")]
        else:
            if not os.path.isabs(template_path):
                template_path = os.path.join(self.root_path, template_path)
            self.template_paths = [os.path.abspath(template_path)]

        self.config = Config(self.root_path, config)

        self._user_loader = None

        self.filters = {}

    def filter(self, f):
        """
        Decorator to add a filter to Waterspout.

        Add your filter like ::

            waterspout = Waterspout()

            @waterspout.filter
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
          waterspout.reverse_url.
        """
        urlspec = [pattern, handler_class]
        if kwargs:
            urlspec.append(kwargs)
        if name:
            urlspec.append(name)
        self.handlers.append(urlspec)

    def register_app(self, app, prefix=''):
        """
        Register an app to waterspout.

        :param app: A Waterspout app.
        :param prefix:
          URL prefix for this app.
          Will be ``/<app_name>`` by default
        """
        if app.parent is not None:
            print("%s has been registered before." % app)
            return
        if not prefix:
            prefix = '/%s' % app.name
        self.template_paths.append(app.template_path)

        if hasattr(app, "_user_loader"):
            if self._user_loader:
                raise RuntimeError("An user loader already registered"
                                   "But %s app provided another." % app.name)
            self._user_loader = app._user_loader

        if prefix == '/':
            self.handlers += app.handlers
        else:
            for handler_class in app.handlers:
                url = '%s%s' % (prefix, handler_class[0])
                new_handler_class = [url] + list(handler_class[1:])
                self.handlers.append(tuple(new_handler_class))
        self.filters.update(app.filters)
        app.parent = self

    @property
    def application(self):
        application = tornado.web.Application(
            handlers=self.handlers,
            **self.config
        )
        auto_escape = self.config.get('autoescape', False)
        env = Environment(
            autoescape=auto_escape,
            loader=FileSystemLoader(self.template_paths)
        )
        sentry_dsn = self.config.get('sentry_dsn', None)
        if sentry_dsn:
            try:
                from raven.contrib.tornado import AsyncSentryClient
                assert AsyncSentryClient
            except ImportError:
                import logging
                logging.warning("Sentry support requires raven."
                                "Run: pip install raven")
                application.sentry_client = None
            else:
                application.sentry_client = AsyncSentryClient(sentry_dsn)

        env.filters = self.filters
        application.env = env
        application._user_loader = self._user_loader

        return application

    def TestClient(self):
        """
        Return the TestClient.

        Use it like ::

            client = waterspout.TestClient()
            assert client.get('/').body == 'Hello World'
        """
        from waterspout.testing import TestClient
        return TestClient(self.application)

    def user_loader(self, f):
        """
        Decoration to change the user loader function.

        Example ::

            @waterspout.user_loader
            def load_user(session):
                return User.get(int(session["id"]))

        :param f: the user loader function
        """
        self._user_loader = f
        return f

    def run(self):
        """
        Run your Waterspout Application.
        """
        from tornado.httpserver import HTTPServer
        import tornado.ioloop
        application = self.application
        tornado.options.parse_command_line()
        if options.config:
            tornado.options.parse_config_file(options.config)
        http_server = HTTPServer(application)

        address = self.config.get('address', '127.0.0.1')
        port = int(self.config.get('port', 8888))

        http_server.listen(port, address)
        import logging
        logging.info("Start serving at %s:%s" % (address, port))
        tornado.ioloop.IOLoop.instance().start()


class App(object):
    """
    The App in Waterspout is just like the App in Django.
    A Waterspout Application consists of plenty of Apps.

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
            caller_path = os.path.abspath(caller_module.__file__)
            self.root_path = os.path.dirname(caller_path)
        self.template_path = os.path.join(self.root_path, "templates")
        if handlers is None:
            handlers = []
        self.handlers = handlers
        self.parent = None
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
        if self.parent is not None:
            self.parent.filters.update(self.filters)
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
          Waterspout.reverse_url.
        """
        urlspec = [pattern, handler_class]
        if kwargs:
            urlspec.append(kwargs)
        if name:
            urlspec.append(name)
        self.handlers.append(urlspec)

    def __repr__(self):
        return '<App %s>' % self.name

    def TestClient(self):
        """
        Return the TestClient for the current Waterspout.

        Use it like ::

            client = app.TestClient()
            assert client.get('/').body == 'Hello World'
        """
        Waterspout = self.parent
        assert Waterspout is not None, \
            "You need to register app before testing"

        from waterspout.testing import TestClient
        return TestClient(Waterspout.Waterspout)

    def user_loader(self, f):
        """
        Decoration to change the user loader function.

        Example ::

            @app.user_loader
            def load_user(session):
                return User.get(int(session["id"]))

        :param f: the user loader function
        """
        self._user_loader = f
        return f
