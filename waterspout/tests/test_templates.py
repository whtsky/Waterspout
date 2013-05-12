from waterspout.app import Application
from waterspout.web import RequestHandler


class TestHandler(RequestHandler):
    def get(self):
        self.render("test.html", name="test")


application = Application(__name__, handlers=[('/', TestHandler)])


def test_jinja():
    client = application.TestClient()
    body = client.get('/').body
    assert body == "test"


def test_template_path():
    application = Application(__name__, handlers=[('/', TestHandler)],
                              template_path="templates_2")
    client = application.TestClient()
    body = client.get('/').body
    assert body == "test2"
