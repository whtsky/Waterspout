# -*- coding: utf-8 -*-

from waterspout import server_name

from waterspout.app import Waterspout
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

        assert self.session.miao


class MessageFlashingHandler(RequestHandler):
    def get(self):
        assert not self.get_flashed_messages()
        self.flash("aa")
        assert self.get_flashed_messages() == ["aa"]
        self.flash("aa", category="message")
        self.flash("bb", category="bb")
        assert self.get_flashed_messages(category_filter=["bb"]) == ["bb"]
        assert self.get_flashed_messages(True) == [('message', 'aa')]


handlers = [
    ('/', HelloWorldHandler),
    ('/post', PostHandler),
    ('/api', APIHandler),
    ('/session', SessionHandler),
    ('/message', MessageFlashingHandler)
]

waterspout = Waterspout(__name__, handlers=handlers, cookie_secret="..")


def test_test():
    client = waterspout.TestClient()
    body = client.get('/').body
    assert body == to_unicode(body)


def test_session():
    client = waterspout.TestClient()
    assert client.get('/session').code == 200


def test_route():
    client = waterspout.TestClient()
    assert client.get('/').body == 'Hello World'


def test_static():
    client = waterspout.TestClient()
    assert client.get('/robots.txt').headers["Server"] == server_name
    assert client.get('/static/>_<').code == 404
    response = client.get('/static/喵.txt')
    assert response.headers["Server"] == server_name
    assert response.code == 200


def test_csrf():
    client = waterspout.TestClient()
    assert client.post('/post', body='..').code == 403
    assert client.post('/api', body='..').code == 200


def test_api():
    client = waterspout.TestClient()
    assert client.post('/api', body='..').body == '{"name": "whtsky"}'
    assert client.post('/api?callback=note', body='..').body == \
           'note({"name": "whtsky"});'


def test_message_flashing():
    client = waterspout.TestClient()
    assert client.get('/message').code == 200
