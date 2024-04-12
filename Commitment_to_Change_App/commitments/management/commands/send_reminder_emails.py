import datetime
from smtplib import SMTPException

from django.core.management.base import BaseCommand

from commitments.models import CommitmentReminderEmail, RecurringReminderEmail


def send_one_time_reminder_emails_for_commitments():
    emails_scheduled_for_today_or_earlier = CommitmentReminderEmail.objects.filter(
        # Include prior days in case email failed to send previously.
        date__lte=datetime.date.today(),
    ).all()
    try_to_send_all_emails(emails_scheduled_for_today_or_earlier)

def send_recurring_reminder_emails_for_commitments():
    recurring_emails_scheduled_for_today_or_earlier = RecurringReminderEmail.objects.filter(
        # Include prior days in case email failed to send previously.
        next_email_date__lte=datetime.date.today()
    ).all()
    try_to_send_all_emails(recurring_emails_scheduled_for_today_or_earlier)

def try_to_send_all_emails(emails):
    for email in emails:
        try:
            email.send()
        except SMTPException:
            pass # Do not cause the whole batch to fail if only one is a problem.


class Command(BaseCommand):
    help = "Sends reminder emails scheduled for today or earlier."

    def handle(self, *args, **kwargs):
        send_one_time_reminder_emails_for_commitments()
        send_recurring_reminder_emails_for_commitments()
