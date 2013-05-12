import waterspout
import tornado.web
import tornado.escape


try:
    from raven.contrib.tornado import SentryMixin
    assert SentryMixin
except ImportError:
    SentryMixin = object


class WaterspoutHandler(tornado.web.RequestHandler, SentryMixin):
    """
    The most basic RequestHandler for Waterspout.
    Sentry support inside.
    """
    def set_default_headers(self):
        self._headers["Server"] = waterspout.server_name

    def _capture(self, call_name, data=None, **kwargs):
        if not self.get_sentry_client():
            return
        super(SentryMixin, self)._capture(self, call_name, data, **kwargs)


class RequestHandler(WaterspoutHandler):
    """
    Base RequestHandler for Waterspout Application
    """
    def render(self, template_name, **kwargs):
        """
        Renders the template with the given arguments as the response.

        :param template_name:
          name of template file
        :param kwargs:
          arguments passing to the template
        """
        self.write(self.render_string(template_name=template_name, **kwargs))

    @property
    def session(self):
        """
        The session object works pretty much like an ordinary dict ::

            class SessionHandler(RequestHandler):
                def get(self):
                    session = self.session
                    self.write(session['name'])

                def post(self):
                    self.session['name'] = 'whtsky'

        .. attention ::
          Session requires ``cookie_secret`` setting.
        """
        if not hasattr(self, '_session'):
            class Session(object):
                def __getattr__(s, name):
                    return self.get_secure_cookie(name)

                def __setattr__(s, name, value):
                    return self.set_secure_cookie(name, value)
            self._session = Session()

        return self._session

    @property
    def globals(self):
        """
        An alias for Environment.globals in Jinja2.
        """
        return self.application.env.globals

    @property
    def template_namespace(self):
        """
        A dictionary to be used as the default template namespace.
        """
        return dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url
        )

    def render_string(self, template_name, **kwargs):
        """Generate the given template with the given arguments.

        We return the generated string. To generate and write a template
        as a response, use render() above.

        :param template_name:
          name of template file
        :param kwargs:
          arguments passing to the template
        """
        env = self.application.env
        env.globals.update(self.template_namespace)
        var = env.get_template(template_name)
        return var.render(**kwargs)


class APIHandler(WaterspoutHandler):
    """
    Handler class for writing JSON API
    """
    def check_xsrf_cookie(self):
        pass

    def write(self, chunk, callback=None):
        """
        Writes the given chunk to the output buffer.

        :param chunk:
          chunk to be written to the output buffer.
          If the given chunk is a dictionary or a list, we write it as
          JSON and set the Content-Type of the response to be
          ``application/json``.
          (if you want to send JSON as a different ``Content-Type``, call
          set_header *after* calling write()).

          Note that lists are converted to JSON *can* cause a potential
          cross-site security vulnerability.  More details at
          http://is.gd/2LqAcE
        :param callback:
          callback function name for JSONP.
          We will look for ``callback`` argument if callback is not provided.
          Waterspout will write your chunk as JSONP if callback is not None.
        """
        if isinstance(chunk, (dict, list)):
            chunk = tornado.escape.json_encode(chunk)
            if callback is None:
                callback = self.get_argument('callback', None)
            if callback:
                chunk = "%s(%s)" % (callback, tornado.escape.to_unicode(chunk))
                self.set_header("Content-Type",
                                "application/javascript; charset=UTF-8")
            else:
                self.set_header("Content-Type",
                                "application/json; charset=UTF-8")
        super(APIHandler, self).write(chunk)


class StaticFileHandler(tornado.web.StaticFileHandler, WaterspoutHandler):
    pass
