from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from commitments.forms import ClinicianProfileForm
from commitments.mixins import ClinicianLoginRequiredMixin, ProviderLoginRequiredMixin
from commitments.models import ClinicianProfile, ProviderProfile


class ProfileRedirectingView(LoginRequiredMixin, RedirectView):
    http_method_names = ["get"]

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_clinician:
            return reverse("view ClinicianProfile")
        if self.request.user.is_provider:
            return reverse("view ProviderProfile")
        raise ObjectDoesNotExist(
            "This user is neither a clinician nor a provider and therefore no profile exists!"
        )


class ViewClinicianProfileView(ClinicianLoginRequiredMixin, DetailView):
    template_name = "commitments/Profile/view_clinician_profile.html"
    context_object_name = "clinician_profile"

    def get_object(self, queryset=None):
        return ClinicianProfile.objects.get(user=self.request.user)


class EditClinicianProfileView(ClinicianLoginRequiredMixin, UpdateView):
    form_class = ClinicianProfileForm
    template_name = "commitments/Profile/edit_clinician_profile.html"
    context_object_name = "clinician_profile"
    success_url = reverse_lazy("view ClinicianProfile")

    def get_object(self, queryset=None):
        return ClinicianProfile.objects.get(user=self.request.user)


class ViewProviderProfileView(ProviderLoginRequiredMixin, DetailView):
    template_name = "commitments/Profile/view_provider_profile.html"
    context_object_name = "provider_profile"

    def get_object(self, queryset=None):
        return ProviderProfile.objects.get(user=self.request.user)
