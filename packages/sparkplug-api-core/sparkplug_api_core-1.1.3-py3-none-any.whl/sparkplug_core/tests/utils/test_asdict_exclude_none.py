from dataclasses import dataclass

from django.test import TestCase

from sparkplug_core.utils import asdict_exclude_none


@dataclass
class SampleData:
    field1: str
    field2: int
    field3: None = None


class TestAsdictExcludeNone(TestCase):
    def test_excludes_none_values(self):
        obj = SampleData(field1="value1", field2=42, field3=None)
        result = asdict_exclude_none(obj)

        assert result == {"field1": "value1", "field2": 42}

    def test_includes_all_non_none_values(self):
        obj = SampleData(field1="value1", field2=42, field3="value3")
        result = asdict_exclude_none(obj)

        assert result == {"field1": "value1", "field2": 42, "field3": "value3"}

    def test_empty_dataclass(self):
        @dataclass
        class EmptyData:
            pass

        obj = EmptyData()
        result = asdict_exclude_none(obj)

        assert result == {}
