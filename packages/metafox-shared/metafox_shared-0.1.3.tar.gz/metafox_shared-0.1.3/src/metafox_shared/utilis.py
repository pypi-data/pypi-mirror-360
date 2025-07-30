import datetime

def get_current_date() -> str:
    """
    Get the current date and time in ISO 8601 format with " UTC" appended.

    Returns:
        str: The current date and time in ISO 8601 format with " UTC" appended.
    """
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None).isoformat() + " UTC"