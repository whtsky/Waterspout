from waterspout.web import RequestHandler


class Bar(RequestHandler):
    def get(self):
        self.write('bar')

handlers = [
    ('/', Bar)
]