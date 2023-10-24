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
