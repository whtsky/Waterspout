__all__ = ['Application', 'App']

import os

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
    def __init__(self, handlers=None, default_host="", transforms=None,
                 wsgi=False, **settings):
        if handlers is None:
            handlers = []
        self.handlers = handlers
        self.default_host = default_host
        self.transforms = transforms
        self.wsgi = wsgi
        self.settings = settings
        template_path = settings.get("template_path", None)
        if not (template_path and isinstance(template_path, str)):
            self.template_paths = []
        else:
            self.template_paths = [template_path]

    def add_handler(self, rule, handler):
        """
        Directly add a handler to Application.
        Note that adding handlers to an App and
        register apps to Application is recommended.

        :param rule:
        :param handler:
        """
        self.handlers.append([rule, handler])

    def register_app(self, app, prefix=''):
        """
        Register an app to Application.

        :param app: A Waterspout app.
        :param prefix:
          URL prefix for this app.
          Will be ``/<app_name>`` by default
        """
        if app.registered:
            print("%s has been registered before." % app)
            return
        if not prefix:
            prefix = '/%s' % app.name
        self.template_paths.append(app.template_path)
        if prefix == '/':
            self.handlers += app.handlers
        else:
            for handler in app.handlers:
                url = '%s%s' % (prefix, handler[0])
                new_handler = [url] + list(handler[1:])
                self.handlers.append(tuple(new_handler))
        app.registered = True

    @property
    def application(self):
        application = tornado.web.Application(
            handlers=self.handlers,
            default_host=self.default_host,
            transforms=self.transforms,
            wsgi=self.wsgi,
            **self.settings
        )
        application.env = Environment(
            loader=FileSystemLoader(self.template_paths)
        )
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
    def __init__(self, name, import_name, handlers=None):
        self.name = name
        self.import_name = import_name
        self.root_path = get_root_path(import_name)
        self.template_path = os.path.join(self.root_path, "templates")
        if handlers is None:
            handlers = []
        self.handlers = handlers
        self.registered = False

    def add_handler(self, rule, handler):
        """
        Add a handler to App.
        """
        self.handlers.append([rule, handler])

    def __repr__(self):
        return '<App %s>' % self.name
