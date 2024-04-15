import datetime

from django.forms import ModelForm, DateInput, ModelChoiceField, \
    BooleanField, HiddenInput, TypedChoiceField
from django.db.models import IntegerChoices

from commitments.models import Commitment, Course, CommitmentReminderEmail, \
    RecurringReminderEmail


class CommitmentForm(ModelForm):
    class Meta:
        model = Commitment
        fields = [
            "title",
            "description",
            "deadline",
            "associated_course"
        ]
        widgets = {
            "deadline": DateInput(attrs={"type": "date"})
        }

    associated_course = ModelChoiceField(
        queryset=Course.objects.none(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner")
        super(ModelForm, self).__init__(*args, **kwargs)
        self._set_owner_enrolled_courses_as_associated_course_options(owner)
        self._disable_editing_if_suggested_commitment()
        self.fields['deadline'].widget.attrs.update({
            "min": f"{datetime.date.today()}"
        })

    def _set_owner_enrolled_courses_as_associated_course_options(self, owner):
        if not hasattr(self.instance, 'owner') or not self.instance.owner:
            self.instance.owner = owner
        elif owner != self.instance.owner:
            raise ValueError("Cannot change the owner of a commitment!")
        self.fields['associated_course'].queryset = self.instance.owner.course_set.all()

    def _disable_editing_if_suggested_commitment(self):
        if self.instance.source_template:
            self.fields["title"].disabled = True
            self.fields["description"].disabled = True
            self.fields["associated_course"].disabled = True


class CommitmentCreationForm(CommitmentForm):
    """This class exists to add preset reminder options on email creation but not on edits."""

    class ReminderOption(IntegerChoices):
        NO_REMINDERS = (0, "No reminders")
        DEADLINE_ONLY = (1, "One email on the deadline")
        MONTHLY = (2, "One reminder per month")
        WEEKLY = (3, "One reminder per week")

    reminder_schedule = TypedChoiceField(
        coerce=int,
        choices=ReminderOption.choices,
        initial=ReminderOption.MONTHLY,
        help_text="These options may be customized further after you make this commitment.",
        # We will treat empty = NO_REMINDERS.
        # This simplifies the code for testing other creation functionality.
        empty_value=ReminderOption.NO_REMINDERS,
        required=False
    )

    def save(self, commit=True):
        commitment = super(CommitmentForm, self).save(commit)
        schedule = self.cleaned_data.get(
            "reminder_schedule", 
            CommitmentCreationForm.ReminderOption.NO_REMINDERS
        )
        if commit:
            self._create_emails_for_preset_schedule(commitment, schedule)
        return commitment

    def _create_emails_for_preset_schedule(self, commitment, schedule):
        match schedule:
            case CommitmentCreationForm.ReminderOption.DEADLINE_ONLY.value:
                CommitmentReminderEmail.objects.create(
                    commitment=commitment,
                    date=commitment.deadline
                )
            case CommitmentCreationForm.ReminderOption.MONTHLY.value:
                self._create_recurring_email_with_interval(commitment, 30)
            case CommitmentCreationForm.ReminderOption.WEEKLY.value:
                self._create_recurring_email_with_interval(commitment, 7)

    def _create_recurring_email_with_interval(self, commitment, interval):
        RecurringReminderEmail.objects.create(
            commitment=commitment,
            next_email_date=datetime.date.today() + datetime.timedelta(days=1),
            interval=interval
        )


class CreateCommitmentFromSuggestedCommitmentForm(CommitmentCreationForm):
    def __init__(self, suggested_commitment_template, source_course, *args, **kwargs):
        if kwargs.get("instance"):
            raise TypeError(
                "CreateCommitmentFromSuggestedCommitmentForm is for creating new Commitments only!"
            )
        instance = Commitment()
        instance.apply_commitment_template(suggested_commitment_template)
        instance.associated_course = source_course
        kwargs.update({"instance": instance})
        super().__init__(*args, **kwargs )


class CompleteCommitmentForm(ModelForm):
    class Meta:
        model = Commitment
        fields = []

    complete = BooleanField(initial=True, widget=HiddenInput())

    def save(self, commit=True):
        self.instance.mark_complete()
        super().save(commit=commit)


class DiscontinueCommitmentForm(ModelForm):
    class Meta:
        model = Commitment
        fields = []

    discontinue = BooleanField(initial=True, widget=HiddenInput())

    def save(self, commit=True):
        self.instance.mark_discontinued()
        super().save(commit=commit)


class ReopenCommitmentForm(ModelForm):
    class Meta:
        model = Commitment
        fields = []

    reopen = BooleanField(initial=True, widget=HiddenInput())

    def save(self, commit=True):
        self.instance.reopen()
        super().save(commit=commit)
