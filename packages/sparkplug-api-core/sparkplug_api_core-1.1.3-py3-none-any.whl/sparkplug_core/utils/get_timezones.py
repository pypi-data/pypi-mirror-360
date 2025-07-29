import zoneinfo
from functools import cache


@cache
def get_timezones() -> list[str]:
    zones = [
        zone
        for zone in zoneinfo.available_timezones()
        if (("/" in zone or zone == "UTC") and not zone.startswith("Etc/"))
    ]
    return sorted(zones)


TIMEZONE_CHOICES = [(item, item) for item in get_timezones()]
