from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from commitments.business_logic import write_course_commitments_as_csv
from commitments.forms import CommitmentTemplateForm, CourseForm, \
    CourseSelectSuggestedCommitmentsForm, JoinCourseForm
from commitments.generic_views import GeneratedTemporaryTextFileDownloadView
from commitments.mixins import ProviderLoginRequiredMixin
from commitments.models import ClinicianProfile, ProviderProfile, Course


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
        context["suggested_commitments"] = course.suggested_commitments_list
        for suggested_commitment in context["suggested_commitments"]:
            suggested_commitment.enrich_with_course_specific_statistics(course)
        return context

    def get_template_names(self):
        if self.request.user.is_authenticated and self.request.user == self.object.owner.user:
            return ["commitments/Course/course_view_owned_page.html"]
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This is necessary to enable creating CommitmentTemplates with AJAX.
        # None of the actual logic is handled by this view, it just supplies the
        # fields that would be used by the logic view to avoid duplication.
        context['CommitmentTemplateForm'] = CommitmentTemplateForm
        return context


class DownloadCourseCommitmentsCSVView(
    ProviderLoginRequiredMixin, GeneratedTemporaryTextFileDownloadView
):
    filename = "course_commitments.csv"

    def write_text_to_file(self, temporary_file):
        course_id = self.kwargs["course_id"]
        viewer = ProviderProfile.objects.get(user=self.request.user)
        course = get_object_or_404(Course, id=course_id, owner=viewer)
        write_course_commitments_as_csv(course, temporary_file)
