from datetime import date
from django.test import SimpleTestCase
from cme_accounts.models import User
from .models import Commitment, ClinicianProfile

class CommitmentTestCase(SimpleTestCase):
    def setUp(self):
        user = User(username="testuser", password="password", email="test@email.me")
        self.commitment_owner = ClinicianProfile(user=user)
        
    def test_mark_complete_marks_complete(self):
        """Test that mark_complete actually sets commitment status to complete."""
        commitment = Commitment(
            owner=self.commitment_owner,
            title="In Progress",
            description="Mark me complete please",
            deadline=date.today(),
            status=Commitment.CommitmentStatus.IN_PROGRESS
        )
        commitment.mark_complete()
        self.assertEqual(
            Commitment.CommitmentStatus.COMPLETE,
            commitment.status
        )

    def test_mark_discontinued_marks_discontinued(self):
        commitment = Commitment(
            owner=self.commitment_owner,
            title="In Progress",
            description="Mark me discontinued please",
            deadline=date.today(),
            status=Commitment.CommitmentStatus.IN_PROGRESS
        )
        commitment.mark_discontinued()
        self.assertEqual(
            Commitment.CommitmentStatus.DISCONTINUED,
            commitment.status
        )
        # TODO CLAYTON Make this test like the one above, then implement in models.py and
        # change things in views.py to use your new method.

    def test_reopen_marks_in_progress_when_date_is_not_past(self):
        today = date.today()
        future_deadline = today.replace(year=today.year + 1)

        commitment = Commitment(
            owner=self.commitment_owner,
            title="Complete",
            description="Reopen me please",
            deadline=future_deadline,
            status=Commitment.CommitmentStatus.COMPLETE
        )

        commitment.reopen()

        self.assertEqual(
            Commitment.CommitmentStatus.IN_PROGRESS,
            commitment.status
        )
        # Make this test like the ones above, but make sure the deadline is not
        # a past date. Also make sure the initial status is COMPLETE or DISCONTINUED. 
        # Implement in models.py.

    def test_reopen_marks_expired_when_date_is_past(self):
        today = date.today()
        past_deadline = today.replace(year=today.year - 1)

        commitment = Commitment(
            owner=self.commitment_owner,
            title="Complete",
            description="Reopen me please",
            deadline=past_deadline,
            status=Commitment.CommitmentStatus.COMPLETE
        )

        commitment.reopen()

        self.assertEqual(
            Commitment.CommitmentStatus.EXPIRED,
            commitment.status
        )
    