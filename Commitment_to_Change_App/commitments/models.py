import datetime

from django.core.mail import send_mail
from django.core.validators import MinValueValidator
from django.db import models
from django.template.loader import render_to_string

import cme_accounts.models
from commitments.business_logic import CommitmentLogic, CommitmentTemplateLogic, CourseLogic
from commitments.enums import CommitmentStatus
from commitments import validators


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

    @property
    def email(self):
        return self.user.email


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

    @property
    def derived_commitments(self):
        return list(Commitment.objects.filter(source_template=self).all())


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

    @property
    def associated_commitments_list(self):
        # Because business logic methods iterate over the associated commitments, and because
        # Django ManyToManyFields are not iterable, we must wrap them with a property.
        return self.associated_commitments.all()

    @property
    def suggested_commitments_list(self):
        # Suppressed because this mistakenly triggers an error in the VSCode extension:
        # https://github.com/pylint-dev/pylint-django/issues/404
        # pylint does not show such an error from the command line.
        return self.suggested_commitments.all() #pylint: disable=no-member

    def _add_student(self, student):
        # We must override this due to ManyToManyField using different methods than list.
        # Pylint doesn't understand that contains(...) is applied to the field at runtime.
        if not self.students.contains(student): #pylint: disable=no-member
            self.students.add(student)


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
        default=None,
        related_name="associated_commitments"
    )

    def __init__(self, *args, **kwargs):
        CommitmentLogic.__init__(self, data_object=self)
        models.Model.__init__(self, *args, **kwargs)


class CommitmentReminderEmail(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    commitment = models.ForeignKey(
        Commitment, on_delete=models.CASCADE, related_name="reminder_emails"
    )
    date = models.DateField(
        "Date of email",
        validators=[
            validators.date_is_in_future
        ]
    )

    email_subject_template = "commitments/CommitmentReminderEmail/reminder_email_subject.txt"
    email_body_template = "commitments/CommitmentReminderEmail/reminder_email_body.txt"

    def send(self):
        context = self._generate_context()
        send_mail(
            subject=self._get_mail_subject(context),
            message=self._get_mail_body(context),
            from_email=None, # This uses the default email for the site
            recipient_list=[self.commitment.owner.email]
        )
        # If successful, the email should *not* be sent again. Delete it.
        self.delete()

    def _generate_context(self):
        days_remaining = (self.commitment.deadline - datetime.date.today()).days
        return {
            "date": self.date,
            "commitment": self.commitment,
            "owner": self.commitment.owner,
            "days_remaining": days_remaining
        }

    def _get_mail_subject(self, context):
        return render_to_string(
            self.email_subject_template,
            context=context
        )

    def _get_mail_body(self, context):
        return render_to_string(
            self.email_body_template,
            context=context
        )


class RecurringReminderEmail(models.Model):
    created = models.DateTimeField("Date/Time of creation", auto_now_add=True)
    last_updated = models.DateTimeField("Date/Time of last modification", auto_now=True)
    commitment = models.OneToOneField(
        Commitment, on_delete=models.CASCADE, related_name="recurring_email"
    )
    interval = models.PositiveSmallIntegerField(
        "Interval between emails, in days",
        validators=[
            MinValueValidator(limit_value=1)
        ]
    )
    next_email_date = models.DateField()
