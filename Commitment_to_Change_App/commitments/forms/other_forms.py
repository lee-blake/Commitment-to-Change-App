from django.forms import ModelForm, HiddenInput, BooleanField, Form

from commitments.models import ClinicianProfile, CommitmentTemplate, ProviderProfile


class ClinicianProfileForm(ModelForm):
    class Meta:
        model = ClinicianProfile
        fields = [
            "first_name",
            "last_name",
            "institution"
        ]


class ProviderProfileForm(ModelForm):
    class Meta:
        model = ProviderProfile
        fields = [
            "institution"
        ]


class CommitmentTemplateForm(ModelForm):
    class Meta:
        model = CommitmentTemplate
        fields = [
            "title",
            "description"
        ]


class GenericDeletePostKeySetForm(Form):
    """A generic form that can be used for DeleteViews. It requires that the POST key 'delete'
    be nonempty, which helps ensure that POST requests to delete are intentional."""

    delete = BooleanField(initial=True, widget=HiddenInput())
