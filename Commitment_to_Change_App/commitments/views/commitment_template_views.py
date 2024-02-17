from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from commitments.forms import CommitmentTemplateForm, GenericDeletePostKeySetForm
from commitments.mixins import ProviderLoginRequiredMixin
from commitments.models import ProviderProfile, CommitmentTemplate


class CreateCommitmentTemplateView(ProviderLoginRequiredMixin, CreateView):
    form_class = CommitmentTemplateForm
    template_name = "commitments/CommitmentTemplate/commitment_template_create_page.html"

    def form_valid(self, form):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        form.instance.owner = viewer
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "view CommitmentTemplate",
            kwargs={"commitment_template_id": self.object.id}
        )


class ViewCommitmentTemplateView(ProviderLoginRequiredMixin, DetailView):
    model = CommitmentTemplate
    template_name = "commitments/CommitmentTemplate/commitment_template_view_page.html"
    pk_url_kwarg = "commitment_template_id"
    context_object_name = "commitment_template"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commitment_template = context["commitment_template"]
        commitment_template.enrich_with_statistics()
        return context

    def get_queryset(self):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        return CommitmentTemplate.objects.filter(
            owner=viewer
        )


class EditCommitmentTemplateView(ProviderLoginRequiredMixin, UpdateView):
    form_class = CommitmentTemplateForm
    template_name = "commitments/CommitmentTemplate/commitment_template_edit_page.html"
    pk_url_kwarg = "commitment_template_id"
    context_object_name = "commitment_template"

    def get_queryset(self):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        return CommitmentTemplate.objects.filter(
            owner=viewer
        )

    def get_success_url(self):
        return reverse(
            "view CommitmentTemplate",
            kwargs={"commitment_template_id": self.object.id}
        )


class DeleteCommitmentTemplateView(ProviderLoginRequiredMixin, DeleteView):
    model = CommitmentTemplate
    form_class = GenericDeletePostKeySetForm
    template_name = "commitments/CommitmentTemplate/commitment_template_delete_page.html"
    pk_url_kwarg = "commitment_template_id"
    context_object_name = "commitment_template"
    success_url = reverse_lazy("provider dashboard")

    def get_queryset(self):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        return CommitmentTemplate.objects.filter(
            owner=viewer
        )
