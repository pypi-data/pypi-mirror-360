from django_extensions.db.fields import ShortUUIDField
from django_extensions.db.models import TimeStampedModel


class BaseModel(
    TimeStampedModel,
):
    uuid = ShortUUIDField()

    class Meta:
        get_latest_by = "created"
        abstract = True

    @property
    def is_new(self) -> bool:
        # Check if creating a new instance
        # https://stackoverflow.com/a/35647389/2407209
        # https://docs.djangoproject.com/en/3.0/ref/models/instances/#state
        return self._state.adding
