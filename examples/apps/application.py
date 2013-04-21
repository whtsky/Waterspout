from waterspout.app import Application

application = Application()


import bar
import foo

application.register_app(bar.app)
application.register_app(foo.app, prefix='/')

if __name__ == '__main__':
    application.run()
