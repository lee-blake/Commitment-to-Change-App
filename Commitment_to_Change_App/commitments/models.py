from django.db import models


# TODO this is just for demonstrating that inherited methods work. When we
# create the actual CommitmentLogicProvider* class, we will remove this.
#   *Name subject to change.
class CommitmentParent:
    def double_description(self):
        self.description += self.description


# Create your models here.

class Commitment(models.Model, CommitmentParent):
    class CommitmentStatus(models.IntegerChoices):
        IN_PROGRESS = 0
        COMPLETE = 1
        EXPIRED = 2

    created = models.DateTimeField("Datetime of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Datetime of last modification", auto_now=True)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Detailed description", max_length=2000)
    status = models.IntegerField(choices=CommitmentStatus.choices)
    deadline = models.DateField("Deadline of the commitment")

    # TODO This needs to go away once we have an expiration daemon.
    def mark_expired_if_deadline_has_passed(self, today):
        if self.deadline < today and self.status == Commitment.CommitmentStatus.IN_PROGRESS:
            self.status = Commitment.CommitmentStatus.EXPIRED
            self.save()
