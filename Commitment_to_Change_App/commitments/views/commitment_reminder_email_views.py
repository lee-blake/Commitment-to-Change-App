from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from commitments.forms import CommitmentReminderEmailForm
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
