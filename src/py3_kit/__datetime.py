import arrow


def now(fmt: str = "YYYY-MM-DD HH:mm:ss") -> str:
    return arrow.now().format(fmt)


def delta(start_datetime_str: str, end_datetime_str: str) -> int:
    """
    >>> delta("2026-01-07 08:56:48","2026-01-07 13:00:00")
    14592

    Args:
        start_datetime_str:
        end_datetime_str:

    Returns:

    """
    start_datetime = arrow.get(start_datetime_str).datetime
    end_datetime = arrow.get(end_datetime_str).datetime
    seconds = (end_datetime - start_datetime).total_seconds()
    return int(seconds)
