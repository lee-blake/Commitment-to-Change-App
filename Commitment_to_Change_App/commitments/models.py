import datetime

from django.db import models

import cme_accounts.models
import commitments.enums

from commitments.business_logic import CommitmentLogic
from . import validators


class ClinicianProfile(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    user = models.OneToOneField(cme_accounts.models.User, on_delete=models.CASCADE)
    first_name = models.CharField("First name", max_length=100, blank=True, null=True)
    last_name = models.CharField("Last name", max_length=100, blank=True, null=True)
    institution = models.CharField("Institution", max_length=250, blank=True, null=True)

    @property
    def username(self):
        return self.user.username


class ProviderProfile(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    user = models.OneToOneField(cme_accounts.models.User, on_delete=models.CASCADE)
    institution = models.CharField("Institution name", max_length=250)


class CommitmentTemplate(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    owner = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", max_length=2000)

    def __str__(self):
        return str(self.title)

    def into_commitment(self, **kwargs):
        return Commitment(
            title=self.title,
            description=self.description,
            source_template=self,
            **kwargs
        )


class Course(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    owner = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", max_length=2000)
    identifier = models.CharField("Identifier", max_length=64, blank=True, null=True)
    start_date = models.DateField("Course start date", blank=True, null=True)
    end_date = models.DateField("Course end date", blank=True, null=True)
    suggested_commitments = models.ManyToManyField(CommitmentTemplate)
    join_code = models.CharField("Join code", max_length=100)
    students = models.ManyToManyField(ClinicianProfile)

    def __str__(self):
        return self.title.__str__()


class Commitment(CommitmentLogic, models.Model):
    # TODO This is a ompatibility fix to avoid changing usages until logic is fully extracted.
    CommitmentStatus = commitments.enums.CommitmentStatus

    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    source_template = models.ForeignKey(
        CommitmentTemplate, on_delete=models.SET_NULL, null=True, default=None
    )
    owner = models.ForeignKey(ClinicianProfile, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", max_length=2000)
    status = models.IntegerField(
        choices=CommitmentStatus.choices,
        default = CommitmentStatus.IN_PROGRESS
    )
    deadline = models.DateField("Deadline", validators=[
        validators.date_is_not_in_past
    ])
    associated_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    def __init__(self, *args, **kwargs):
        CommitmentLogic.__init__(self, data_object=self)
        models.Model.__init__(self, *args, **kwargs)

    def save_expired_if_past_deadline(self):
        today = datetime.date.today()
        if self.deadline < today and self.status == Commitment.CommitmentStatus.IN_PROGRESS:
            self.status = Commitment.CommitmentStatus.EXPIRED
            self.save()

    def mark_complete(self):
        self.status = Commitment.CommitmentStatus.COMPLETE

    def mark_discontinued(self):
        self.status = Commitment.CommitmentStatus.DISCONTINUED

    def reopen(self):
        if self.status in {
            Commitment.CommitmentStatus.COMPLETE,
            Commitment.CommitmentStatus.DISCONTINUED
            }:
            today = datetime.date.today()
            if self.deadline >= today:
                self.status = Commitment.CommitmentStatus.IN_PROGRESS
            else:
                self.status = Commitment.CommitmentStatus.EXPIRED
