from enum import Enum

from django.contrib.auth import get_user_model
from djangorestframework_camel_case.util import camelize

from .socket_send import socket_send


def send_admin_action(
    *,
    action_type: Enum,
    payload: dict | None = None,
) -> None:
    target_uuids = (
        get_user_model()
        .objects.filter(is_staff=True)
        .filter(is_active=True)
        .values_list("uuid", flat=True)
    )

    context = {
        "type": action_type,
        "payload": camelize(payload),
    }

    for uuid in target_uuids:
        socket_send(uuid, context)
