from waterspout.app import Waterspout
from waterspout.web import RequestHandler


class TestHandler(RequestHandler):
    def get(self):
        self.render("test.html", name="test")


def test_jinja():
    waterspout = Waterspout(__name__, handlers=[('/', TestHandler)])
    client = waterspout.TestClient()
    body = client.get('/').body
    assert body == "test"


def test_template_path():
    waterspout = Waterspout(__name__, handlers=[('/', TestHandler)],
                            template_path="templates_2")
    client = waterspout.TestClient()
    body = client.get('/').body
    assert body == "test2"
