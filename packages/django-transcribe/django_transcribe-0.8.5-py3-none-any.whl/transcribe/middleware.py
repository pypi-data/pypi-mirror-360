import logging

from django.http import JsonResponse
from django.utils import timezone

logger = logging.getLogger(__name__)


class PingViewMiddleware:
    PING_PATH = '/status/ping'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.strip('/') == self.PING_PATH.strip('/'):
            return JsonResponse({'datetime': timezone.now()})
        else:
            return self.get_response(request)
