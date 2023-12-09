from datetime import date

import pytest

from cme_accounts.models import User
from commitments.enums import CommitmentStatus
from commitments.models import ClinicianProfile, Commitment, CommitmentTemplate, \
    ProviderProfile, Course

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

    class TestIntoCommitment:
        """Tests for CommitmentTemplate.into_commitment"""

        @pytest.fixture(name="commitment_template_owner")
        def fixture_commitment_template_owner(self):
            user = User(
                username="provider",
                password="password",
                email="test@email.me",
                is_provider=True
            )
            return ProviderProfile(
                user=user
            )

        @pytest.fixture(name="commitment_owner")
        def fixture_commitment_owner(self):
            user = User(
                username="clinician",
                password="password",
                email="test@email.me",
                is_clinician=True
            )
            return ClinicianProfile(
                user=user
            )

        def test_converting_copies_required_template_fields(self, commitment_template_owner):
            template = CommitmentTemplate(
                title="Template title",
                description="Template description",
                owner=commitment_template_owner
            )
            commitment = template.into_commitment()
            assert commitment.title == "Template title"
            assert commitment.description == "Template description"

        def test_converting_does_not_return_same_require_template_fields_each_time(
            self, commitment_template_owner
        ):
            template = CommitmentTemplate(
                title="A different title",
                description="A different description",
                owner=commitment_template_owner
            )
            commitment = template.into_commitment()
            assert commitment.title == "A different title"
            assert commitment.description == "A different description"

        def test_converting_correctly_refers_back_to_source_template(
            self, commitment_template_owner
        ):
            template = CommitmentTemplate(
                title="Template title",
                description="Template description",
                owner=commitment_template_owner
            )
            commitment = template.into_commitment()
            assert commitment.source_template == template

        def test_converting_assigns_mandatory_commitment_keyword_arguments(
            self, commitment_owner, commitment_template_owner
        ):
            """Test that other mandatory keyword arguments to Commitments are set on the Commitment
            created by into_commitment"""

            template = CommitmentTemplate(
                title="Template title",
                description="Template description",
                owner=commitment_template_owner
            )
            commitment = template.into_commitment(
                owner=commitment_owner,
                deadline=date.today()
            )
            assert commitment.deadline == date.today()


    class TestCommitmentTemplateToString:
        """Tests for CommitmentTemplate.__str__"""

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
        """Tests for Course.__str__"""

        @pytest.mark.parametrize("title", ["First title", "Second title"])
        def test_returns_title(self, title):
            course = Course(title=title)
            assert str(course) == title
        