from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(
    PageNumberPagination,
):
    page_size = 25
    page_size_query_param = "page_size"

    def get_paginated_response(self, data: dict) -> Response:
        # Add `total_pages` to the paginated response.
        response = super().get_paginated_response(data)
        response.data["total_pages"] = self.page.paginator.num_pages
        return response
