from waterspout.app import Application, App
from waterspout.web import RequestHandler


def test_register_app():

    class Foo(RequestHandler):
        def get(self):
            self.write('This is foo app.')

    handlers = [
        ('/', Foo)
    ]

    app = App('app name', __name__, handlers)

    assert app.application is None

    application = Application()
    application.register_app(app)

    assert app.application is application
