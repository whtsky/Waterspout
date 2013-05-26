from waterspout.app import Waterspout
from waterspout.web import RequestHandler

from waterspout.auth import login_required, permission_required


class LoginHandler(RequestHandler):
    def get(self):
        if not self.session["id"]:
            self.session["id"] = 1
        else:
            self.session["id"] = 2
        self.write(".")


class LoginRequireHandler(RequestHandler):
    @login_required
    def get(self):
        self.write('success')


admin_require = permission_required(lambda x: x == 2)


class AdminRequireHandler(RequestHandler):
    @admin_require
    def get(self):
        self.write('id==2')


handlers = [
    ('/', LoginHandler),
    ('/a', LoginRequireHandler),
    ('/b', AdminRequireHandler)
]

waterspout = Waterspout(__name__, handlers=handlers,
                        cookie_secret="..", login_url="/")


@waterspout.user_loader
def load_user(session):
    return session["id"]


def test_auth():
    client = waterspout.TestClient()
    assert client.get('/a').effective_url.endswith("?next=%2Fa")
    print client.get('/b')
    print client.get('/')
