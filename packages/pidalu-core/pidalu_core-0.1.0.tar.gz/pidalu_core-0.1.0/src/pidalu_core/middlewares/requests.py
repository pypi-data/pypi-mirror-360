import threading

_request_local = threading.local()


def get_current_request():
    return getattr(_request_local, "request", None)


def get_current_user():
    request = get_current_request()
    if request and hasattr(request, "user") and request.user.is_authenticated:
        return request.user
    return None


class RequestMiddleware:
    """
    Store the current request in thread-local storage.
    Add this middleware high in the MIDDLEWARE list in settings.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_local.request = request
        response = self.get_response(request)
        return response
