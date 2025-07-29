from dataclasses import dataclass, field
from typing import ClassVar

from rest_framework_dataclasses.serializers import DataclassSerializer

from sparkplug_core.utils import get_pagination_start_end


@dataclass
class SearchTermData:
    page: int
    term: str | None = ""
    start: int = field(init=False, default=None)
    end: int = field(init=False, default=None)

    def __post_init__(self) -> None:
        # Validate and set the page
        try:
            self.page = int(self.page)
        except ValueError:
            self.page = 1

        # Set start and end based on the page
        self.start, self.end = get_pagination_start_end(self.page)


class SearchTermSerializer(DataclassSerializer):
    class Meta:
        dataclass: type = SearchTermData
        extra_kwargs: ClassVar[dict] = {
            "term": {"allow_blank": True},
        }
