from waterspout.app import App
from .handlers import handlers

app = App('foo', __name__, handlers)