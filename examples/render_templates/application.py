import os

from waterspout.app import Application

application = Application()


import foo

application.register_app(foo.app, prefix='/')

if __name__ == '__main__':
    application.run()
