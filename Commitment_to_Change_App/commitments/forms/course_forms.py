from django.core.exceptions import ValidationError
from django.forms import ModelForm, CheckboxSelectMultiple, HiddenInput, \
    ModelMultipleChoiceField, BooleanField, DateInput

from commitments.models import Course, CommitmentTemplate


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "description",
            "identifier",
            "start_date",
            "end_date"
        ]
        widgets = {
            "start_date": DateInput(attrs={"type": "date"}),
            "end_date": DateInput(attrs={"type": "date"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.generate_join_code_if_none_exists(
            Course.DEFAULT_JOIN_CODE_LENGTH
        )

    def clean(self):
        cleaned_data = super().clean()
        if not self._start_date_not_after_end_date(cleaned_data):
            raise ValidationError(
                "The course start date must not be after the end date!",
                code="invalid_date_range"
            )

    def _start_date_not_after_end_date(self, cleaned_data):
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date:
            return start_date <= end_date
        return True


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


class JoinCourseForm(ModelForm):
    class Meta:
        model = Course
        fields = []

    join = BooleanField(initial=True, widget=HiddenInput())

    def __init__(self, student, student_join_code, *args, **kwargs):
        self._student = student
        self._student_join_code = student_join_code
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.enroll_student_with_join_code(self._student, self._student_join_code)
        return self.instance
