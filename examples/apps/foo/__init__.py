from .handlers import handlers
from waterspout.app import App


app = App('foo', __name__, handlers)