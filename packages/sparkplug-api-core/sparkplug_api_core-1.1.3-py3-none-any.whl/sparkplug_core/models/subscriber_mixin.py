from sparkplug_core.enums import SubscriptionType
from sparkplug_core.redis import ContentSubscription


class SubscriberMixin:
    def get_browse_subscribers(self) -> list[str]:
        object_id = None
        if hasattr(self, "parent"):
            object_id = self.parent.uuid

        return ContentSubscription.get_members(
            object_type=self.subscription_key,
            subscription_type=SubscriptionType.BROWSE,
            object_id=object_id,
        )

    def get_item_subscribers(self) -> list[str]:
        return ContentSubscription.get_members(
            object_type=self.subscription_key,
            subscription_type=SubscriptionType.ITEM,
            object_id=self.uuid,
        )
