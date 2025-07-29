from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def socket_send(
    group_name: str,
    context: dict,
) -> None:
    channel_layer = get_channel_layer()

    payload = {
        "type": "send_event",
        "context": context,
    }

    async_to_sync(channel_layer.group_send)(
        group_name,
        payload,
    )
