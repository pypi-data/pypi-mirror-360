from dataclasses import asdict, dataclass


def asdict_exclude_none(obj: dataclass) -> dict:
    return {
        key: value for key, value in asdict(obj).items() if value is not None
    }
