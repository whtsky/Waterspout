# -*- coding: utf-8 -*-

from waterspout import server_name

from waterspout.app import Application
from waterspout.web import RequestHandler, APIHandler
from waterspout.utils import to_unicode


class HelloWorldHandler(RequestHandler):
    def get(self):
        self.write('Hello World')


class PostHandler(RequestHandler):
    def post(self):
        self.write('success')


class APIHandler(APIHandler):
    def post(self):
        self.write('success')


handlers = [
    ('/', HelloWorldHandler),
    ('/post', PostHandler),
    ('/api', APIHandler)
]

application = Application(__name__, handlers=handlers)


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


def test_csrf():
    client = application.TestClient()
    assert client.post('/post', body='..').code == 403
    assert client.post('/api', body='..').code == 200
