from datetime import datetime, timezone

def convert_to_rfc3339(date_str=None):
    """
    Converts a date string (YYYY-MM-DD) to RFC 3339 format.
    If no date is provided, returns the current UTC timestamp in RFC 3339 format.

    Args:
        date_str (str, optional): Date string in 'YYYY-MM-DD' format. Defaults to None.

    Returns:
        str: RFC 3339 formatted datetime (ISO 8601 with UTC time) or empty string if invalid.
    """
    if date_str is None:  # If no date is provided, return the current time
        dt = datetime.now(timezone.utc).replace(microsecond=0)  # Ensure no microseconds
        return dt.isoformat(timespec='seconds').replace("+00:00", "Z")

    if not date_str:  # Handle empty or None values
        return ""

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")  # Convert string to datetime
        dt = dt.replace(tzinfo=timezone.utc, microsecond=0)  # Set UTC timezone & remove microseconds
        return dt.isoformat(timespec='seconds').replace("+00:00", "Z")  # Return RFC 3339 format
    except ValueError:
        return date_str  # Return original value if parsing fails


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def year_month():
    return datetime.now().strftime('%Y-%m')
