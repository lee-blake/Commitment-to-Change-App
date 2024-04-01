from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.edit import CreateView, DeleteView, FormView
from django.views.generic.list import ListView

from commitments.forms import CommitmentReminderEmailForm, GenericDeletePostKeySetForm, \
    ClearCommitmentReminderEmailsForm, RecurringReminderEmailForm
from commitments.mixins import ClinicianLoginRequiredMixin
from commitments.models import Commitment, ClinicianProfile, CommitmentReminderEmail


class CreateCommitmentReminderEmailView(ClinicianLoginRequiredMixin, CreateView):
    template_name = "commitments/CommitmentReminderEmail/create_reminder_email.html"

    def get_form(self, form_class=None):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        source_commitment = get_object_or_404(
            Commitment,
            id=self.kwargs["commitment_id"],
            owner=viewer
        )
        return CommitmentReminderEmailForm(
            commitment=source_commitment,
            **self.get_form_kwargs()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commitment"] = context["form"].instance.commitment
        return context

    def get_success_url(self):
        return reverse(
            "view CommitmentReminderEmails",
            kwargs={"commitment_id": self.kwargs["commitment_id"]}
        )


class ViewCommitmentReminderEmailsView(ClinicianLoginRequiredMixin, ListView):
    template_name = "commitments/CommitmentReminderEmail/view_reminder_emails.html"
    context_object_name = "reminder_emails"

    def get_queryset(self):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        source_commitment = get_object_or_404(
            Commitment,
            id=self.kwargs["commitment_id"],
            owner=viewer
        )
        return CommitmentReminderEmail.objects.filter(commitment=source_commitment)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commitment"] = get_object_or_404(Commitment, id=self.kwargs["commitment_id"])
        return context


class DeleteCommitmentReminderEmailView(ClinicianLoginRequiredMixin, DeleteView):
    model = CommitmentReminderEmail
    form_class = GenericDeletePostKeySetForm
    template_name = "commitments/CommitmentReminderEmail/delete_reminder_email.html"
    pk_url_kwarg = "reminder_email_id"
    context_object_name = "reminder_email"

    def get_queryset(self):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        source_commitment = get_object_or_404(
            Commitment,
            id=self.kwargs["commitment_id"],
            owner=viewer
        )
        return CommitmentReminderEmail.objects.filter(commitment=source_commitment)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commitment"] = get_object_or_404(Commitment, id=self.kwargs["commitment_id"])
        return context

    def get_success_url(self, **kwargs):
        return reverse(
            "view CommitmentReminderEmails",
            kwargs={"commitment_id": self.kwargs["commitment_id"]}
        )


class ClearCommitmentReminderEmailsView(ClinicianLoginRequiredMixin, FormView):
    template_name = "commitments/CommitmentReminderEmail/clear_reminder_emails.html"

    def get_object(self):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        return get_object_or_404(
            Commitment,
            id=self.kwargs["commitment_id"],
            owner=viewer
        )

    def get_form(self, form_class=None):
        return ClearCommitmentReminderEmailsForm(
            self.get_object(), **self.get_form_kwargs()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commitment"] = self.get_object()
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse(
            "view CommitmentReminderEmails",
            kwargs={"commitment_id": self.kwargs["commitment_id"]}
        )


class CreateRecurringReminderEmailView(ClinicianLoginRequiredMixin, CreateView):
    template_name = "commitments/CommitmentReminderEmail/create_recurring_reminder_email.html"

    def get_form(self, form_class=None):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        source_commitment = get_object_or_404(
            Commitment,
            id=self.kwargs["commitment_id"],
            owner=viewer
        )
        return RecurringReminderEmailForm(
            commitment=source_commitment,
            **self.get_form_kwargs()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commitment"] = context["form"].instance.commitment
        return context

    def get_success_url(self):
        return reverse(
            "view CommitmentReminderEmails",
            kwargs={"commitment_id": self.kwargs["commitment_id"]}
        )
