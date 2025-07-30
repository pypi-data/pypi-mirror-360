from datetime import datetime
from typing import Optional

import pendulum


def format_dt(date: Optional[datetime] = None) -> str:
    if date is None:
        return ""
    return pendulum.instance(date).to_day_datetime_string()


def format_date(date: Optional[datetime] = None) -> str:
    if date is None:
        return ""
    return pendulum.instance(date).to_date_string()


def truncate(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[:length] + "..."
