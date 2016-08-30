from django.core.exceptions import MiddlewareNotUsed

from data_request.models import AuthenticationContent, DataRequest


class StartupMiddleware(object):
    """
    Initiated only once during first request.
    Here we can perform startup tasks that require access to database.
    """
    def __init__(self):
        # Removing all user data
        AuthenticationContent.objects.all().delete()
        DataRequest.objects.all().delete()

        raise MiddlewareNotUsed('Startup complete')
