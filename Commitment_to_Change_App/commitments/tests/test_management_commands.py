import datetime
from smtplib import SMTPException

import pytest

from django.core.management import call_command

from commitments.enums import CommitmentStatus
from commitments.management.commands.expire_commitments import \
    expire_in_progress_commitments_past_deadline
from commitments.management.commands.send_reminder_emails import \
    send_one_time_reminder_emails_for_commitments, \
    send_recurring_reminder_emails_for_commitments, \
    try_to_send_all_emails
from commitments.models import Commitment, CommitmentReminderEmail, RecurringReminderEmail


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
class TestSendOneTimeReminderEmailsForCommitments:
    """Tests for send_one_time_reminder_emails_for_commitments"""

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
        send_one_time_reminder_emails_for_commitments()
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
        send_one_time_reminder_emails_for_commitments()
        assert CommitmentReminderEmail.objects.filter(id=yesterday.id).count() == 0
        assert CommitmentReminderEmail.objects.filter(id=today.id).count() == 0
        assert CommitmentReminderEmail.objects.filter(id=tomorrow.id).count() == 1


@pytest.mark.django_db
class TestSendRecurringReminderEmailsForCommitments:
    """Tests for send_recurring_reminder_emails_for_commitments"""

    def test_reminder_emails_are_sent_for_all_non_future_dates(
        self, minimal_commitment, captured_email
    ):
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today() - datetime.timedelta(days=1),
            interval=30
        )
        # This is a quick way to clone minimal_commitment to avoid problems with one-to-one.
        minimal_commitment.id = None
        minimal_commitment.save()
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today(),
            interval=30
        )
        minimal_commitment.id = None
        minimal_commitment.save()
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today() + datetime.timedelta(days=1),
            interval=30
        )
        send_recurring_reminder_emails_for_commitments()
        assert len(captured_email) == 2

    def test_next_email_dates_update_appropriately(
        self, minimal_commitment
    ):
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today() - datetime.timedelta(days=1),
            interval=30
        )
        # This is a quick way to clone minimal_commitment to avoid problems with one-to-one.
        minimal_commitment.id = None
        minimal_commitment.save()
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today(),
            interval=30
        )
        minimal_commitment.id = None
        minimal_commitment.save()
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today() + datetime.timedelta(days=1),
            interval=30
        )
        send_recurring_reminder_emails_for_commitments()
        expected_next_date_for_emails_sent = datetime.date.today() + datetime.timedelta(days=30)
        assert RecurringReminderEmail.objects.filter(
            next_email_date=expected_next_date_for_emails_sent
        ).count() == 2


class TestTryToSendAllEmails:
    """Tests for _try_to_send_all_emails"""

    def test_one_failure_does_not_derail_other_emails(self):
        class FailOnceEmail:
            emails_sent = 0
            has_failed = False

            def send(self):
                if not self.has_failed:
                    self.has_failed = True
                    raise SMTPException()
                self.emails_sent += 1

        fail_once = FailOnceEmail()
        emails = [fail_once, fail_once, fail_once]
        try_to_send_all_emails(emails)
        assert fail_once.emails_sent == 2


@pytest.mark.django_db
class TestSendReminderEmailsCommand:
    """Tests for send_reminder_emails.Command integration"""

    def test_called_command_sends_correct_one_time_emails(
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

    def test_called_command_sends_correct_recurring_emails(
        self, minimal_commitment, captured_email
    ):
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today() - datetime.timedelta(days=1),
            interval=30
        )
        # This is a quick way to clone minimal_commitment to avoid problems with one-to-one.
        minimal_commitment.id = None
        minimal_commitment.save()
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today(),
            interval=30
        )
        minimal_commitment.id = None
        minimal_commitment.save()
        RecurringReminderEmail.objects.create(
            commitment=minimal_commitment,
            next_email_date=datetime.date.today() + datetime.timedelta(days=1),
            interval=30
        )
        call_command("send_reminder_emails")
        assert len(captured_email) == 2
