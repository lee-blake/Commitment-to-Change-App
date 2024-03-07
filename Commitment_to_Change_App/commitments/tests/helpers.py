"""Helper functions for testing"""

import re
from smtplib import SMTPException


def convert_date_to_general_regex(date):
    year = date.year
    month = date.month
    month_text = date.strftime("%B")
    short_month_text = date.strftime("%b")
    day = date.day
    re_iso_format = str(date)
    re_year_first_slashes = f"{year}\\/0?{month}\\/0?{day}"
    re_month_first_slashes = f"0?{month}\\/0?{day}\\/{year}"
    re_month_text_first = f"{month_text}\\s+0?{day},?\\s+{year}"
    re_short_month_text_first = f"{short_month_text}\\.?\\s+0?{day},?\\s+{year}"
    return re.compile(
        f"({re_month_first_slashes}|{re_iso_format}|{re_month_text_first}|" +
        f"{re_short_month_text_first}|{re_year_first_slashes})"
    )


class FailBackend:
    """Mock email backend for testing behavior when email sending fails with an exception"""
    
    def __init__(self, *args, **kwargs):
        pass

    def send_messages(self, messages):
        raise SMTPException()
