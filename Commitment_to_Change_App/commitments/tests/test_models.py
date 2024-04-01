from datetime import date, timedelta
from smtplib import SMTPException

import pytest

from cme_accounts.models import User
from commitments.models import ClinicianProfile, Commitment, CommitmentTemplate, Course, \
    CommitmentReminderEmail, RecurringReminderEmail


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


    @pytest.mark.django_db
    class TestDerivedCommitments:
        """Tests for CommitmentTemplate.derived_commitments"""

        def test_no_derived_commitments_returns_empty_list(self, minimal_provider):
            template = CommitmentTemplate.objects.create(
                title="Test CommitmentTemplate",
                description="No derived commitments",
                owner=minimal_provider
            )
            assert template.derived_commitments == []

        def test_one_derived_commitment_returns_in_list(self, minimal_provider, minimal_clinician):
            template = CommitmentTemplate.objects.create(
                title="Test CommitmentTemplate",
                description="One derived commitment",
                owner=minimal_provider
            )
            commitment = Commitment.objects.create(
                title="Test Commitment",
                description="Derived from a CommitmentTemplate",
                deadline=date.today(),
                owner=minimal_clinician,
                source_template=template
            )
            assert template.derived_commitments == [commitment]


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
        """Tests for Course.associated_commitments_list"""

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
    class TestSuggestedCommitmentsList:
        """Tests for Course.suggested_commitments_list"""

        def test_no_suggested_commitments_returns_empty_iterable(self, minimal_course):
            assert len(minimal_course.suggested_commitments_list) == 0
            assert iter(minimal_course.suggested_commitments_list)

        def test_one_suggested_commitment_returns_iterable_containing_it(
            self, minimal_course, minimal_commitment_template
        ):
            minimal_course.suggested_commitments.add(minimal_commitment_template)
            minimal_course.save()
            assert minimal_commitment_template in minimal_course.suggested_commitments_list
            assert iter(minimal_course.suggested_commitments_list)


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


@pytest.mark.django_db
class TestCommitmentReminderEmail:
    """Tests for CommitmentReminderEmail"""

    class TestSend:
        """Tests for CommitmentReminderEmail.send"""

        def test_sends_email_to_correct_address(self, minimal_commitment, captured_email):
            reminder_email = CommitmentReminderEmail.objects.create(
                commitment=minimal_commitment,
                date=date.today()
            )
            reminder_email.send()
            assert len(captured_email) == 1
            assert captured_email[0].to == [minimal_commitment.owner.user.email]

        def test_deletes_self_after_sending(self, minimal_commitment):
            reminder_email = CommitmentReminderEmail.objects.create(
                commitment=minimal_commitment,
                date=date.today()
            )
            reminder_email.send()
            assert CommitmentReminderEmail.objects.filter(id=reminder_email.id).count() == 0

        def test_does_not_delete_if_sending_fails(self, settings, minimal_commitment):
            settings.EMAIL_BACKEND = "commitments.tests.helpers.FailBackend"
            reminder_email = CommitmentReminderEmail.objects.create(
                commitment=minimal_commitment,
                date=date.today()
            )
            with pytest.raises(SMTPException):
                reminder_email.send()
            assert CommitmentReminderEmail.objects.filter(id=reminder_email.id).count() == 1

        def test_subject_contains_indication_of_purpose(self, captured_email, minimal_commitment):
            reminder_email = CommitmentReminderEmail.objects.create(
                commitment=minimal_commitment,
                date=date.today()
            )
            reminder_email.send()
            assert len(captured_email) == 1
            assert "commitment" in captured_email[0].subject.lower()

        @pytest.mark.parametrize("title", ["Title 1", "Title 2"])
        def test_body_references_specific_commitment(
            self, captured_email, minimal_commitment, title
        ):
            minimal_commitment.title = title
            minimal_commitment.save()
            reminder_email = CommitmentReminderEmail.objects.create(
                commitment=minimal_commitment,
                date=date.today()
            )
            reminder_email.send()
            assert len(captured_email) == 1
            assert title in captured_email[0].body


@pytest.mark.django_db
class TestRecurringReminderEmail:
    """Tests for RecurringReminderEmail"""

    class TestSend:
        """Tests for RecurringReminderEmail.send"""

        def test_sends_email_to_correct_address(self, minimal_commitment, captured_email):
            recurring_email = RecurringReminderEmail.objects.create(
                commitment=minimal_commitment,
                next_email_date=date.today(),
                interval=30
            )
            recurring_email.send()
            assert len(captured_email) == 1
            assert captured_email[0].to == [minimal_commitment.owner.user.email]

        def test_subject_contains_indication_of_purpose(self, captured_email, minimal_commitment):
            recurring_email = RecurringReminderEmail.objects.create(
                commitment=minimal_commitment,
                next_email_date=date.today(),
                interval=30
            )
            recurring_email.send()
            assert len(captured_email) == 1
            assert "commitment" in captured_email[0].subject.lower()

        @pytest.mark.parametrize("title", ["Title 1", "Title 2"])
        def test_body_references_specific_commitment(
            self, captured_email, minimal_commitment, title
        ):
            minimal_commitment.title = title
            minimal_commitment.save()
            recurring_email = RecurringReminderEmail.objects.create(
                commitment=minimal_commitment,
                next_email_date=date.today(),
                interval=30
            )
            recurring_email.send()
            assert len(captured_email) == 1
            assert title in captured_email[0].body

        def test_next_email_sent_updates_relative_to_today(
            self, minimal_commitment
        ):
            recurring_email = RecurringReminderEmail.objects.create(
                commitment=minimal_commitment,
                next_email_date=date(2000, 1, 1),
                interval=1
            )
            recurring_email.send()
            reloaded_recurring_email = RecurringReminderEmail.objects.get(id=recurring_email.id)
            assert reloaded_recurring_email.next_email_date == date.today() + timedelta(days=1)
