import re
from datetime import datetime

def to_datetime(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"❌ Invalid date format: {date_str}. It should be YYYY-MM-DD")

def slugify(string: str, separator: str = "-") -> str:
    """Slugify a string.

    Args:
        string (str): String to slugify.
        separator (str): Separator between words. Defaults to "-".

    Returns:
        str: Slugified string.
    """
    slug = string.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", separator, slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug
