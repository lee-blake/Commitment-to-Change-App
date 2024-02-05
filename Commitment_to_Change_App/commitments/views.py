from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView


from commitments.business_logic import write_course_commitments_as_csv, \
    write_aggregate_course_statistics_as_csv
from commitments.enums import CommitmentStatus
from commitments.forms import CommitmentForm, CourseForm, CommitmentTemplateForm, \
    CourseSelectSuggestedCommitmentsForm, GenericDeletePostKeySetForm, CompleteCommitmentForm, \
    DiscontinueCommitmentForm, ReopenCommitmentForm, JoinCourseForm, \
    CreateCommitmentFromSuggestedCommitmentForm
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
        else:
            return ["commitments/Commitment/commitment_view_unowned_page.html"]

    def get_object(self, queryset=None):
        commitment = super().get_object(queryset=queryset)
        commitment.save_expired_if_past_deadline()
        return commitment


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


class CompleteCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        viewer = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=viewer)
        form = CompleteCommitmentForm(request.POST, instance=commitment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("clinician dashboard"))
        else:
            return HttpResponseBadRequest(
                "'complete' key must be nonempty to complete a commitment"
            )


class DiscontinueCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        viewer = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=viewer)
        form = DiscontinueCommitmentForm(request.POST, instance=commitment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("clinician dashboard"))
        else:
            return HttpResponseBadRequest(
                "'discontinue' key must be nonempty to discontinue a commitment"
            )


class ReopenCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        viewer = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=viewer)
        form = ReopenCommitmentForm(request.POST, instance=commitment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("clinician dashboard"))
        else:
            return HttpResponseBadRequest(
                "'reopen' key must be nonempty to reopen a commitment"
            )


class CreateCourseView(ProviderLoginRequiredMixin, CreateView):
    form_class = CourseForm
    template_name = "commitments/Course/course_create_page.html"

    def form_valid(self, form):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        form.instance.owner = viewer
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "view Course",
            kwargs={"course_id": self.object.id}
        )


class ViewCourseView(LoginRequiredMixin, DetailView):
    model = Course
    pk_url_kwarg = "course_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Enrich the course object with its statistics
        course = context["course"]
        course.enrich_with_statistics()
        return context

    def get_template_names(self):
        if self.request.user.is_authenticated and self.request.user == self.object.owner.user:
            return ["commitments/Course/course_view_owned_page.html"]
        else:
            # The viewer must be a student or we should 404 for plausibile deniability of
            # the existence of the course. Filtering the students for the user works in one line.
            get_object_or_404(self.object.students, user=self.request.user)
            return ["commitments/Course/course_view_unowned_page.html"]


class EditCourseView(ProviderLoginRequiredMixin, UpdateView):
    form_class = CourseForm
    template_name = "commitments/Course/course_edit_page.html"
    pk_url_kwarg = "course_id"

    def get_queryset(self):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        return Course.objects.filter(
            owner=viewer
        )

    def get_success_url(self):
        return reverse(
            "view Course",
            kwargs={"course_id": self.object.id}
        )


class JoinCourseView(LoginRequiredMixin, UpdateView):
    template_name = "commitments/Course/course_student_join_page.html"
    pk_url_kwarg = "course_id"

    def get_queryset(self):
        return Course.objects.filter(join_code=self.kwargs["join_code"])

    def get_form(self, form_class=None):
        viewer = get_object_or_404(ClinicianProfile, user=self.request.user)
        return JoinCourseForm(
            viewer,
            self.kwargs["join_code"],
            **self.get_form_kwargs()
        )

    def get_success_url(self):
        return reverse(
            "view Course",
            kwargs={"course_id": self.object.id}
        )

    # We must override the get and post methods to allow the course owner to view the
    # landing page without getting a 403. It is simple enough to be worth it.
    def get(self, *args, **kwargs):
        if self.request.user == Course.objects.get(id=kwargs["course_id"]).owner.user:
            return render(
                self.request,
                "commitments/Course/course_owner_join_page.html",
                {"course": self.get_object()}
            )
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if not self.request.user.is_clinician:
            raise PermissionDenied("Providers cannot join courses.")
        return super().post(*args, **kwargs)


class CourseChangeSuggestedCommitmentsView(ProviderLoginRequiredMixin, UpdateView):
    form_class = CourseSelectSuggestedCommitmentsForm
    template_name = "commitments/Course/course_change_suggested_commitments.html"
    pk_url_kwarg = "course_id"

    def get_queryset(self):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        return Course.objects.filter(
            owner=viewer
        )

    def get_success_url(self):
        return reverse(
            "view Course",
            kwargs={"course_id": self.object.id}
        )


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


class DownloadCourseCommitmentsCSVView(
    ProviderLoginRequiredMixin, GeneratedTemporaryTextFileDownloadView
):
    filename = "course_commitments.csv"

    def write_text_to_file(self, temporary_file):
        course_id = self.kwargs["course_id"]
        viewer = ProviderProfile.objects.get(user=self.request.user)
        course = get_object_or_404(Course, id=course_id, owner=viewer)
        write_course_commitments_as_csv(course, temporary_file)


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
