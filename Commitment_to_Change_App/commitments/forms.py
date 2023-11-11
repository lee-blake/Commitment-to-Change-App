from django.forms import ModelForm, DateInput, ModelChoiceField

from .models import Commitment, Course


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
