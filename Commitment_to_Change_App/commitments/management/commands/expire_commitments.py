import datetime

from django.core.management.base import BaseCommand

from commitments.enums import CommitmentStatus
from commitments.models import Commitment


def expire_in_progress_commitments_past_deadline():
    commitments_past_deadline = Commitment.objects.filter(
        deadline__lt=datetime.date.today(),
        status=CommitmentStatus.IN_PROGRESS
    )
    commitments_past_deadline.update(status=CommitmentStatus.EXPIRED)


class Command(BaseCommand):
    help = "Marks commitments that are in progress and past their deadlines as expired"

    def handle(self, *args, **kwargs):
        expire_in_progress_commitments_past_deadline()
