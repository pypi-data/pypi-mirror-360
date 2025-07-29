from dataclasses import dataclass

import pytest
from django.test import TestCase
from rest_framework.exceptions import APIException, ValidationError
from rest_framework_dataclasses.serializers import DataclassSerializer

from sparkplug_core.utils import get_validated_dataclass


@dataclass
class ExampleDataclass:
    field1: str
    field2: int


class ExampleDataclassSerializer(DataclassSerializer):
    class Meta:
        dataclass = ExampleDataclass


class GetValidatedDataclassTests(TestCase):
    def test_valid_data(self):
        data = {"field1": "test", "field2": 123}
        result = get_validated_dataclass(
            serializer_class=ExampleDataclassSerializer,
            data=data,
        )
        assert isinstance(result, ExampleDataclass)
        assert result.field1 == "test"
        assert result.field2 == 123

    def test_invalid_data(self):
        data = {"field1": "test", "field2": "invalid_int"}
        with pytest.raises(ValidationError) as exc_info:
            get_validated_dataclass(
                serializer_class=ExampleDataclassSerializer,
                data=data,
            )
        assert "field2" in exc_info.value.detail
        assert exc_info.value.detail["field2"][0].code == "invalid"

    def test_serializer_class_not_subclass(self):
        class NotASerializer:
            pass

        data = {"field1": "test", "field2": 123}
        with pytest.raises(APIException) as exc_info:
            get_validated_dataclass(
                serializer_class=NotASerializer,
                data=data,
            )
        assert (
            "serializer_class must be a subclass of DataclassSerializer"
            in str(exc_info.value)
        )

    def test_missing_required_field(self):
        data = {"field1": "test"}
        with pytest.raises(ValidationError) as exc_info:
            get_validated_dataclass(
                serializer_class=ExampleDataclassSerializer,
                data=data,
            )
        assert "field2" in exc_info.value.detail
        assert exc_info.value.detail["field2"][0].code == "required"

    def test_extra_field_ignored(self):
        data = {"field1": "test", "field2": 123, "extra": "ignored"}
        result = get_validated_dataclass(
            serializer_class=ExampleDataclassSerializer,
            data=data,
        )
        assert isinstance(result, ExampleDataclass)
        assert result.field1 == "test"
        assert result.field2 == 123
        assert not hasattr(result, "extra")
