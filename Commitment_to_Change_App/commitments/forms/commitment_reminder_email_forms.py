import datetime

from django.forms import ModelForm, DateInput, HiddenInput, BooleanField, Form

from commitments.models import Commitment, CommitmentReminderEmail


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


class ClearCommitmentReminderEmailsForm(Form):
    class Meta:
        model = Commitment
        fields = []

    clear = BooleanField(initial=True, widget=HiddenInput())

    def __init__(self, commitment, *args, **kwargs):
        self._commitment = commitment
        super().__init__(*args, **kwargs)

    def save(self):
        CommitmentReminderEmail.objects.filter(commitment=self._commitment).delete()
