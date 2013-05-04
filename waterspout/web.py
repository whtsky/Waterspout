__all__ = ['RequestHandler', 'APIHandler']

import waterspout
import tornado.web
import tornado.escape


class WaterspoutHandler(tornado.web.RequestHandler):
    """
    The most basic RequestHandler for Waterspout.
    Sentry support inside.
    """
    def set_default_headers(self):
        self._headers["Server"] = waterspout.server_name

    @property
    def sentry_client(self):
        """
        Returns the sentry client configured in the application.
        """
        return self.application.sentry_client

    def get_sentry_data_from_request(self):
        """
        Extracts the data required for 'sentry.interfaces.Http' from the
        current request being handled by the request handler

        :param return: A dictionary.
        """
        return {
            'sentry.interfaces.Http': {
                'url': self.request.full_url(),
                'method': self.request.method,
                'data': self.request.arguments,
                'query_string': self.request.query,
                'cookies': self.request.headers.get('Cookie', None),
                'headers': dict(self.request.headers),
            }
        }

    def get_sentry_user_info(self):
        """
        Data for sentry.interfaces.User

        Default implementation only sends `is_authenticated` by checking if
        `tornado.web.RequestHandler.get_current_user` tests postitively for on
        Truth calue testing
        """
        return {
            'sentry.interfaces.User': {
                'is_authenticated': True if self.get_current_user() else False
            }
        }

    def get_sentry_extra_info(self):
        """
        Subclass and implement this method if you need to send any extra
        information
        """
        return {
            'extra': {
            }
        }

    def get_default_context(self):
        data = {}

        # Update request data
        data.update(self.get_sentry_data_from_request())

        # update user data
        data.update(self.get_sentry_user_info())

        # Update extra data
        data.update(self.get_sentry_extra_info())

        return data

    def _capture(self, call_name, data=None, **kwargs):
        if data is None:
            data = self.get_default_context()
        else:
            default_context = self.get_default_context()
            if isinstance(data, dict):
                default_context.update(data)
            else:
                default_context['extra']['extra_data'] = data
            data = default_context

        return getattr(self.sentry_client, call_name)(data=data, **kwargs)

    def captureException(self, exc_info=None, **kwargs):
        return self._capture('captureException', exc_info=exc_info, **kwargs)

    def captureMessage(self, message, **kwargs):
        return self._capture('captureMessage', message=message, **kwargs)

    def write_error(self, status_code, **kwargs):
        """Override implementation to report all exceptions to sentry.
        """
        rv = super(WaterspoutHandler, self).write_error(status_code, **kwargs)
        if self.sentry_client:
            self.captureException(exc_info=kwargs.get('exc_info'))
        return rv


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
