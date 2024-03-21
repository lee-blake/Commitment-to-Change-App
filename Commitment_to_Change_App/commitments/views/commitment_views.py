from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from commitments.forms import CommitmentForm, GenericDeletePostKeySetForm, \
    CompleteCommitmentForm, DiscontinueCommitmentForm, ReopenCommitmentForm, \
    CreateCommitmentFromSuggestedCommitmentForm, ClearCommitmentReminderEmailsForm
from commitments.mixins import ClinicianLoginRequiredMixin
from commitments.models import Commitment, ClinicianProfile, Course


class CreateCommitmentView(ClinicianLoginRequiredMixin, CreateView):
    form_class = CommitmentForm
    template_name = "commitments/Commitment/make_commitment.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        kwargs.update({ "owner": viewer })
        return kwargs

    def get_success_url(self):
        return reverse(
            "view Commitment",
            kwargs={"commitment_id": self.object.id}
        )


class ViewCommitmentView(DetailView):
    model = Commitment
    pk_url_kwarg = "commitment_id"

    def get_template_names(self):
        if self.request.user.is_authenticated and self.request.user == self.object.owner.user:
            return ["commitments/Commitment/commitment_view_owned_page.html"]
        return ["commitments/Commitment/commitment_view_unowned_page.html"]


class EditCommitmentView(ClinicianLoginRequiredMixin, UpdateView):
    form_class = CommitmentForm
    template_name = "commitments/Commitment/commitment_edit_page.html"
    pk_url_kwarg = "commitment_id"

    def get_queryset(self):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        return Commitment.objects.filter(
            owner=viewer
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        kwargs.update({"owner": viewer})
        return kwargs

    def get_success_url(self):
        return reverse(
            "view Commitment",
            kwargs={"commitment_id": self.object.id}
        )


class DeleteCommitmentView(ClinicianLoginRequiredMixin, DeleteView):
    model = Commitment
    form_class = GenericDeletePostKeySetForm
    template_name = "commitments/Commitment/commitment_delete_page.html"
    pk_url_kwarg = "commitment_id"
    context_object_name = "commitment"
    success_url = reverse_lazy("clinician dashboard")

    def get_queryset(self):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        return Commitment.objects.filter(
            owner=viewer
        )


class CreateFromSuggestedCommitmentView(ClinicianLoginRequiredMixin, CreateView):
    template_name = "commitments/Commitment/commitment_create_from_suggested_commitment.html"

    def get_form(self, form_class=None):
        source_course = get_object_or_404(Course, id=self.kwargs["course_id"])
        suggested_commitment_template = get_object_or_404(
            source_course.suggested_commitments,
            id=self.kwargs["commitment_template_id"]
        )
        # The viewer must be a student or we should 404 for plausibile deniability of
        # the existence of the course. Filtering the students for the user works and gets
        # us the owner at the same time.
        student_viewer = get_object_or_404(source_course.students, user=self.request.user)
        return CreateCommitmentFromSuggestedCommitmentForm(
            suggested_commitment_template,
            source_course,
            owner=student_viewer,
            **self.get_form_kwargs()
        )

    def get_success_url(self):
        return reverse(
            "view Commitment",
            kwargs={"commitment_id": self.object.id}
        )


class CompleteCommitmentView(ClinicianLoginRequiredMixin, UpdateView):
    http_method_names = ["post"]
    form_class = CompleteCommitmentForm
    template_name = "commitments/Commitment/commitment_edit_page.html"
    pk_url_kwarg = "commitment_id"

    def get_queryset(self):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        return Commitment.objects.filter(
            owner=viewer
        )

    def form_valid(self, form):
        # We also must clear the reminder emails when the status is changed to something inactive.
        ClearCommitmentReminderEmailsForm(self.object).save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return HttpResponseBadRequest(
            "'complete' key must be nonempty to complete a commitment"
        )

    def get_success_url(self):
        return reverse("clinician dashboard")


class DiscontinueCommitmentView(ClinicianLoginRequiredMixin, UpdateView):
    http_method_names = ["post"]
    form_class = DiscontinueCommitmentForm
    pk_url_kwarg = "commitment_id"

    def get_queryset(self):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        return Commitment.objects.filter(
            owner=viewer
        )

    def form_valid(self, form):
        # We also must clear the reminder emails when the status is changed to something inactive.
        ClearCommitmentReminderEmailsForm(self.object).save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return HttpResponseBadRequest(
            "'discontinue' key must be nonempty to discontinue a commitment"
        )

    def get_success_url(self):
        return reverse("clinician dashboard")


class ReopenCommitmentView(ClinicianLoginRequiredMixin, UpdateView):
    http_method_names = ["post"]
    form_class = ReopenCommitmentForm
    pk_url_kwarg = "commitment_id"

    def get_queryset(self):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        return Commitment.objects.filter(
            owner=viewer
        )

    def form_invalid(self, form):
        return HttpResponseBadRequest(
            "'reopen' key must be nonempty to reopen a commitment"
        )

    def get_success_url(self):
        return reverse("clinician dashboard")
    