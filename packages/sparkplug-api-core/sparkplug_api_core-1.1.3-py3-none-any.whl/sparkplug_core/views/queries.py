import logging

from decouple import config
from rest_framework.response import Response

log = logging.getLogger(__name__)


class LogQueryCount:
    def dispatch(self, *args, **kwargs) -> Response:
        response = super().dispatch(*args, **kwargs)

        log_level = config("API_LOG_LEVEL", default="INFO")

        if log_level != "DEBUG":
            return response

        # For debugging purposes only.
        from django.db import connection

        query_count = len(connection.queries)

        msg = f"{self.__class__.__name__}: {query_count}"

        log.debug(msg)

        return response


class LogQueries:
    def dispatch(self, *args, **kwargs) -> Response:
        response = super().dispatch(*args, **kwargs)

        log_level = config("API_LOG_LEVEL", default="INFO")

        if log_level != "DEBUG":
            return response

        # For debugging purposes only.
        from django.db import connection

        query_count = len(connection.queries)

        msg = f"{self.__class__.__name__}: {query_count}"

        log.debug(msg)

        for query in connection.queries:
            msg = query["sql"]
            log.debug(msg)

        return response
