import pytest

from datetime import date

from cme_accounts.models import User
from commitments.models import ClinicianProfile, Commitment


class TestCommitment:
    @pytest.fixture
    def commitment_owner(self):
        user = User(
            username="testuser", 
            password="password", 
            email="test@email.me"
        )
        return ClinicianProfile(
            user=user
        )

    class TestMarkExpiredIfPastDeadline:
        """Tests for mark_expired_if_past_deadline"""
        def test_marks_expired_if_past_deadline_and_in_progress(self, commitment_owner):
            today = date.today()
            past_deadline = today.replace(year=today.year - 1)
            commitment = Commitment(
                owner=commitment_owner,
                title="Test title",
                description="Test description",
                deadline=past_deadline,
                status=Commitment.CommitmentStatus.IN_PROGRESS
            )
            commitment.mark_expired_if_past_deadline()
            assert commitment.status == Commitment.CommitmentStatus.EXPIRED
        
        def test_no_status_change_if_future_deadline_and_in_progress(self, commitment_owner):
            commitment = Commitment(
                owner=commitment_owner,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=Commitment.CommitmentStatus.IN_PROGRESS
            )
            commitment.mark_expired_if_past_deadline()
            assert commitment.status == Commitment.CommitmentStatus.IN_PROGRESS
        
        def test_no_status_change_if_not_in_progress(self, commitment_owner):
            today = date.today()
            past_deadline = today.replace(year=today.year - 1)
            commitment = Commitment(
                owner=commitment_owner,
                title="Test title",
                description="Test description",
                deadline=past_deadline,
                status=Commitment.CommitmentStatus.COMPLETE
            )
            commitment.mark_expired_if_past_deadline()
            assert commitment.status == Commitment.CommitmentStatus.COMPLETE
        