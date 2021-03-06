import re
import warnings

from django import http
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class CanonicalHostMiddleware(MiddlewareMixin):
    """ Redirects to a canonical host if the current host is not the canonical
    host. """

    response_redirect_class = http.HttpResponsePermanentRedirect

    def process_request(self, request):

        canonical_host = getattr(settings, "CANONICAL_HOST", None)

        if not canonical_host:
            return

        host = request.get_host()

        if host == canonical_host:
            return

        path = request.get_full_path()
        redirect_url = ('%s://%s%s' % (request.scheme, canonical_host, path))
        return self.response_redirect_class(redirect_url)


class UnprependWWWMiddleware(MiddlewareMixin):
    """ Unprepends www if necessary. """

    response_redirect_class = http.HttpResponsePermanentRedirect

    def process_request(self, request):
        """
        Rewrite the URL based on settings.UNPREPEND_WWW
        """

        unprepend_www = getattr(settings, "UNPREPEND_WWW", False)

        if not unprepend_www:
            return

        # Check for a redirect based on settings.UNPREPEND_WWW
        host = request.get_host()
        must_unprepend = unprepend_www and host and host.lower().startswith('www.')
        wwwless_host = host[4:]
        redirect_url = ('%s://%s' % (request.scheme, wwwless_host)) if must_unprepend else ''

        path = request.get_full_path()

        # Return a redirect if necessary
        if redirect_url or path != request.get_full_path():
            redirect_url += path
            return self.response_redirect_class(redirect_url)
