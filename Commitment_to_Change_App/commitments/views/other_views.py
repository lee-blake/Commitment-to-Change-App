from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.base import View, TemplateView

from commitments.business_logic import write_aggregate_course_statistics_as_csv
from commitments.enums import CommitmentStatus
from commitments.generic_views import GeneratedTemporaryTextFileDownloadView
from commitments.mixins import ClinicianLoginRequiredMixin, ProviderLoginRequiredMixin
from commitments.models import Commitment, ClinicianProfile, ProviderProfile, Course, \
    CommitmentTemplate


class DashboardRedirectingView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_clinician:
            return HttpResponseRedirect("/app/dashboard/clinician/")
        elif request.user.is_provider:
            return HttpResponseRedirect("/app/dashboard/provider/")
        else:
            return HttpResponseServerError(
                "This user is neither a clinician nor a provider and therefore no dashboard exists!"
            )


class ClinicianDashboardView(ClinicianLoginRequiredMixin, TemplateView):
    template_name = "commitments/dashboard/clinician/dashboard_clinician_page.html"

    def get_context_data(self, **kwargs):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        commitments = Commitment.objects.filter(owner=viewer)
        # We need to auto-expire them to make sure they are grouped correctly.
        for commitment in commitments:
            commitment.save_expired_if_past_deadline()
        context = super().get_context_data(**kwargs)
        context["enrolled_courses"] = viewer.course_set.all()
        context["commitments"] = {
            "in_progress": commitments.filter(status=CommitmentStatus.IN_PROGRESS),
            "completed": commitments.filter(status=CommitmentStatus.COMPLETE),
            "expired": commitments.filter(status=CommitmentStatus.EXPIRED),
            "discontinued": commitments.filter(status=CommitmentStatus.DISCONTINUED)
        }
        return context


class ProviderDashboardView(ProviderLoginRequiredMixin, TemplateView):
    template_name = "commitments/dashboard/provider/dashboard_provider_page.html"

    def get_context_data(self, **kwargs):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        context = super().get_context_data(**kwargs)
        context["courses"] = Course.objects.filter(owner=viewer)
        context["commitment_templates"] = CommitmentTemplate.objects.filter(owner=viewer)
        return context


class AggregateCourseStatisticsCSVDownloadView(
    ProviderLoginRequiredMixin, GeneratedTemporaryTextFileDownloadView
):
    filename = "course_statistics.csv"

    def write_text_to_file(self, temporary_file):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        courses = Course.objects.filter(owner=viewer).all()
        write_aggregate_course_statistics_as_csv(courses, temporary_file)
