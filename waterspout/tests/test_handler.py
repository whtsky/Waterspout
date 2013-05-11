from waterspout.app import Application
from waterspout.web import RequestHandler


class HelloWorldHandler(RequestHandler):
    def get(self):
        self.write('Hello World')


application = Application(__name__, handlers=[('/', HelloWorldHandler)])


def test_test():
    client = application.TestClient()
    from waterspout.utils import to_unicode
    body = client.get('/').body
    assert body == to_unicode(body)


def test_route():
    client = application.TestClient()
    assert client.get('/').body == 'Hello World'
