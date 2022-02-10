from datetime import datetime, timezone

def display_timestamp(timestamp: int) -> datetime:
    """Return python datetime from utc timestamp"""
    return datetime.fromtimestamp(timestamp, timezone.utc)


def utc_timestamp() -> int:
    """Return current utc timestamp rounded to nearest int"""
    return int(datetime.utcnow().timestamp())

