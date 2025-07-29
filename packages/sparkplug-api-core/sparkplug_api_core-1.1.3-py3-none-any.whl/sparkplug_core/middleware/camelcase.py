from django.http import HttpRequest, HttpResponse
from djangorestframework_camel_case.settings import api_settings
from djangorestframework_camel_case.util import underscoreize


# https://github.com/vbabiy/djangorestframework-camel-case/pull/68/files
class CamelCaseQueryParamsMiddleware:
    def __init__(self, get_response: HttpResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Underscoreize query params
        request.GET = underscoreize(
            request.GET,
            **api_settings.JSON_UNDERSCOREIZE,
        )

        return self.get_response(request)
