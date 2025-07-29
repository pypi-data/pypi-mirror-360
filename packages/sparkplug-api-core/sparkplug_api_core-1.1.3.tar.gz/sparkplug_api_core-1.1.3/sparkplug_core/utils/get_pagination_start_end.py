from sparkplug_core.pagination import DefaultPagination


def get_pagination_start_end(page: int) -> tuple[int, int]:
    """
    Return the start and end indices for pagination based on the given page.
    """
    start = (page - 1) * DefaultPagination.page_size
    end = start + DefaultPagination.page_size - 1
    return (start, end)
