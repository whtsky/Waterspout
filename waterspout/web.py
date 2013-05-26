import waterspout
import tornado.web
import tornado.escape

from waterspout.utils import Session

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
            self._session = Session(self)

        return self._session

    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        if hasattr(self, '_session'):
            self.session.save()
        super(WaterspoutHandler, self).finish(chunk)


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

    def get_current_user(self):
        user_loader = self.application._user_loader
        if user_loader:
            return self.application._user_loader(self.session)

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

    def flash(self, message, category='message'):
        """Flashes a message to the next request.  In order to remove the
        flashed message from the session and to display it to the user,
        the template has to call :func:`get_flashed_messages`.

        :param message: the message to be flashed.
        :param category: the category for the message.  The following values
                         are recommended:
                         ``'message'`` for any kind of message,
                         ``'error'`` for errors,
                         ``'info'`` for information messages and
                         ``'warning'`` for warnings.
                         However any kind of string can be used as category.
        """
        session = self.session
        flashes = session.get('_flashes', [])
        flashes.append((category, message))
        session['_flashes'] = flashes

    def get_flashed_messages(self, with_categories=False, category_filter=[]):
        """Pulls all flashed messages from the session and returns them.
        Further calls in the same request to the function will return
        the same messages.  By default just the messages are returned,
        but when `with_categories` is set to `True`, the return value will
        be a list of tuples in the form ``(category, message)`` instead.

        Filter the flashed messages to one or more categories by providing
        those categories in `category_filter`.
        This allows rendering categories in separate html blocks.
        The `with_categories` and `category_filter` arguments are distinct:

        * `with_categories` controls whether categories are returned with
          message text
          (`True` gives a tuple, where `False` gives just the message text).
        * `category_filter` filters the messages down to only those matching
          the provided categories.


        :param with_categories: set to `True` to also receive categories.
        :param category_filter: whitelist of categories to limit return values
        """
        session = self.session
        flashes = session.get('_flashes', [])
        if category_filter:
            remained = filter(lambda f: f[0] not in category_filter, flashes)
            session['_flashes'] = remained
            flashes = filter(lambda f: f[0] in category_filter, flashes)
        else:
            session['_flashes'] = []
        if not with_categories:
            return [x[1] for x in flashes]
        return flashes


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
                chunk = "%s(%s);" % (callback,
                                     tornado.escape.to_unicode(chunk))
                self.set_header("Content-Type",
                                "application/javascript; charset=UTF-8")
            else:
                self.set_header("Content-Type",
                                "application/json; charset=UTF-8")
        super(APIHandler, self).write(chunk)


class StaticFileHandler(tornado.web.StaticFileHandler, WaterspoutHandler):
    pass
