import datetime

from django.db import models

import cme_accounts.models

from . import validators


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


class Commitment(models.Model):
    class CommitmentStatus(models.IntegerChoices):
        IN_PROGRESS = 0
        COMPLETE = 1
        EXPIRED = 2
        DISCONTINUED = 3

        def __str__(self):
            match self:
                case 0:
                    return "In Progress"
                case 1:
                    return "Complete"
                case 2:
                    return "Past Due"
                case 3:
                    return "Discontinued"


    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    source_template = models.ForeignKey(
        CommitmentTemplate, on_delete=models.SET_NULL, null=True, default=None
    )
    owner = models.ForeignKey(ClinicianProfile, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", max_length=2000)
    status = models.IntegerField(choices=CommitmentStatus.choices)
    deadline = models.DateField("Deadline", validators=[
        validators.date_is_not_in_past
    ])
    associated_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    @property
    def status_text(self):
        return Commitment.CommitmentStatus.__str__(self.status)

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
