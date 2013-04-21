__all__ = ['RequestHandler']

import waterspout
import tornado.web


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

    def render_string(self, template_name, **kwargs):
        """Generate the given template with the given arguments.

        We return the generated string. To generate and write a template
        as a response, use render() above.

        :param template_name:
          name of template file
        :param kwargs:
          arguments passing to the template
        """
        var = self.application.env.get_template(template_name)
        return var.render(**kwargs)
