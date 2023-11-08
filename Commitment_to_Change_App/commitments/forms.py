from django.forms import ModelForm, DateInput

from .models import Commitment


class CommitmentForm(ModelForm):
    class Meta:
        model = Commitment
        fields = [
            "title",
            "description",
            "deadline"
        ]
        widgets = {
            "deadline": DateInput(attrs={"type": "date"})
        }


class DeleteCommitmentForm(ModelForm):
    class Meta:
        model = Commitment
        fields = [
            "title",
            "deadline"
        ]
        widgets = {
            "deadline": DateInput(attrs={"type": "date"})
        }
