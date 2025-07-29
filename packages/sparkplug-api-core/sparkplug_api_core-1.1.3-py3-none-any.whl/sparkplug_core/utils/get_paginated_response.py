from django.conf import settings
from django.db.models import QuerySet
from django.utils.module_loading import import_string
from django.views.generic import View
from rest_framework import status
from rest_framework.pagination import BasePagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

DEFAULT_PAGINATION_CLASS = import_string(
    settings.REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"],
)


def get_paginated_response(
    *,
    serializer_class: Serializer,
    queryset: QuerySet,
    request: Request,
    view: View,
    pagination_class: BasePagination = DEFAULT_PAGINATION_CLASS,
) -> Response:
    """Return a paginated response for a given queryset."""
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(
        data=serializer.data,
        status=status.HTTP_200_OK,
    )
