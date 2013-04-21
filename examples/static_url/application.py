import os
from waterspout.app import Application

base = os.path.abspath(os.path.dirname(__file__))
application = Application(static_path=os.path.join(base, "static"))


import foo

application.register_app(foo.app, prefix='/')

if __name__ == '__main__':
    application.run()
