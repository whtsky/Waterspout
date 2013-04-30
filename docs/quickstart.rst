Quickstart
==============

You need to have Waterspout installed to read this page. If you do not, head over to the :ref:`installation` section first.

Hello World
--------------

A Hello World application in Waterspout ::

    from waterspout.app import Application
    from waterspout.web import RequestHandler


    class HelloWorldHandler(RequestHandler):
        def get(self):
            self.write('Hello World!')

    Application([
        ('/', HelloWorldHandler)
    ]).run()
