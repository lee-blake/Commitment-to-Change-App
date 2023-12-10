from django.core.exceptions import ValidationError
from django.forms import ModelForm, DateInput, ModelChoiceField, CheckboxSelectMultiple, \
    ModelMultipleChoiceField, BooleanField, Form, HiddenInput

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
        owner = kwargs.pop("owner")
        super(ModelForm, self).__init__(*args, **kwargs)
        if not hasattr(self.instance, 'owner') or not self.instance.owner:
            self.instance.owner = owner
        elif owner != self.instance.owner:
            raise ValueError("Cannot change the owner of a commitment!")
        self.fields['associated_course'].queryset = self.instance.owner.course_set.all()
        self._disable_editing_if_suggested_commitment()

    def _disable_editing_if_suggested_commitment(self):
        if self.instance.source_template:
            self.fields["title"].disabled = True
            self.fields["description"].disabled = True
            self.fields["associated_course"].disabled = True


class CreateCommitmentFromSuggestedCommitmentForm(CommitmentForm):
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


class GenericDeletePostKeySetForm(Form):
    delete = BooleanField(initial=True, widget=HiddenInput())


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
