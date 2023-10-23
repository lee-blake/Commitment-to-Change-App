from django.db import models


# TODO this is just for demonstrating that inherited methods work. When we
# create the actual CommitmentLogicProvider* class, we will remove this.
#   *Name subject to change.
class CommitmentParent:
    def double_description(self):
        self.description += self.description


# Create your models here.

class Commitment(models.Model, CommitmentParent):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
