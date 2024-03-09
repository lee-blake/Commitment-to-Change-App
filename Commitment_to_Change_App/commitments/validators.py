import datetime

from django.core.exceptions import ValidationError


def date_is_not_in_past(value):
    if (not isinstance(value, datetime.date)) or value < datetime.date.today():
        raise ValidationError(f"{value} is not a non-past date!")

def date_is_in_future(value):
    if (not isinstance(value, datetime.date)) or value <= datetime.date.today():
        raise ValidationError(f"{value} is not a future date!")
