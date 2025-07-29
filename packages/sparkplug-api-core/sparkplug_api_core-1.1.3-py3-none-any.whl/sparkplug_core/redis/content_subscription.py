from sparkplug_core.utils import (
    build_cache_key,
    redis_db,
)


class ContentSubscription:
    @staticmethod
    def build_user_key(*, user_uuid: str) -> str:
        return build_cache_key(
            [
                user_uuid,
                "content-subscriptions",
            ]
        )

    @staticmethod
    def subscribe(
        *,
        subscriber_uuid: str,
        object_type: str,
        subscription_type: str,
        object_id: str | None = None,
    ) -> None:
        key = build_cache_key(
            [
                object_type,
                subscription_type,
                object_id,
            ]
        )

        subscription_set = redis_db.Set(key)
        subscription_set.add(subscriber_uuid)

        user_key = ContentSubscription.build_user_key(
            user_uuid=subscriber_uuid,
        )

        user_subscriptions = redis_db.Set(user_key)
        user_subscriptions.add(key)

    @staticmethod
    def unsubscribe(
        *,
        subscriber_uuid: str,
        key: str,
    ) -> None:
        subscription_set = redis_db.Set(key)
        subscription_set.remove(subscriber_uuid)

        user_key = ContentSubscription.build_user_key(
            user_uuid=subscriber_uuid,
        )

        user_subscriptions = redis_db.Set(user_key)
        user_subscriptions.remove(key)

    @staticmethod
    def get_members_by_key(
        *,
        key: str,
        exclude_uuid: str | None = None,
    ) -> list[str]:
        subscription_set = redis_db.Set(key)

        return [
            i.decode()
            for i in subscription_set.members()
            if exclude_uuid != i.decode()
        ]

    @staticmethod
    def get_members(
        *,
        object_type: str,
        subscription_type: str,
        object_id: str | None = None,
        exclude_uuid: str | None = None,
    ) -> list[str]:
        key = build_cache_key(
            [
                object_type,
                subscription_type,
                object_id,
            ]
        )

        return ContentSubscription.get_members_by_key(
            key=key,
            exclude_uuid=exclude_uuid,
        )

    @staticmethod
    def get_user_subscriptions(*, user_uuid: str) -> list[str]:
        user_key = ContentSubscription.build_user_key(
            user_uuid=user_uuid,
        )

        user_subscriptions = redis_db.Set(user_key)

        return [i.decode() for i in user_subscriptions.members()]

    @staticmethod
    def remove_user_subscriptions(*, user_uuid: str) -> None:
        subscriptions = ContentSubscription.get_user_subscriptions(
            user_uuid=user_uuid,
        )

        for key in subscriptions:
            ContentSubscription.unsubscribe(
                subscriber_uuid=user_uuid,
                key=key,
            )

        user_key = ContentSubscription.build_user_key(
            user_uuid=user_uuid,
        )

        user_subscriptions = redis_db.Set(user_key)
        del user_subscriptions
