from dataclasses import dataclass

from rest_framework.exceptions import APIException
from rest_framework_dataclasses.serializers import DataclassSerializer


def get_validated_dataclass(
    serializer_class: type[DataclassSerializer],
    *,
    data: dict,
) -> dataclass:
    """Validate serializer data and return a dataclass."""
    if not issubclass(serializer_class, DataclassSerializer):
        msg = "serializer_class must be a subclass of DataclassSerializer"
        raise APIException(msg)

    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)

    # Return the validated dataclass instance directly
    return serializer.validated_data
