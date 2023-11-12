import cme_accounts.models
from django.db import models

from . import validators


# TODO this is just for demonstrating that inherited methods work. When we
# create the actual CommitmentLogicProvider* class, we will remove this.
#   *Name subject to change.
class CommitmentParent:
    def double_description(self):
        self.description += self.description


# Create your models here.

class ClinicianProfile(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    user = models.OneToOneField(cme_accounts.models.User, on_delete=models.CASCADE)

    @property
    def username(self):
        return self.user.username


class ProviderProfile(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    user = models.OneToOneField(cme_accounts.models.User, on_delete=models.CASCADE)


class Course(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    owner = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", max_length=2000)
    join_code = models.CharField("Join code", max_length=100)
    students = models.ManyToManyField(ClinicianProfile)

    def __str__(self):
        return self.title


class Commitment(models.Model, CommitmentParent):
    class CommitmentStatus(models.IntegerChoices):
        IN_PROGRESS = 0
        COMPLETE = 1
        EXPIRED = 2
        DISCONTINUED = 3

        def __str__(self):
            match self:
                case 0:
                    return "In progress"
                case 1:
                    return "Complete"
                case 2:
                    return "Past Due"
                case 3:
                    return "Discontinued"
                case _:
                    return "no number"

    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    owner = models.ForeignKey(ClinicianProfile, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", max_length=2000)
    status = models.IntegerField(choices=CommitmentStatus.choices)
    deadline = models.DateField("Deadline", validators=[
        validators.date_is_not_in_past
    ])
    associated_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, default=None)

    @property
    def status_text(self):
        return Commitment.CommitmentStatus.__str__(self.status)

    # TODO This needs to go away once we have an expiration daemon.
    def mark_expired_if_deadline_has_passed(self, today):
        if self.deadline < today and self.status == Commitment.CommitmentStatus.IN_PROGRESS:
            self.status = Commitment.CommitmentStatus.EXPIRED
            self.save()