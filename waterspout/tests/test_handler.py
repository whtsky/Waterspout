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
        self.write({'name': 'whtsky'})


class SessionHandler(RequestHandler):
    def get(self):
        self.session["name"] = "whtsky"
        self.session.miao = "wang"

        assert not self.session.a
        assert not self.session["b"]

handlers = [
    ('/', HelloWorldHandler),
    ('/post', PostHandler),
    ('/api', APIHandler),
    ('/session', SessionHandler)
]

application = Application(__name__, handlers=handlers, cookie_secret="..")


def test_test():
    client = application.TestClient()
    body = client.get('/').body
    assert body == to_unicode(body)


def test_session():
    client = application.TestClient()
    assert client.get('/session').code == 200


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


def test_api():
    client = application.TestClient()
    assert client.post('/api', body='..').body == '{"name": "whtsky"}'
    assert client.post('/api?callback=note', body='..').body == \
           'note({"name": "whtsky"});'