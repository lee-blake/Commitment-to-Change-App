import datetime
from smtplib import SMTPException

from django.core.management.base import BaseCommand

from commitments.models import CommitmentReminderEmail


def send_reminder_emails_for_commitments():
    emails_scheduled_for_today_or_earlier = CommitmentReminderEmail.objects.filter(
        # Include prior days in case email failed to send previously.
        date__lte=datetime.date.today(),
    ).all()
    for email in emails_scheduled_for_today_or_earlier:
        try:
            email.send()
        except SMTPException:
            pass # Do not cause the whole batch to fail if only one is a problem.


class Command(BaseCommand):
    help = "Sends reminder emails scheduled for today or earlier."

    def handle(self, *args, **kwargs):
        send_reminder_emails_for_commitments()
