from django.views.generic.detail import DetailView

from commitments.mixins import ClinicianLoginRequiredMixin, ProviderLoginRequiredMixin
from commitments.models import ClinicianProfile, ProviderProfile


class ViewClinicianProfileView(ClinicianLoginRequiredMixin, DetailView):
    template_name = "commitments/Profile/view_clinician_profile.html"
    context_object_name = "clinician_profile"

    def get_object(self, queryset=None):
        return ClinicianProfile.objects.get(user=self.request.user)


class ViewProviderProfileView(ProviderLoginRequiredMixin, DetailView):
    template_name = "commitments/Profile/view_provider_profile.html"
    context_object_name = "provider_profile"

    def get_object(self, queryset=None):
        return ProviderProfile.objects.get(user=self.request.user)
