import datetime

from django.forms import ModelForm, DateInput, HiddenInput, BooleanField, Form

from commitments.models import CommitmentReminderEmail, RecurringReminderEmail


class CommitmentReminderEmailForm(ModelForm):
    class Meta:
        model = CommitmentReminderEmail
        fields = [
            "date"
        ]
        widgets = {
            "date": DateInput(attrs={"type": "date"})
        }

    def __init__(self, commitment, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.instance.commitment = commitment
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self.fields['date'].widget.attrs.update({
            "min": f"{tomorrow}"
        })


class RecurringReminderEmailForm(ModelForm):
    class Meta:
        model = RecurringReminderEmail
        fields = [
            "interval"
        ]

    def __init__(self, commitment, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.instance.commitment = commitment
        if not self.instance.next_email_date:
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            self.instance.next_email_date = tomorrow
        self.fields['interval'].widget.attrs.update({
            "min": "1",
            "value": 30
        })


class ClearCommitmentReminderEmailsForm(Form):
    clear = BooleanField(initial=True, widget=HiddenInput())

    def __init__(self, commitment, *args, **kwargs):
        self._commitment = commitment
        super().__init__(*args, **kwargs)

    def save(self):
        CommitmentReminderEmail.objects.filter(commitment=self._commitment).delete()
