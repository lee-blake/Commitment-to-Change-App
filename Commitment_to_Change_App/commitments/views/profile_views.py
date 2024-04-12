from django.views.generic.detail import DetailView

from commitments.mixins import ClinicianLoginRequiredMixin
from commitments.models import ClinicianProfile


class ViewClinicianProfileView(ClinicianLoginRequiredMixin, DetailView):
    template_name = "commitments/Profile/view_clinician_profile.html"
    context_object_name = "clinician_profile"

    def get_object(self, queryset=None):
        return ClinicianProfile.objects.get(user=self.request.user)
