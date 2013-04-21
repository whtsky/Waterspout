from waterspout.app import Application
from waterspout.web import RequestHandler


class HelloWorldHandler(RequestHandler):
    def get(self):
        self.write('Hello World!')

Application([
    ('/', HelloWorldHandler)
]).run()
