from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, \
    HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy

from commitments.enums import CommitmentStatus
from .forms import CommitmentForm, CourseForm, CommitmentTemplateForm, \
    CourseSelectSuggestedCommitmentsForm, GenericDeletePostKeySetForm, CompleteCommitmentForm, \
    DiscontinueCommitmentForm, ReopenCommitmentForm, CreateCommitmentFromSuggestedCommitmentForm
from .mixins import ClinicianLoginRequiredMixin, ProviderLoginRequiredMixin
from .models import Commitment, ClinicianProfile, ProviderProfile, Course, CommitmentTemplate


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


class ClinicianDashboardView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitments = Commitment.objects.filter(owner=profile)
        for commitment in commitments:
            commitment.save_expired_if_past_deadline()

        in_progress = list(filter(lambda x: x.status == 0, commitments))
        completed = list(filter(lambda x: x.status == 1, commitments))
        expired = list(filter(lambda x: x.status == 2, commitments))
        discontinued = list(filter(lambda x: x.status == 3, commitments))

        enrolled_courses = profile.course_set.all()

        context = {
            'in_progress_commitments': in_progress,
            'expired_commitments': expired,
            'completed_commitments': completed,
            'discontinued_commitments': discontinued,
            'enrolled_courses': enrolled_courses
        }

        return render(request, "commitments/dashboard/clinician/dashboard_clinician_page.html", context)


class ProviderDashboardView(ProviderLoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        profile = ProviderProfile.objects.get(user=request.user)
        courses = Course.objects.filter(owner=profile)
        commitment_templates = CommitmentTemplate.objects.filter(owner=profile)
        return render(
            request,
            "commitments/dashboard/provider/dashboard_provider_page.html", 
            {
                "courses": courses,
                "commitment_templates": commitment_templates
            }
        )


class MakeCommitmentView(ClinicianLoginRequiredMixin, CreateView):
    form_class = CommitmentForm
    template_name = "commitments/Commitment/make_commitment.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile = ClinicianProfile.objects.get(user=self.request.user)
        kwargs.update({ "owner": profile })
        return kwargs

    def get_success_url(self):
        return reverse(
            "view commitment",
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
            "view commitment",
            kwargs={"commitment_id": self.object.id}
        )


class CompleteCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
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
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
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
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
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
            "view course",
            kwargs={"course_id": self.object.id}
        )


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
            "view course",
            kwargs={"course_id": self.object.id}
        )


class ViewCourseView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, course_id):
        course = get_object_or_404(Course, id=course_id)
        associated_commitments = Commitment.objects.filter(associated_course=course)
        context = {
            "course": course,
            "associated_commitments": associated_commitments
        }
        if request.user.is_provider and \
                course.owner == ProviderProfile.objects.get(user=request.user):
            return render(request, "commitments/Course/course_view_owned_page.html", context)
        elif request.user.is_clinician and course.students.contains(
            ClinicianProfile.objects.get(user=request.user)
        ):
            return render(
                request, "commitments/Course/course_view_unowned_page.html", context)
        else:
            return HttpResponseNotFound("<h1>404</h1")


class JoinCourseView(LoginRequiredMixin, View):

    @staticmethod
    def get(request, course_id, join_code):
        course = get_object_or_404(Course, id=course_id, join_code=join_code)
        if request.user.is_provider:
            profile = ProviderProfile.objects.get(user=request.user)
            if not course.owner == profile:
                raise PermissionDenied("Providers cannot join courses.")
            return render(
                request,
                "commitments/Course/course_owner_join_page.html",
                context={"course": course}
            )
        return render(
            request,
            "commitments/Course/course_student_join_page.html",
            context={"course": course}
        )

    @staticmethod
    def post(request, course_id, join_code):
        if not request.user.is_clinician:
            raise PermissionDenied("Providers cannot join courses.")
        if request.POST.get("join") == "true":
            course = get_object_or_404(Course, id=course_id, join_code=join_code)
            profile = ClinicianProfile.objects.get(user=request.user)
            if not course.students.contains(profile):
                course.students.add(profile)
            return HttpResponseRedirect(
                reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
            )
        else:
            return JoinCourseView.get(request, course_id, join_code)


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

    def get_queryset(self):
        viewer = ProviderProfile.objects.get(user=self.request.user)
        return CommitmentTemplate.objects.filter(
            owner=viewer
        )


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
            "view course",
            kwargs={"course_id": self.object.id}
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
            "view commitment",
            kwargs={"commitment_id": self.object.id}
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
