import functools

from tornado.web import urlparse, urlencode, HTTPError


def permission_required(f):
    """
    Returns a decoration that check the current user with given function.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If the user does not have the permission, they will receive 403 page.
    """
    @functools.wraps(f)
    def check_permission(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            user = self.current_user
            if not user:
                if self.request.method in ("GET", "HEAD"):
                    url = self.get_login_url()
                    if "?" not in url:
                        if urlparse.urlsplit(url).scheme:
                            # if login url is absolute, make next absolute too
                            next_url = self.request.full_url()
                        else:
                            next_url = self.request.uri
                        url += "?" + urlencode(dict(next=next_url))
                    self.redirect(url)
                    return
            elif f(user):
                return method(self, *args, **kwargs)
            raise HTTPError(403)

        return wrapper
    return check_permission


login_required = permission_required(lambda x: True)
