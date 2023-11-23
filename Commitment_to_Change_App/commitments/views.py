import datetime
import random
import string

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed, \
    HttpResponseServerError, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View
from django.urls import reverse

import cme_accounts.forms
import cme_accounts.models

from .forms import CommitmentForm, DeleteCommitmentForm, CourseForm, CommitmentTemplateForm, \
    CourseSelectSuggestedCommitmentsForm
from .mixins import ClinicianLoginRequiredMixin, ProviderLoginRequiredMixin
from .models import Commitment, ClinicianProfile, ProviderProfile, Course, CommitmentTemplate


def commitment_remaining_time(request, commitment_id):
    commitment = get_object_or_404(Commitment, id=commitment_id)
    commitment.show = commitment.deadline
    context = {"commitment": commitment}
    if commitment.deadline > datetime.date.today():
        return render(request, "commitments/view_commitment.html", context)
    else:
        commitment.status = Commitment.CommitmentStatus.EXPIRED


def view_commitment(request, commitment_id):
    commitment = get_object_or_404(Commitment, id=commitment_id)
    commitment.save_expired_if_past_deadline()
    context = {"commitment": commitment}
    if request.user.is_authenticated and request.user == commitment.owner.user:
        return render(request, "commitments/view_owned_commitment.html", context)
    else:
        return render(request, "commitments/view_commitment.html", context)


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

        return render(request, "commitments/dashboard_clinician.html", context)


class ProviderDashboardView(ProviderLoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        profile = ProviderProfile.objects.get(user=request.user)
        courses = Course.objects.filter(owner=profile)
        commitment_templates = CommitmentTemplate.objects.filter(owner=profile)
        return render(
            request,
            "commitments/dashboard_provider.html", 
            {
                "courses": courses,
                "commitment_templates": commitment_templates
            }
        )


class MakeCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        profile = ClinicianProfile.objects.get(user=request.user)
        form = CommitmentForm(profile=profile)
        return render(request, "commitments/make_commitment.html", context={"form": form})

    @staticmethod
    def post(request, *args, **kwargs):
        profile = ClinicianProfile.objects.get(user=request.user)
        form = CommitmentForm(request.POST, profile=profile)
        if form.is_valid():
            form.instance.owner = profile
            form.instance.status = Commitment.CommitmentStatus.IN_PROGRESS
            commitment = form.save()
            return HttpResponseRedirect(
                reverse(
                    "view commitment",
                    kwargs={"commitment_id": commitment.id}
                )
            )
        else:
            return render(request, "commitments/make_commitment.html", context={"form": form})


class DeleteCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def get(request, commitment_id):
        commitment = get_object_or_404(Commitment, id=commitment_id)
        form = DeleteCommitmentForm(instance=commitment)
        return render(
            request,
            "commitments/delete_commitment.html",
            context={
                "commitment": commitment,
                "form": form})

    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        if request.POST.get("delete") == "true":
            commitment.delete()
            return HttpResponseRedirect("/app/dashboard")
        else:
            return HttpResponseBadRequest("'delete' key must be set 'true' to be deleted")


class EditCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def get(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        commitment.save_expired_if_past_deadline()
        form = CommitmentForm(instance=commitment, profile=profile)
        return render(
            request,
            "commitments/edit_commitment.html",
            context={
                "commitment": commitment,
                "form": form
            }
        )

    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        commitment.save_expired_if_past_deadline()
        form = CommitmentForm(request.POST, instance=commitment, profile=profile)
        if form.is_valid():
            commitment = form.save()
            return HttpResponseRedirect(
                reverse(
                    "view commitment",
                    kwargs={"commitment_id": commitment.id}
                )
            )
        else:
            return render(
                request,
                "commitments/edit_commitment.html",
                context={
                    "commitment": commitment,
                    "form": form
                }
            )


class CompleteCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        if request.POST.get("complete") == "true":
            commitment.mark_complete()
            commitment.save()
            return HttpResponseRedirect(
                reverse(
                    "view commitment",
                    kwargs={"commitment_id": commitment.id}
                )
            )
        else:
            return HttpResponseBadRequest(
                "'complete' key must be set to 'true' to complete a commitment"
            )


class DiscontinueCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        if request.POST.get("discontinue") == "true":
            commitment.mark_discontinued()
            commitment.save()
            return HttpResponseRedirect(
                reverse(
                    "view commitment",
                    kwargs={"commitment_id": commitment.id}
                )
            )
        else:
            return HttpResponseBadRequest(
                "'discontinue' key must be set to 'true' to discontinue a commitment"
            )

    @staticmethod
    def get(request):
        return HttpResponseNotAllowed(['POST'])


class ReopenCommitmentView(ClinicianLoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        if request.POST.get("reopen") == "true":
            commitment.reopen()
            commitment.save()
            return HttpResponseRedirect(
                reverse(
                    "view commitment",
                    kwargs={"commitment_id": commitment.id}
                )
            )
        else:
            return HttpResponseBadRequest(
                "'reopen' key must be set to 'true' to reopen a commitment"
            )

    @staticmethod
    def get(request):
        return HttpResponseNotAllowed(['POST'])


class RegisterTypeChoiceView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        return render(request, "commitments/register_choice.html")


class RegisterClinicianView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "commitments/must_log_out.html")
        form = cme_accounts.forms.CustomUserCreationForm()
        return render(request, "commitments/register_clinician.html", context={"form": form})

    @staticmethod
    def post(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "commitments/must_log_out.html")
        form = cme_accounts.forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.instance.is_clinician = True
            user = form.save()
            ClinicianProfile.objects.create(user=user)
            return render(request, "commitments/register_successful.html")
        else:
            return render(request, "commitments/register_clinician.html", context={"form": form})


class RegisterProviderView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "commitments/must_log_out.html")
        form = cme_accounts.forms.CustomUserCreationForm()
        return render(request, "commitments/register_provider.html", context={"form": form})

    @staticmethod
    def post(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "commitments/must_log_out.html")
        form = cme_accounts.forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.instance.is_provider = True
            user = form.save()
            ProviderProfile.objects.create(user=user)
            return render(request, "commitments/register_successful.html")
        else:
            return render(request, "commitments/register_provider.html", context={"form": form})


class CreateCourseView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        form = CourseForm()
        return render(request, "commitments/create_course.html", context={"form": form})

    @staticmethod
    def post(request, *args, **kwargs):
        form = CourseForm(request.POST)
        if form.is_valid():
            form.instance.owner = ProviderProfile.objects.get(user=request.user)
            form.instance.join_code = CreateCourseView.generate_random_join_code(8)
            course = form.save()
            return HttpResponseRedirect(
                reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
            )
        else:
            return render(request, "commitments/create_course.html", context={"form": form})

    @staticmethod
    def generate_random_join_code(length):
        return ''.join(random.choice(string.ascii_uppercase) for i in range(0, length))


class EditCourseView(ProviderLoginRequiredMixin, View):
    @staticmethod
    def get(request, course_id):
        profile = ProviderProfile.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, owner=profile)
        form = CourseForm(instance=course)
        return render(
            request,
            "commitments/edit_course.html", 
            context= {
                "course": course,
                "form": form
            }
        )

    @staticmethod
    def post(request, course_id):
        profile = ProviderProfile.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, owner=profile)
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            return HttpResponseRedirect(
                reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
            )
        else:
            return render(
                request,
                "commitments/edit_course.html", 
                context= {
                    "course": course,
                    "form": form
                }
            )


class ViewCourseView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, course_id):
        course = get_object_or_404(Course, id=course_id)
        associated_commitments = Commitment.objects.filter(associated_course=course)
        total = 0
        in_progress = 0
        complete = 0
        past_due = 0
        discontinued = 0
        for commitment in associated_commitments:
            total += 1
            match commitment.status:
                case Commitment.CommitmentStatus.IN_PROGRESS:
                    in_progress += 1
                case Commitment.CommitmentStatus.COMPLETE:
                    complete += 1
                case Commitment.CommitmentStatus.EXPIRED:
                    past_due += 1
                case Commitment.CommitmentStatus.DISCONTINUED:
                    discontinued += 1

        context = {
            "course": course,
            "associated_commitments": associated_commitments,
            "status_breakdown": {
                "total": total,
                "in_progress": in_progress,
                "complete": complete,
                "past_due": past_due,
                "discontinued": discontinued
            }
        }
        if request.user.is_provider and \
                course.owner == ProviderProfile.objects.get(user=request.user):
            return render(request, "commitments/view_owned_course.html", context)
        elif request.user.is_clinician and course.students.contains(
            ClinicianProfile.objects.get(user=request.user)
        ):
            return render(
                request, "commitments/view_course.html", context)
        else:
            return HttpResponseNotFound("<h1>404</h1")


class JoinCourseView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, course_id, join_code):
        course = get_object_or_404(Course, id=course_id, join_code=join_code)
        if request.user.is_clinician:
            profile = ClinicianProfile.objects.get(user=request.user)
            if not course.students.contains(profile):
                course.students.add(profile)
            return HttpResponseRedirect(
                reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
            )
        elif request.user.is_provider:
            return HttpResponseRedirect(
                reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
            )


class CreateCommitmentTemplateView(ProviderLoginRequiredMixin, View):

    @staticmethod
    def get(request):
        form = CommitmentTemplateForm()
        return render(
            request,
            "commitments/create_commitment_template.html",
            context={"form": form}
        )

    @staticmethod
    def post(request):
        form = CommitmentTemplateForm(request.POST)
        if form.is_valid():
            form.instance.owner = ProviderProfile.objects.get(user=request.user)
            commitment_template = form.save()
            return HttpResponseRedirect(
                reverse(
                    "view CommitmentTemplate", 
                    kwargs={ "commitment_template_id": commitment_template.id }
                )
            )
        else:
            return render(
                request,
                "commitments/create_commitment_template.html",
                context={"form": form}
            )


class ViewCommitmentTemplateView(ProviderLoginRequiredMixin, View):

    @staticmethod
    def get(request, commitment_template_id):
        profile = ProviderProfile.objects.get(user=request.user)
        commitment_template= get_object_or_404(
            CommitmentTemplate,
            id=commitment_template_id,
            owner=profile
        )
        return render(
            request,
            "commitments/view_commitment_template.html",
            context={"commitment_template": commitment_template}
        )


class CourseChangeSuggestedCommitmentsView(ProviderLoginRequiredMixin, View):

    @staticmethod
    def get(request, course_id):
        viewer = ProviderProfile.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, owner=viewer)
        form = CourseSelectSuggestedCommitmentsForm(instance=course)
        return render(
            request,
            "commitments/course_change_suggested_commitments.html",
            context={"course": course, "form": form}
        )

    @staticmethod
    def post(request, course_id):
        viewer = ProviderProfile.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, owner=viewer)
        form = CourseSelectSuggestedCommitmentsForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse(
                    "view course", 
                    kwargs={ "course_id": course.id }
                )
            )
        else:
            return CourseChangeSuggestedCommitmentsView.get(request, course_id)


class CreateFromSuggestedCommitmentView(ClinicianLoginRequiredMixin, View):

    @staticmethod
    def get(request, course_id, commitment_template_id):
        course = get_object_or_404(Course, id=course_id)
        viewer = get_object_or_404(
            course.students, user=request.user
        )
        commitment_template = get_object_or_404(
            course.suggested_commitments, id=commitment_template_id
        )
        form_instance = commitment_template.into_commitment(
            owner=viewer,
            associated_course=course
        )
        form = CommitmentForm(instance=form_instance, profile=viewer)
        return render(
            request,
            "commitments/create_from_suggested_commitment.html",
            {"form": form, "course": course, "commitment_template": commitment_template}
        )

    @staticmethod
    def post(request, course_id, commitment_template_id):
        course = get_object_or_404(Course, id=course_id)
        viewer = get_object_or_404(
            course.students, user=request.user
        )
        commitment_template = get_object_or_404(
            course.suggested_commitments, id=commitment_template_id
        )
        form_instance = commitment_template.into_commitment(
            owner=viewer,
            associated_course=course,
            status=Commitment.CommitmentStatus.IN_PROGRESS
        )
        form = CommitmentForm(request.POST, instance=form_instance, profile=viewer)
        if form.is_valid():
            commitment = form.save()
            return HttpResponseRedirect(
                reverse(
                    "view commitment",
                    kwargs={ "commitment_id": commitment.id }
                )
            )
        else:
            return render(
                request,
                "commitments/create_from_suggested_commitment.html",
                {"form": form, "course": course, "commitment_template": commitment_template}
            )


class DeleteCommitmentTemplateView(ProviderLoginRequiredMixin, View):

    @staticmethod
    def get(request, commitment_template_id):
        viewer = ProviderProfile.objects.get(user=request.user)
        commitment_template = get_object_or_404(
            CommitmentTemplate, id=commitment_template_id, owner=viewer
        )
        return render(
            request,
            "commitments/delete_commitment_template.html",
            {"commitment_template": commitment_template}
        )

    @staticmethod
    def post(request, commitment_template_id):
        viewer = ProviderProfile.objects.get(user=request.user)
        commitment_template = get_object_or_404(
            CommitmentTemplate, id=commitment_template_id, owner=viewer
        )
        if request.POST.get("delete") == "true":
            commitment_template.delete()
            return HttpResponseRedirect(
                reverse("provider dashboard")
            )
        else:
            return HttpResponseBadRequest("'delete' key must be set 'true' to be deleted")


class EditCommitmentTemplateView(ProviderLoginRequiredMixin, View):

    @staticmethod
    def get(request, commitment_template_id):
        viewer = ProviderProfile.objects.get(user=request.user)
        commitment_template = get_object_or_404(
            CommitmentTemplate, id=commitment_template_id, owner=viewer
        )
        form = CommitmentTemplateForm(instance=commitment_template)
        return render(
            request,
            "commitments/edit_commitment_template.html",
            context={
                "commitment_template": commitment_template,
                "form": form
            }
        )

    @staticmethod
    def post(request, commitment_template_id):
        viewer = ProviderProfile.objects.get(user=request.user)
        commitment_template = get_object_or_404(
            CommitmentTemplate, id=commitment_template_id, owner=viewer
        )
        form = CommitmentTemplateForm(request.POST, instance=commitment_template)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse(
                    "view CommitmentTemplate",
                    kwargs={"commitment_template_id": commitment_template_id}
                )
            )
        else:
            return render(
                request,
                "commitments/edit_commitment_template.html",
                context={
                    "commitment_template": commitment_template,
                    "form": form
                }
            )
