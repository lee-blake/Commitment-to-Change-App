import datetime

from django.db import models

import cme_accounts.models

from commitments.business_logic import CommitmentLogic, CommitmentTemplateLogic, CourseLogic
from commitments.enums import CommitmentStatus
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
        # This property is here because we need to split the authentication user from
        # the different account types. See cme_accounts.models.User for details. As such,
        # the username is stored on the User object.
        return self.user.username


class ProviderProfile(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    user = models.OneToOneField(cme_accounts.models.User, on_delete=models.CASCADE)
    institution = models.CharField("Institution name", max_length=250)


class CommitmentTemplate(CommitmentTemplateLogic, models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    owner = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", max_length=2000)

    def __init__(self, *args, **kwargs):
        CommitmentTemplateLogic.__init__(self, data_object=self)
        models.Model.__init__(self, *args, **kwargs)

    def __str__(self):
        return str(self.title)

    def into_commitment(self, **kwargs):
        return Commitment(
            title=self.title,
            description=self.description,
            source_template=self,
            **kwargs
        )


class Course(CourseLogic, models.Model):
    DEFAULT_JOIN_CODE_LENGTH = 8

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

    def __init__(self, *args, **kwargs):
        CourseLogic.__init__(self, data_object=self)
        models.Model.__init__(self, *args, **kwargs)

    def __str__(self):
        return self.title.__str__()


class Commitment(CommitmentLogic, models.Model):
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
        if self.deadline < today and self.status == CommitmentStatus.IN_PROGRESS:
            self.status = CommitmentStatus.EXPIRED
            self.save()
