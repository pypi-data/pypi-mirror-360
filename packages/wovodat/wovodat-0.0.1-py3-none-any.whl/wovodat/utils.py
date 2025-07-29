from datetime import datetime

def to_datetime(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"❌ Invalid date format: {date_str}. It should be YYYY-MM-DD")
