import pytest

from commitments.forms import CommitmentForm, CourseForm
from commitments.models import ClinicianProfile, Commitment


class TestCommitmentForm:
    """Tests for CommitmentForm"""

    class TestInit:
        """Tests for CommitmentForm.__init__"""

        def test_switching_owners_raises_value_error(self):
            original_owner = ClinicianProfile()
            commitment = Commitment(owner=original_owner)
            new_owner = ClinicianProfile()
            with pytest.raises(ValueError):
                CommitmentForm(instance=commitment, owner=new_owner)


class TestCourseForm:
    """Tests for CourseForm"""

    # TODO add more tests for old functionality

    class TestIsValid:
        """Tests for CourseForm.is_valid"""

        def test_empty_unique_identifier_is_valid(self):
            form = CourseForm(
                {
                    "title": "Course Title",
                    "description": "Description",
                    "unique_identifier": ""
                }
            )
            assert form.is_valid()

        def test_empty_course_dates_are_valid(self):
            form = CourseForm(
                {
                    "title": "Course Title",
                    "description": "Description",
                    "start_date": "",
                    "end_date": ""
                }
            )
            assert form.is_valid()

        def test_non_date_start_date_is_not_valid(self):
            form = CourseForm(
                {
                    "title": "Course Title",
                    "description": "Description",
                    "start_date": "not a date"
                }
            )
            assert not form.is_valid()

        def test_non_date_end_date_is_not_valid(self):
            form = CourseForm(
                {
                    "title": "Course Title",
                    "description": "Description",
                    "end_date": "also not a date"
                }
            )
            assert not form.is_valid()

        def test_only_start_date_provided_is_valid(self):
            form = CourseForm(
                {
                    "title": "Course Title",
                    "description": "Description",
                    "start_date": "2000-01-01"
                }
            )
            assert form.is_valid()

        def test_only_end_date_provided_is_valid(self):
            form = CourseForm(
                {
                    "title": "Course Title",
                    "description": "Description",
                    "end_date": "2010-01-01"
                }
            )
            assert form.is_valid()

        def test_end_date_before_start_date_is_invalid(self):
            form = CourseForm(
                {
                    "title": "Course Title",
                    "description": "Description",
                    "start_date": "2000-01-01",
                    "end_date": "1999-12-31"
                }
            )
            assert not form.is_valid()
