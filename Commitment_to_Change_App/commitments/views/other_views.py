import itertools

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.generic.base import RedirectView, TemplateView

from commitments.business_logic import write_aggregate_course_statistics_as_csv, \
    write_aggregate_commitment_template_statistics_as_csv, CommitmentStatusStatistics
from commitments.enums import CommitmentStatus
from commitments.generic_views import GeneratedTemporaryTextFileDownloadView
from commitments.mixins import ClinicianLoginRequiredMixin, ProviderLoginRequiredMixin
from commitments.models import Commitment, ClinicianProfile, ProviderProfile, Course, \
    CommitmentTemplate


class DashboardRedirectingView(LoginRequiredMixin, RedirectView):
    http_method_names = ["get"]

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_clinician:
            return reverse("clinician dashboard")
        if self.request.user.is_provider:
            return reverse("provider dashboard")
        raise ObjectDoesNotExist(
            "This user is neither a clinician nor a provider and therefore no dashboard exists!"
        )


class ClinicianDashboardView(ClinicianLoginRequiredMixin, TemplateView):
    template_name = "commitments/dashboard/clinician/dashboard_clinician_page.html"

    def get_context_data(self, **kwargs):
        viewer = ClinicianProfile.objects.get(user=self.request.user)
        commitments = Commitment.objects.filter(owner=viewer)
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


class AggregateCommitmentTemplateStatisticsCSVDownloadView(
    ProviderLoginRequiredMixin, GeneratedTemporaryTextFileDownloadView
):
    filename = "commitment_template_statistics.csv"

    def write_text_to_file(self, temporary_file):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        commitment_templates = CommitmentTemplate.objects.filter(owner=viewer).all()
        write_aggregate_commitment_template_statistics_as_csv(commitment_templates, temporary_file)


class StatisticsOverviewView(ProviderLoginRequiredMixin, TemplateView):
    template_name = "commitments/statistics/statistics_overview_page.html"

    def get_context_data(self, **kwargs):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        context = super().get_context_data(**kwargs)
        context["courses"] = Course.objects.filter(owner=viewer)
        context["overall_course_stats"] = CommitmentStatusStatistics(
            # This is effectively the same as aggregating into one list and unpacking.
            *itertools.chain.from_iterable(
                course.associated_commitments_list for course in context["courses"]
            )
        ).as_json()
        for course in context["courses"]:
            course.enrich_with_statistics()
        context["commitment_templates"] = CommitmentTemplate.objects.filter(owner=viewer)
        for commitment_template in context["commitment_templates"]:
            commitment_template.enrich_with_statistics()
        return context
