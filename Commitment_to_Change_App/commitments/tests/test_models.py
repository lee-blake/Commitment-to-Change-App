import pytest

from datetime import date

from cme_accounts.models import User
from commitments.models import ClinicianProfile, Commitment


class TestCommitmentStatus:
    """Tests for Commitment.CommitmentStatus"""

    class TestToStr:
        """Tests for Commitment.CommitmentStatus.__str__"""

        def test_in_progress_gives_correct_string(self):
            assert str(Commitment.CommitmentStatus.IN_PROGRESS) == "In Progress"

        def test_complete_gives_correct_string(self):
            assert str(Commitment.CommitmentStatus.COMPLETE) == "Complete"
        
        def test_expired_gives_correct_string(self):
            """Test that EXPIRED converts to string correctly.
            
            While we may use 'expired' in the code, it is a little force for users
            and so we should display 'past due' instead."""

            assert str(Commitment.CommitmentStatus.EXPIRED) == "Past Due"

        def test_discontinued_gives_correct_string(self):
            assert str(Commitment.CommitmentStatus.DISCONTINUED) == "Discontinued"


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
                status=Commitment.CommitmentStatus.IN_PROGRESS
            )
            commitment.save_expired_if_past_deadline()
            reloaded_commitment = Commitment.objects.get(id=commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.EXPIRED

        def test_no_status_change_if_future_deadline_and_in_progress(self, saved_commitment_owner):
            commitment = Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=Commitment.CommitmentStatus.IN_PROGRESS
            )
            commitment.save_expired_if_past_deadline()
            reloaded_commitment = Commitment.objects.get(id=commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.IN_PROGRESS
        
        def test_no_status_change_if_not_in_progress(self, saved_commitment_owner):
            today = date.today()
            past_deadline = today.replace(year=today.year - 1)
            commitment = Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=past_deadline,
                status=Commitment.CommitmentStatus.COMPLETE
            )
            commitment.save_expired_if_past_deadline()
            reloaded_commitment = Commitment.objects.get(id=commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.COMPLETE

        def test_no_database_touch_if_not_changed(self, saved_commitment_owner):
            today = date.today()
            past_deadline = today.replace(year=today.year - 1)
            commitment = Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=past_deadline,
                status=Commitment.CommitmentStatus.COMPLETE
            )
            last_modification_before_method_call = commitment.last_updated
            commitment.save_expired_if_past_deadline()
            reloaded_commitment = Commitment.objects.get(id=commitment.id)
            assert reloaded_commitment.last_updated == last_modification_before_method_call