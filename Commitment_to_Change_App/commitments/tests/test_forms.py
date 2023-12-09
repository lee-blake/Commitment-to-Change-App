import datetime

import pytest

from cme_accounts.models import User

from commitments.enums import CommitmentStatus
from commitments.forms import CommitmentForm, CourseForm, CompleteCommitmentForm,\
     DiscontinueCommitmentForm
from commitments.models import ClinicianProfile, Commitment


@pytest.fixture(name="unsaved_in_progress_commitment")
def fixture_unsaved_in_progress_commitment():
    return Commitment(
        title="test title",
        description="test description",
        deadline=datetime.date.today(),
        status=CommitmentStatus.IN_PROGRESS,
        owner=ClinicianProfile(
            user=User(
                username="username",
                email="fake@email.com",
                password="password"
            )
        )
    )

@pytest.fixture(name="saved_commitment")
def fixture_saved_commitment(unsaved_in_progress_commitment):
    unsaved_in_progress_commitment.owner.user.save()
    unsaved_in_progress_commitment.owner.save()
    unsaved_in_progress_commitment.save()
    return unsaved_in_progress_commitment


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


class TestCompleteCommitmentForm:
    """Tests for CompleteCommitmentForm"""

    class TestIsValid:
        """Tests for CompleteCommitmentForm.is_valid"""

        def test_no_complete_key_is_not_valid(self, unsaved_in_progress_commitment):
            form = CompleteCommitmentForm({}, instance=unsaved_in_progress_commitment)
            assert not form.is_valid()

        def test_complete_key_present_at_all_is_valid(self, unsaved_in_progress_commitment):
            form = CompleteCommitmentForm(
                {"complete": "present"}, instance=unsaved_in_progress_commitment
            )
            assert form.is_valid()


    class TestSave:
        """Tests for CompleteCommitmentForm.save"""

        def test_save_without_commit_marks_complete(self, unsaved_in_progress_commitment):
            form = CompleteCommitmentForm(
                {"complete": "present"}, instance=unsaved_in_progress_commitment
            )
            form.save(commit=False)
            assert unsaved_in_progress_commitment.status == CommitmentStatus.COMPLETE

        @pytest.mark.django_db
        def test_save_with_commit_saves_complete(self, saved_commitment):
            form = CompleteCommitmentForm(
                {"complete": "present"}, instance=saved_commitment
            )
            form.save(commit=True)
            reloaded_commitment = Commitment.objects.get(id=saved_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.COMPLETE


class TestDiscontinueCommitmentForm:
    """Tests for DiscontinueCommitmentForm"""

    class TestIsValid:
        """Tests for DiscontinueCommitmentForm.is_valid"""

        def test_no_discontinue_key_is_not_valid(self, unsaved_in_progress_commitment):
            form = DiscontinueCommitmentForm({}, instance=unsaved_in_progress_commitment)
            assert not form.is_valid()

        def test_discontinue_key_present_at_all_is_valid(self, unsaved_in_progress_commitment):
            form = DiscontinueCommitmentForm(
                {"discontinue": "present"}, instance=unsaved_in_progress_commitment
            )
            assert form.is_valid()


    class TestSave:
        """Tests for DiscontinueCommitmentForm.save"""

        def test_save_without_commit_marks_discontinued(self, unsaved_in_progress_commitment):
            form = DiscontinueCommitmentForm(
                {"discontinue": "present"}, instance=unsaved_in_progress_commitment
            )
            form.save(commit=False)
            assert unsaved_in_progress_commitment.status == CommitmentStatus.DISCONTINUED

        @pytest.mark.django_db
        def test_save_with_commit_saves_discontinued(self, saved_commitment):
            form = DiscontinueCommitmentForm(
                {"discontinue": "present"}, instance=saved_commitment
            )
            form.save(commit=True)
            reloaded_commitment = Commitment.objects.get(id=saved_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.DISCONTINUED
