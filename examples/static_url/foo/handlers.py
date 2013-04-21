from waterspout.web import RequestHandler


class RenderHandler(RequestHandler):
    def get(self):
        self.render('index.html')

handlers = [
    ('/', RenderHandler)
]