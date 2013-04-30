__all__ = ['RequestHandler']

import waterspout
import tornado.web
from waterspout.utils import cached_property


class RequestHandler(tornado.web.RequestHandler):
    def clear(self):
        """Resets all headers and content for this response."""
        super(RequestHandler, self).clear()
        self._headers["Server"] = waterspout.server_name

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
        class Session(object):
            def __getattr__(s, name):
                return self.get_secure_cookie(name)

            def __setattr__(s, name, value):
                return self.set_secure_cookie(name, value)

        return Session()

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
