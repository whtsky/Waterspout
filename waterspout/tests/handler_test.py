from waterspout.app import Application
from waterspout.web import RequestHandler


class HelloWorldHandler(RequestHandler):
    def get(self):
        self.write('Hello World')


application = Application(handlers=[('/', HelloWorldHandler)])


def test_route():
    client = application.TestClient()
    assert client.get('/').body == 'Hello World'
