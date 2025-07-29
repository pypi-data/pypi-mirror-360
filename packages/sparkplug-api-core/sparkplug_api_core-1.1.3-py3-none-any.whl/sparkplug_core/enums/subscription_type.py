from enum import Enum


class SubscriptionType(str, Enum):
    # Subscribe to updates
    BROWSE = "BROWSE"

    # Subscribe to updates for a particular item, or its descendants
    ITEM = "ITEM"

    def __str__(self) -> str:
        return self.name
