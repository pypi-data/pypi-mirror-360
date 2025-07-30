def format_bytes(size: int) -> str:
    """
    Converts a size in bytes to a human-readable format

    Parameters:
        size (``int``):
            The size in bytes

    Returns:
        ``str``:
            The formatted size with the appropriate suffix

    """

    suffixes = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size >= 1024 and i < len(suffixes) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {suffixes[i]}"


def parse_bytes(size_str: str) -> str:
    """
    Converts a size in a human-readable format to bytes

    Parameters:
        size_str (``str``):
            The size in a human-readable format, e.g., ``2.00 KB``

    Returns:
        ``int``:
            The size in bytes

    Raises:
        ``ValueError``:
            If the input ``size_str`` is in an invalid format

    """

    suffixes = ["B", "KB", "MB", "GB", "TB"]
    size_str = size_str.strip()
    size, suffix = size_str[:-2], size_str[-2:].upper()

    if suffix not in suffixes:
        raise ValueError("Invalid size format")

    try:
        size = float(size)
    except ValueError:
        raise ValueError("Invalid size format")

    power = suffixes.index(suffix)
    size *= 1024**power
    return int(size)


units = [
    ("year", 365 * 24 * 60 * 60),
    ("day", 24 * 60 * 60),
    ("hour", 60 * 60),
    ("minute", 60),
    ("second", 1),
]


def format_duration(seconds: int, format_option: str = "short") -> str:
    """
    Formats the given duration in seconds into a human-readable string representation

    Parameters:
        seconds (``int``):
            The duration in seconds

        format_option (``str``, *optional*):
            The formatting option either ``long`` or ``short``. Default is "short"

    Returns:
        ``str``:
            The formatted duration string

    Raises:
        ``ValueError``:
            If the duration is a negative number
    """

    if seconds < 0:
        raise ValueError("Duration must be a non-negative number")

    parts = []
    for unit, duration in units:
        if seconds >= duration:
            count = seconds // duration
            seconds %= duration

            if count > 1:
                unit += "s"

            parts.append(f"{count} {unit}")

    if not parts:
        return "0 seconds"

    if format_option == "long":
        if len(parts) == 1:
            return parts[0]
        last_part = parts.pop()
        return ", ".join(parts) + " and " + last_part
    elif format_option == "short":
        hours = int(seconds // 3600)
        minutes = int((seconds // 60) % 60)
        seconds = int(seconds % 60)

        time_parts = []
        if hours > 0:
            time_parts.append(str(hours))
        time_parts.append(f"{minutes:02d}")
        time_parts.append(f"{seconds:02d}")
        return ":".join(time_parts)
    else:
        raise ValueError("Invalid format option. Available options: 'long', 'short'")


def format_number_short(number: int) -> str:
    """
    Convert a number to a short format with a specified number of decimal places

    Parameters:
        number (``float``):
            The number to format

    Returns:
        ``str``:
            The formatted number in short format
    """

    suffixes = {0: "", 3: "K", 6: "M", 9: "B", 12: "T", 15: "Q"}

    order = 0
    while number >= 10**3 and order < max(suffixes.keys()):
        order += 3
        number /= 10**3

    if number.is_integer():
        formatted_number = f"{int(number)}"
    else:
        formatted_number = f"{number:.1f}".rstrip("0").rstrip(".")

    formatted_number += suffixes.get(order, "")

    return formatted_number


def convert_to_bytes(value: int, unit: str) -> int:
    """
    Convert a number with a unit prefix into bytes

    Parameters:
        value (``int``):
            The numerical value

        unit (``str``):
            The unit prefix (e.g., "B", "KB", "MB", "GB", "TB", "PB")

    Returns:
        ``int``:
            The value converted to bytes
    """

    unit = unit.upper()
    if unit == "B":
        return value
    elif unit == "KB":
        return int(value * 1024)
    elif unit == "MB":
        return int(value * 1024 * 1024)
    elif unit == "GB":
        return int(value * 1024 * 1024 * 1024)
    elif unit == "TB":
        return int(value * 1024 * 1024 * 1024 * 1024)
    elif unit == "PB":
        return int(value * 1024 * 1024 * 1024 * 1024 * 1024)
    else:
        raise ValueError("Invalid unit. Use 'B', 'KB', 'MB', 'GB', 'TB', or 'PB'.")


def to_numeric(value: int, unit: str) -> int:
    """
    Convert a number with a unit prefix into its numerical value

    Parameters:
        value (``int``):
            The numerical value

        unit (``str``):
            The unit prefix (e.g., "U" for "UNIT", "T" for "TEN", "H" for "HUNDRED", "K" for "THOUSAND",
                    "M" for "MILLION", "B" for "BILLION", "T" for "TRILLION")

    Returns:
        ``float``:
            The value converted to its numerical value
    """

    unit = unit.upper()
    if unit == "U":
        return value
    elif unit == "T":
        return value * 10
    elif unit == "H":
        return value * 100
    elif unit == "K":
        return value * 1000
    elif unit == "M":
        return value * 1000000
    elif unit == "B":
        return value * 1000000000
    elif unit == "T":
        return value * 1000000000000
    else:
        raise ValueError(
            "Invalid unit. Use 'U' for 'UNIT', 'T' for 'TEN', 'H' for 'HUNDRED', 'K' for 'THOUSAND', "
            "'M' for 'MILLION', 'B' for 'BILLION', or 'T' for 'TRILLION'."
        )
