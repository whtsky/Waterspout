# -*- coding: utf-8 -*-

from waterspout import server_name

from waterspout.app import Application
from waterspout.web import RequestHandler
from waterspout.utils import to_unicode


class HelloWorldHandler(RequestHandler):
    def get(self):
        self.write('Hello World')


application = Application(__name__, handlers=[('/', HelloWorldHandler)])


def test_test():
    client = application.TestClient()
    body = client.get('/').body
    assert body == to_unicode(body)


def test_route():
    client = application.TestClient()
    assert client.get('/').body == 'Hello World'


def test_static():
    client = application.TestClient()
    assert client.get('/robots.txt').headers["Server"] == server_name
    assert client.get('/static/>_<').code == 404
    response = client.get('/static/喵.txt')
    assert response.headers["Server"] == server_name
    assert response.code == 200
