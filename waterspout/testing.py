import sys
import time

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.testing import bind_unused_port
from tornado.util import raise_exc_info

from waterspout.utils import to_unicode, smart_quote


class TestClient(object):
    """
    A test client for writing test for **Tornado Application**

    Usage ::

        client = TestClient(application)

        assert client.get('/').body == 'Hello World'
        assert client.post('/').body == '0 o'
    """
    def __init__(self, application):
        self.application = application

        self.__stopped = False
        self.__running = False
        self.__failure = None
        self.__stop_args = None
        self.__timeout = None

        self.setUp()

    def setUp(self):
        sock, port = bind_unused_port()
        self.__port = port

        self.io_loop = self.get_new_ioloop()
        self.io_loop.make_current()
        self.http_server = HTTPServer(self.application, io_loop=self.io_loop)
        self.http_client = AsyncHTTPClient(io_loop=self.io_loop)
        self.http_server.add_sockets([sock])

    def get_new_ioloop(self):
        """Creates a new `.IOLoop` for this test.  May be overridden in
        subclasses for tests that require a specific `.IOLoop` (usually
        the singleton `.IOLoop.instance()`).
        """
        return IOLoop()

    def request(self, url, method='GET',
                headers=None, body=None, **kwargs):
        """
        Start a request to the application and return the response.

        .. attention: Response.body is converted to unicode.

        :param string url: URL to fetch, e.g. "/"
        :param string method: HTTP method, e.g. "GET" or "POST"
        :param headers: Additional HTTP headers to pass on the request
        :param body: HTTP body to pass on the request
        """
        if '//' not in url:
            url = self.get_url(url)
        request = HTTPRequest(url=smart_quote(url), method=method,
                              headers=headers, body=body, **kwargs)
        self.http_client.fetch(request, self.stop)
        response = self.wait()

        response._body = to_unicode(response._get_body())

        return response

    def options(self, url, headers=None, body=None, **kwargs):
        return self.request(url, method='OPTIONS', headers=headers,
                            body=body, **kwargs)

    def get(self, url, headers=None, body=None, **kwargs):
        return self.request(url, method='GET', headers=headers,
                            body=body, **kwargs)

    def head(self, url, headers=None, body=None, **kwargs):
        return self.request(url, method='HEAD', headers=headers,
                            body=body, **kwargs)

    def post(self, url, headers=None, body=None, **kwargs):
        return self.request(url, method='POST', headers=headers,
                            body=body, **kwargs)

    def put(self, url, headers=None, body=None, **kwargs):
        return self.request(url, method='PUT', headers=headers,
                            body=body, **kwargs)

    def delete(self, url, headers=None, body=None, **kwargs):
        return self.request(url, method='DELETE', headers=headers,
                            body=body, **kwargs)

    def trace(self, url, headers=None, body=None, **kwargs):
        return self.request(url, method='TRACE', headers=headers,
                            body=body, **kwargs)

    def connect(self, url, headers=None, body=None, **kwargs):
        return self.request(url, method='CONNECT', headers=headers,
                            body=body, **kwargs)

    def get_http_port(self):
        """Returns the port used by the server.

        A new port is chosen for each test.
        """
        return self.__port

    def get_protocol(self):
        return 'http'

    def get_url(self, path):
        """Returns an absolute url for the given path on the test server."""
        return '%s://localhost:%s%s' % (self.get_protocol(),
                                        self.get_http_port(), path)

    def close(self):
        """CLose http_server, io_loop by sequence, to ensure the environment
        is cleaned up and invoking `setup` successfully within next test
         function

        It is suggested to be called in `TestCase.tearDown`
        """
        self.http_server.stop()
        if (not IOLoop.initialized() or
                self.http_client.io_loop is not IOLoop.instance()):
            self.http_client.close()

        if (not IOLoop.initialized() or
                self.io_loop is not IOLoop.instance()):
            # Try to clean up any file descriptors left open in the ioloop.
            # This avoids leaks, especially when tests are run repeatedly
            # in the same process with autoreload (because curl does not
            # set FD_CLOEXEC on its file descriptors)
            self.io_loop.close(all_fds=True)

    def stop(self, _arg=None, **kwargs):
        """Stops the `.IOLoop`, causing one pending (or future) call to
         `wait()` to return.

        Keyword arguments or a single positional argument passed to
         `stop()` are saved and will be returned by `wait()`.
        """
        assert _arg is None or not kwargs
        self.__stop_args = kwargs or _arg
        if self.__running:
            self.io_loop.stop()
            self.__running = False
        self.__stopped = True

    def wait(self, condition=None, timeout=5):
        """Runs the IOLoop until stop is called or timeout has passed.

        In the event of a timeout, an exception will be thrown.

        If condition is not None, the IOLoop will be restarted after stop()
        until condition() returns true.
        """
        if not self.__stopped:
            if timeout:
                def timeout_func():
                    try:
                        raise Exception(
                            'Async operation timed out after %s seconds' %
                            timeout)
                    except Exception:
                        self.__failure = sys.exc_info()
                    self.stop()
                if self.__timeout is not None:
                    self.io_loop.remove_timeout(self.__timeout)
                timeout = self.io_loop.add_timeout(time.time() + timeout,
                                                   timeout_func)
                self.__timeout = timeout
            while True:
                self.__running = True
                self.io_loop.start()
                if (self.__failure is not None or
                        condition is None or condition()):
                    break
        assert self.__stopped
        self.__stopped = False
        self.__rethrow()
        result = self.__stop_args
        self.__stop_args = None
        return result

    def __rethrow(self):
        if self.__failure is not None:
            failure = self.__failure
            self.__failure = None
            raise_exc_info(failure)
