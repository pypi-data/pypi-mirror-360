from enum import Enum

from djangorestframework_camel_case.util import camelize

from .socket_send import socket_send


def send_client_action(
    *,
    action_type: Enum,
    payload: dict | None = None,
    target_uuid: str | None = None,
    target_uuids: list[str] | None = None,
) -> None:
    if target_uuids is None:
        target_uuids = []

    if target_uuid is not None:
        target_uuids.append(target_uuid)

    context = {
        "type": action_type,
        "payload": camelize(payload),
    }

    for uuid in target_uuids:
        socket_send(uuid, context)
