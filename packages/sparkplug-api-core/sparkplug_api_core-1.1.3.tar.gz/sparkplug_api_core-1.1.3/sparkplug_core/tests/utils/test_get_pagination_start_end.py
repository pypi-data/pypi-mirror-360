from django.test import TestCase

from sparkplug_core.pagination import DefaultPagination

from ...utils.get_pagination_start_end import get_pagination_start_end


class GetPaginationStartEndTest(TestCase):
    def setUp(self):
        # Set a known page size for testing
        self.original_page_size = DefaultPagination.page_size
        DefaultPagination.page_size = 10

    def tearDown(self):
        # Restore the original page size after tests
        DefaultPagination.page_size = self.original_page_size

    def test_get_pagination_start_end_first_page(self):
        start, end = get_pagination_start_end(1)
        assert start == 0
        assert end == 9

    def test_get_pagination_start_end_second_page(self):
        start, end = get_pagination_start_end(2)
        assert start == 10
        assert end == 19

    def test_get_pagination_start_end_third_page(self):
        start, end = get_pagination_start_end(3)
        assert start == 20
        assert end == 29
