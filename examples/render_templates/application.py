import os

from waterspout.app import Application

application = Application(
    template_path=os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               "templates")
)


import foo

application.register_app(foo.app, prefix='/')

if __name__ == '__main__':
    application.run()
