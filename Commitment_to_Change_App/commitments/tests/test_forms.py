import datetime

import pytest

from cme_accounts.models import User

from commitments.enums import CommitmentStatus
from commitments.forms import CommitmentForm, CourseForm, CompleteCommitmentForm,\
     DiscontinueCommitmentForm, ReopenCommitmentForm, CreateCommitmentFromSuggestedCommitmentForm
from commitments.models import ClinicianProfile, Commitment, CommitmentTemplate, Course


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

@pytest.fixture(name="saved_in_progress_commitment")
def fixture_saved_in_progress_commitment(unsaved_in_progress_commitment):
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
        def test_save_with_commit_saves_complete(self, saved_in_progress_commitment):
            form = CompleteCommitmentForm(
                {"complete": "present"}, instance=saved_in_progress_commitment
            )
            form.save(commit=True)
            reloaded_commitment = Commitment.objects.get(id=saved_in_progress_commitment.id)
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
        def test_save_with_commit_saves_discontinued(self, saved_in_progress_commitment):
            form = DiscontinueCommitmentForm(
                {"discontinue": "present"}, instance=saved_in_progress_commitment
            )
            form.save(commit=True)
            reloaded_commitment = Commitment.objects.get(id=saved_in_progress_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.DISCONTINUED


class TestReopenCommitmentForm:
    """Tests for ReopenCommitmentForm"""

    @pytest.fixture(name="unsaved_complete_commitment")
    def fixture_unsaved_complete_commitment(self, unsaved_in_progress_commitment):
        unsaved_in_progress_commitment.status = CommitmentStatus.COMPLETE
        return unsaved_in_progress_commitment

    @pytest.fixture(name="saved_complete_commitment")
    def fixture_saved_complete_commitment(self, saved_in_progress_commitment):
        saved_in_progress_commitment.status = CommitmentStatus.COMPLETE
        saved_in_progress_commitment.save()
        return saved_in_progress_commitment

    @pytest.fixture(name="unsaved_discontinued_commitment")
    def fixture_unsaved_discontinued_commitment(self, unsaved_in_progress_commitment):
        unsaved_in_progress_commitment.status = CommitmentStatus.DISCONTINUED
        unsaved_in_progress_commitment.deadline = datetime.date.fromisoformat("2000-01-01")
        return unsaved_in_progress_commitment

    @pytest.fixture(name="saved_discontinued_commitment")
    def fixture_saved_discontinued_commitment(self, saved_in_progress_commitment):
        saved_in_progress_commitment.status = CommitmentStatus.DISCONTINUED
        saved_in_progress_commitment.deadline = datetime.date.fromisoformat("2000-01-01")
        saved_in_progress_commitment.save()
        return saved_in_progress_commitment

    class TestIsValid:
        """Tests for ReopenCommitmentForm.is_valid"""

        def test_no_reopen_key_is_not_valid(self, unsaved_complete_commitment):
            form = ReopenCommitmentForm({}, instance=unsaved_complete_commitment)
            assert not form.is_valid()

        def test_reopen_key_present_at_all_is_valid(self, unsaved_complete_commitment):
            form = ReopenCommitmentForm(
                {"reopen": "present"}, instance=unsaved_complete_commitment
            )
            assert form.is_valid()


    class TestSave:
        """Tests for ReopenCommitmentForm.save"""

        def test_save_without_commit_reopens_non_expired_complete(
            self, unsaved_complete_commitment
        ):
            form = ReopenCommitmentForm(
                {"reopen": "present"}, instance=unsaved_complete_commitment
            )
            form.save(commit=False)
            assert unsaved_complete_commitment.status == CommitmentStatus.IN_PROGRESS

        @pytest.mark.django_db
        def test_save_with_commit_saves_reopened_non_expired_complete(
            self, saved_complete_commitment
        ):
            form = ReopenCommitmentForm(
                {"reopen": "present"}, instance=saved_complete_commitment
            )
            form.save(commit=True)
            reloaded_commitment = Commitment.objects.get(id=saved_complete_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.IN_PROGRESS

        def test_save_without_commit_reopens_expired_discontinued(
            self, unsaved_discontinued_commitment
        ):
            form = ReopenCommitmentForm(
                {"reopen": "present"}, instance=unsaved_discontinued_commitment
            )
            form.save(commit=False)
            assert unsaved_discontinued_commitment.status == CommitmentStatus.EXPIRED

        @pytest.mark.django_db
        def test_save_with_commit_saves_reopened_expired_discontinued(
            self, saved_discontinued_commitment
        ):
            form = ReopenCommitmentForm(
                {"reopen": "present"}, instance=saved_discontinued_commitment
            )
            form.save(commit=True)
            reloaded_commitment = Commitment.objects.get(id=saved_discontinued_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.EXPIRED


class TestCreateCommitmentFromSuggestedCommitmentForm:
    """Tests for CreateCommitmentFromSuggestedCommitmentForm"""

    class TestInit:
        """Tests for CreateCommitmentFromSuggestedCommitmentForm.__init__"""

        @pytest.fixture(name="commitment_owner")
        def fixture_commitment_owner(self):
            return ClinicianProfile(id=1)

        @pytest.fixture(name="source_template", params=[
            ("First title", "First description"),
            ("Second title", "Second description")
        ])
        def fixture_source_template(self, request):
            return CommitmentTemplate(
                title=request.param[0],
                description=request.param[1]
            )

        @pytest.fixture(name="source_course", params=[1, 2])
        def fixture_source_course(self, request):
            return Course(
                id=request.param
            )


        def test_passing_existing_commitment_raises_type_error(
            self, unsaved_in_progress_commitment, commitment_owner
        ):
            source_template = CommitmentTemplate()
            source_course = Course()
            with pytest.raises(TypeError):
                CreateCommitmentFromSuggestedCommitmentForm(
                    source_template,
                    source_course,
                    instance=unsaved_in_progress_commitment,
                    owner=commitment_owner
                )

        def test_associated_course_is_set_automatically(self, source_course, commitment_owner):
            form = CreateCommitmentFromSuggestedCommitmentForm(
                CommitmentTemplate(),
                source_course,
                owner=commitment_owner
            )
            assert form.instance.associated_course == source_course

        def test_title_is_set_automatically(self, source_template, commitment_owner):
            form = CreateCommitmentFromSuggestedCommitmentForm(
                source_template,
                Course(),
                owner=commitment_owner
            )
            assert form.instance.title == source_template.title
