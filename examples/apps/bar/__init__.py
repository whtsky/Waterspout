from .handlers import handlers
from waterspout.app import App


app = App('bar', __name__, handlers)