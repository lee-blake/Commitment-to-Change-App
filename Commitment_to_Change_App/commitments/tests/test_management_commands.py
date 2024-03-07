import datetime
import pytest

from django.core.management import call_command

from commitments.enums import CommitmentStatus
from commitments.management.commands.expire_commitments import \
    expire_in_progress_commitments_past_deadline
from commitments.management.commands.send_reminder_emails import \
    send_reminder_emails_for_commitments
from commitments.models import Commitment, CommitmentReminderEmail


@pytest.mark.django_db
class TestExpireInProgressCommitmentsPastDeadline:
    """Tests for expire_in_progress_commitments_past_deadline"""

    def test_commitment_satisfying_conditions_is_expired(self, minimal_commitment):
        minimal_commitment.deadline = datetime.date(2000, 1, 1)
        minimal_commitment.status = CommitmentStatus.IN_PROGRESS
        minimal_commitment.save()
        expire_in_progress_commitments_past_deadline()
        reloaded_commitment = Commitment.objects.get(id=minimal_commitment.id)
        assert reloaded_commitment.status == CommitmentStatus.EXPIRED

    @pytest.mark.parametrize(
        "wrong_status", 
        [CommitmentStatus.COMPLETE, CommitmentStatus.DISCONTINUED]
    )
    def test_commitment_with_wrong_status_is_not_expired(
        self, minimal_commitment, wrong_status
    ):
        minimal_commitment.deadline = datetime.date(2000, 1, 1)
        minimal_commitment.status = wrong_status
        minimal_commitment.save()
        expire_in_progress_commitments_past_deadline()
        reloaded_commitment = Commitment.objects.get(id=minimal_commitment.id)
        assert reloaded_commitment.status == wrong_status

    def test_commitment_with_non_past_deadline_is_not_expired(self, minimal_commitment):
        minimal_commitment.deadline = datetime.date.today()
        minimal_commitment.status = CommitmentStatus.IN_PROGRESS
        minimal_commitment.save()
        expire_in_progress_commitments_past_deadline()
        reloaded_commitment = Commitment.objects.get(id=minimal_commitment.id)
        assert reloaded_commitment.status == CommitmentStatus.IN_PROGRESS


@pytest.mark.django_db
class TestExpireCommitmentCommand:
    """Tests for expire_commitment.Command integration"""

    def test_called_command_expires_relevant_commitments(self, minimal_commitment):
        minimal_commitment.deadline = datetime.date(2000, 1, 1)
        minimal_commitment.status = CommitmentStatus.IN_PROGRESS
        minimal_commitment.save()
        call_command("expire_commitments")
        reloaded_commitment = Commitment.objects.get(id=minimal_commitment.id)
        assert reloaded_commitment.status == CommitmentStatus.EXPIRED


@pytest.mark.django_db
class TestSendReminderEmailsForCommitments:
    """Tests for send_reminder_emails_for_commitments"""

    def test_reminder_emails_are_sent_for_all_non_future_dates(
        self, minimal_commitment, captured_email
    ):
        CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today() - datetime.timedelta(days=1)
        )
        CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today()
        )
        CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today() + datetime.timedelta(days=1)
        )
        send_reminder_emails_for_commitments()
        assert len(captured_email) == 2

    def test_correct_reminder_email_objects_are_deleted(
        self, minimal_commitment
    ):
        yesterday = CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today() - datetime.timedelta(days=1)
        )
        today = CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today()
        )
        tomorrow = CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today() + datetime.timedelta(days=1)
        )
        send_reminder_emails_for_commitments()
        assert CommitmentReminderEmail.objects.filter(id=yesterday.id).count() == 0
        assert CommitmentReminderEmail.objects.filter(id=today.id).count() == 0
        assert CommitmentReminderEmail.objects.filter(id=tomorrow.id).count() == 1


@pytest.mark.django_db
class TestSendReminderEmailsCommand:
    """Tests for send_reminder_emails.Command integration"""

    def test_called_command_sends_correct_emails(
        self, minimal_commitment, captured_email
    ):
        CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today() - datetime.timedelta(days=1)
        )
        CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today()
        )
        CommitmentReminderEmail.objects.create(
            commitment=minimal_commitment,
            date=datetime.date.today() + datetime.timedelta(days=1)
        )
        call_command("send_reminder_emails")
        assert len(captured_email) == 2
