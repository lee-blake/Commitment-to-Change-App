from datetime import date

import pytest

from cme_accounts.models import User
from commitments.enums import CommitmentStatus
from commitments.models import ClinicianProfile, Commitment, CommitmentTemplate, Course


class TestClinicianProfile:
    """Tests for ClinicianProfile"""

    class TestUsername:
        """Tests for ClinicianProfile.username"""

        @pytest.fixture(name="created_user", params=["One", "Two"])
        def fixture_created_user(self, request):
            return User(
                id=1,
                username=request.param
            )

        def test_shows_username(self, created_user):
            profile = ClinicianProfile(user=created_user)
            assert profile.username == created_user.username

    class TestEmail:
        """Tests for ClinicianProfile.email"""

        @pytest.fixture(name="created_user", params=["test1@localhost", "test2@email"])
        def fixture_created_user(self, request):
            return User(
                id=1,
                email=request.param
            )

        def test_shows_email(self, created_user):
            profile = ClinicianProfile(user=created_user)
            assert profile.email == created_user.email


class TestCommitment:
    """Tests for Commitment"""

    @pytest.fixture(name="commitment_owner")
    def fixture_commitment_owner(self):
        user = User(
            username="testuser",
            password="password",
            email="test@email.me",
            is_clinician=True
        )
        return ClinicianProfile(
            user=user
        )

    @pytest.fixture(name="saved_commitment_owner")
    def fixture_saved_commitment_owner(self):
        user = User.objects.create(
            username="testuser",
            password="password",
            email="test@email.me",
            is_clinician=True
        )
        return ClinicianProfile.objects.create(
            user=user
        )


    @pytest.mark.django_db
    class TestSaveExpiredIfPastDeadline:
        """Tests for Commitment.save_expired_if_past_deadline"""

        def test_saves_expired_if_past_deadline_and_in_progress(self, saved_commitment_owner):
            today = date.today()
            past_deadline = today.replace(year=today.year - 1)
            commitment = Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=past_deadline,
                status=CommitmentStatus.IN_PROGRESS
            )
            commitment.save_expired_if_past_deadline()
            reloaded_commitment = Commitment.objects.get(id=commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.EXPIRED

        def test_no_status_change_if_future_deadline_and_in_progress(self, saved_commitment_owner):
            commitment = Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=CommitmentStatus.IN_PROGRESS
            )
            commitment.save_expired_if_past_deadline()
            reloaded_commitment = Commitment.objects.get(id=commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.IN_PROGRESS

        def test_no_status_change_if_not_in_progress(self, saved_commitment_owner):
            today = date.today()
            past_deadline = today.replace(year=today.year - 1)
            commitment = Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=past_deadline,
                status=CommitmentStatus.COMPLETE
            )
            commitment.save_expired_if_past_deadline()
            reloaded_commitment = Commitment.objects.get(id=commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.COMPLETE

        def test_no_database_touch_if_not_changed(self, saved_commitment_owner):
            today = date.today()
            past_deadline = today.replace(year=today.year - 1)
            commitment = Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=past_deadline,
                status=CommitmentStatus.COMPLETE
            )
            last_modification_before_method_call = commitment.last_updated
            commitment.save_expired_if_past_deadline()
            reloaded_commitment = Commitment.objects.get(id=commitment.id)
            assert reloaded_commitment.last_updated == last_modification_before_method_call


class TestCommitmentTemplate:
    """Tests for CommitmentTemplate"""

    class TestCommitmentTemplateToString:
        """Tests for making sure CommitmentTemplateLogic.__str__ integrates correctly with
        CommitmentTemplate"""

        def test_first_template_returns_correctly(self):
            template = CommitmentTemplate(
                title="test title 1",
                description="irrelevant"
            )
            assert str(template) == "test title 1"

        def test_second_template_returns_correctly(self):
            template = CommitmentTemplate(
                title="not the same",
                description="also irrelevant"
            )
            assert str(template) == "not the same"


class TestCourse:
    """Tests for Course"""

    class TestStr:
        """Tests for making sure CourseLogic.__str__ integrates correctly with Course"""

        @pytest.mark.parametrize("title", ["First title", "Second title"])
        def test_returns_title(self, title):
            course = Course(title=title)
            assert str(course) == title

    @pytest.mark.django_db
    class TestAssociatedCommitmentsList:
        """Tests for Commitment.associated_commitments_list"""

        def test_no_associated_commitments_returns_empty_iterable(self, minimal_course):
            assert len(minimal_course.associated_commitments_list) == 0
            assert iter(minimal_course.associated_commitments_list)

        def test_one_associated_commitment_returns_iterable_with_it(
            self, minimal_course, minimal_commitment
        ):
            minimal_commitment.associated_course = minimal_course
            minimal_commitment.save()
            assert minimal_commitment in minimal_course.associated_commitments_list
            assert iter(minimal_course.associated_commitments_list)

    @pytest.mark.django_db
    class TestStatistics:
        """Tests for checking that CourseLogic.statistics integrates with Course"""

        def test_associated_commitment_generates_statistics_total_1(
            self, minimal_course, minimal_commitment
        ):
            minimal_commitment.associated_course = minimal_course
            minimal_commitment.save()
            assert minimal_course.statistics["associated_commitments"]["total"] == 1


    @pytest.mark.django_db
    class TestEnrollStudentWithJoinCode:
        """Tests for checking that CourseLogic.enroll_student_with_join_code integrates
        with Course."""

        def test_correct_code_enrolls_student(self, minimal_course, minimal_clinician):
            minimal_course.join_code = "JOINCODE"
            minimal_course.enroll_student_with_join_code(minimal_clinician, "JOINCODE")
            assert minimal_clinician in minimal_course.students.all()

        def test_correct_code_does_not_double_enroll_student(
            self, minimal_course, minimal_clinician
        ):
            minimal_course.join_code = "JOINCODE"
            minimal_course.students.add(minimal_clinician)
            minimal_course.enroll_student_with_join_code(minimal_clinician, "JOINCODE")
            assert minimal_course.students.filter(id=minimal_clinician.id).count() == 1
