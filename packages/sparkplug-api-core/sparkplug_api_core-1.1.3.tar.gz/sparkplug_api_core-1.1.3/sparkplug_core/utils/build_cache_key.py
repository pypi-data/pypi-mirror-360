def build_cache_key(
    parts: list[str | None],
) -> str:
    return ":".join(
        # Convert all entries to strings
        map(
            str,
            # Filter out empty values
            filter(None, parts),
        ),
    )
