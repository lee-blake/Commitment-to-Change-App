from django.forms import ModelForm, DateInput, ModelChoiceField, \
    BooleanField, HiddenInput

from commitments.models import Commitment, Course


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

    def _set_owner_enrolled_courses_as_associated_course_options(self, owner):
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
