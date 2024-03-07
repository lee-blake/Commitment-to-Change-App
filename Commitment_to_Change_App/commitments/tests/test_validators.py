import datetime

import pytest

from django.core.exceptions import ValidationError

from commitments.validators import date_is_not_in_past, date_is_in_future


class TestDateIsNotInPast:
    """Tests for data_is_not_in_past"""

    def test_non_date_raises_validation_error(self):
        with pytest.raises(ValidationError):
            date_is_not_in_past("")

    def test_past_date_raises_validation_error(self):
        past_date = datetime.date.fromisoformat("2000-01-01")
        with pytest.raises(ValidationError):
            date_is_not_in_past(past_date)

    def test_current_day_does_not_raise_validation_error(self):
        date_is_not_in_past(datetime.date.today())

    def test_future_date_does_not_raise_validation_error(self):
        one_year_from_now = datetime.date.today() + datetime.timedelta(days=365)
        date_is_not_in_past(one_year_from_now)


class TestDateIsInFuture:
    """Tests for data_is_in_future"""

    def test_non_date_raises_validation_error(self):
        with pytest.raises(ValidationError):
            date_is_in_future("")

    def test_past_date_raises_validation_error(self):
        past_date = datetime.date.fromisoformat("2000-01-01")
        with pytest.raises(ValidationError):
            date_is_in_future(past_date)

    def test_current_day_does_raise_validation_error(self):
        with pytest.raises(ValidationError):
            date_is_in_future(datetime.date.today())

    def test_future_date_does_not_raise_validation_error(self):
        one_year_from_now = datetime.date.today() + datetime.timedelta(days=365)
        date_is_in_future(one_year_from_now)
