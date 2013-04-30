from waterspout.app import App
from .handlers import handlers

app = App('foo', handlers=handlers)

@app.filter
def u(s):
    return s.upper()