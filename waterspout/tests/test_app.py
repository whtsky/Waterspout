from waterspout.app import Waterspout, App
from waterspout.web import RequestHandler


def test_register_app():

    class Foo(RequestHandler):
        def get(self):
            self.write('This is foo app.')

    handlers = [
        ('/', Foo)
    ]

    app = App('app name', __name__, handlers)

    assert app.parent is None

    waterspout = Waterspout()
    waterspout.register_app(app)

    assert app.parent is waterspout


def test_domain():

    app = App('test', __name__, handlers=[])

    waterspout = Waterspout()
    waterspout.register_app(app, domain='miao.com')

    assert waterspout.handlers == ['^miao.com$', []]
