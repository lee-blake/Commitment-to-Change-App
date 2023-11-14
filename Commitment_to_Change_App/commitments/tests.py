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
        pass # TODO CLAYTON Make this test like the ones above, but make sure the deadline is not
        # a past date. Also make sure the initial status is COMPLETE or DISCONTINUED. 
        # Implement in models.py.

    def test_reopen_marks_expired_when_date_is_past(self):
        pass # TODO CLAYTON Make this, but make sure the deadline is yesterday or earlier.
        # datetime.timedelta(days=1) can help you here. Implement in models.py.
        # Change usage in views.py once this and the above test are done
    
    def test_mark_commitment_expired_if_deadline_has_passed_doesnt_change_complete_status(self):
        pass # TODO CLAYTON If the commitment is complete, its status should remain complete
        # after the method call. Should not require changing method.

    def test_mark_commitment_expired_if_deadline_has_passed_doesnt_change_discontinued_status(self):
        pass # TODO CLAYTON If the commitment is discontinued, its status should remain discontinued
        # after the method call. Should not require changing method.

    def test_mark_commitment_expired_if_deadline_has_passed_doesnt_change_expired_status(self):
        pass # TODO CLAYTON If the commitment is expired, its status should remain expired
        # after the method call, EVEN IF THE DEADLINE IS IN THE FUTURE. Should not require 
        # changing method.

    def test_mark_commitment_expired_if_deadline_has_passed_doesnt_change_future_deadline(self):
        pass # TODO CLAYTON If the deadline is in the future, don't change the status. Should
        # not require changing method.

    def test_mark_commitment_expired_if_deadline_has_passed_expires_if_deadline_in_past(self):
        pass # TODO CLAYTON If the status is IN_PROGRESS and the deadline is in the past (not
        # today), it should be EXPIRED after calling the function. Should not require changing 
        # method.