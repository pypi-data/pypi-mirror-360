import zoneinfo

from django.http import HttpRequest, HttpResponse
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response: HttpResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpResponse) -> HttpRequest:
        if request.user.is_authenticated:
            zone = zoneinfo.ZoneInfo(request.user.timezone)
            timezone.activate(zone)
        else:
            timezone.deactivate()
        return self.get_response(request)
