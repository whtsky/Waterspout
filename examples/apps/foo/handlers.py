from waterspout.web import RequestHandler


class Foo(RequestHandler):
    def get(self):
        self.write('This is foo app. <br>')
        self.write('Bar is registered at <a href="/bar/">/bar/</a>')

handlers = [
    ('/', Foo)
]