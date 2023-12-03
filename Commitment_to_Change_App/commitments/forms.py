from django.forms import ModelForm, DateInput, ModelChoiceField, CheckboxSelectMultiple, \
    ModelMultipleChoiceField

from .models import ClinicianProfile, Commitment, Course, CommitmentTemplate, ProviderProfile


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
        profile = kwargs.pop("profile")
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['associated_course'].queryset = profile.course_set.all()


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


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "description"
        ]


class CommitmentTemplateForm(ModelForm):
    class Meta:
        model = CommitmentTemplate
        fields = [
            "title",
            "description"
        ]

class CourseSelectSuggestedCommitmentsForm(ModelForm):
    class Meta:
        model = Course
        fields = ["suggested_commitments"]

    suggested_commitments = ModelMultipleChoiceField(
        queryset=CommitmentTemplate.objects.none(),
        required=False,
        widget=CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields["suggested_commitments"].queryset = \
            CommitmentTemplate.objects.filter(owner=self.instance.owner)


class ProviderProfileForm(ModelForm):
    class Meta:
        model = ProviderProfile
        fields = [
            "institution"
        ]


class ClinicianProfileForm(ModelForm):
    class Meta:
        model = ClinicianProfile
        fields = [
            "first_name",
            "last_name",
            "institution"
        ]