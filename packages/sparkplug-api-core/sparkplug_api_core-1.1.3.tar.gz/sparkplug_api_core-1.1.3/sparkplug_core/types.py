from typing_extensions import (
    NotRequired,
    TypedDict,
)


class Route(TypedDict):
    name: str
    params: NotRequired[dict[str, str]]
    query: NotRequired[dict[str, str]]
