import datetime
import random
import string

import cme_accounts.forms
import cme_accounts.models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed, \
    HttpResponseServerError, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View

from .forms import CommitmentForm, DeleteCommitmentForm, CourseForm
from .models import Commitment, ClinicianProfile, ProviderProfile, Course


def view_commitment(request, commitment_id):
    commitment = get_object_or_404(Commitment, id=commitment_id)
    commitment.mark_expired_if_deadline_has_passed(datetime.date.today())
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


class ClinicianDashboardView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitments = Commitment.objects.filter(owner=profile)
        for commitment in commitments:
            commitment.mark_expired_if_deadline_has_passed(datetime.date.today())

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


class ProviderDashboardView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        profile = ProviderProfile.objects.get(user=request.user)
        courses = Course.objects.filter(owner=profile)
        return render(request, "commitments/dashboard_provider.html", {"courses": courses})


class MakeCommitmentView(LoginRequiredMixin, View):
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
            return HttpResponseRedirect("/app/commitment/{}/view".format(commitment.id))
        else:
            return render(request, "commitments/make_commitment.html", context={"form": form})


class DeleteCommitmentView(LoginRequiredMixin, View):
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


class EditCommitmentView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        commitment.mark_expired_if_deadline_has_passed(datetime.date.today())
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
        commitment.mark_expired_if_deadline_has_passed(datetime.date.today())
        form = CommitmentForm(request.POST, instance=commitment, profile=profile)
        if form.is_valid():
            commitment = form.save()
            return HttpResponseRedirect("/app/commitment/{}/view".format(commitment.id))
        else:
            return render(
                request,
                "commitments/edit_commitment.html",
                context={
                    "commitment": commitment,
                    "form": form
                }
            )


class CompleteCommitmentView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        if request.POST.get("complete") == "true":
            commitment.status = Commitment.CommitmentStatus.COMPLETE
            commitment.save()
            return HttpResponseRedirect("/app/commitment/{}/view".format(commitment_id))
        else:
            return HttpResponseBadRequest("'complete' key must be set to 'true' to complete a commitment")

    @staticmethod
    def get(request, commitment_id):
        return HttpResponseNotAllowed(['POST'])


class DiscontinueCommitmentView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        if request.POST.get("discontinue") == "true":
            commitment.status = Commitment.CommitmentStatus.DISCONTINUED
            commitment.save()
            return HttpResponseRedirect("/app/commitment/{}/view".format(commitment_id))
        else:
            return HttpResponseBadRequest("'discontinue' key must be set to 'true' to discontinue a commitment")

    @staticmethod
    def get(request, commitment_id):
        return HttpResponseNotAllowed(['POST'])


class ReopenCommitmentView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        if request.POST.get("reopen") == "true":
            if commitment.deadline < datetime.date.today():
                commitment.status = Commitment.CommitmentStatus.EXPIRED
            else:
                commitment.status = Commitment.CommitmentStatus.IN_PROGRESS
            commitment.save()
            return HttpResponseRedirect("/app/commitment/{}/view".format(commitment_id))
        else:
            return HttpResponseBadRequest("'reopen' key must be set to 'true' to reopen a commitment")

    @staticmethod
    def get(request, commitment_id):
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
            return HttpResponse("Clinician user creation successful.<br><a href=\"/accounts/login/\">Log In</a>")
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
            return HttpResponse("Provider user creation successful.<br><a href=\"/accounts/login/\">Log In</a>")
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
            return HttpResponseRedirect("/app/course/{}/view".format(course.id))
        else:
            return render(request, "commitments/create_course.html", context={"form": form})

    @staticmethod
    def generate_random_join_code(length):
        return ''.join(random.choice(string.ascii_uppercase) for i in range(0, length))


class ViewCourseView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if request.user.is_provider and course.owner == ProviderProfile.objects.get(user=request.user):
            return render(request, "commitments/view_owned_course.html", {"course": course})
        elif request.user.is_clinician and course.students.contains(ClinicianProfile.objects.get(user=request.user)):
            return render(request, "commitments/view_course.html", {"course": course})
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
            return HttpResponseRedirect("/app/course/{}/view".format(course.id))
        elif request.user.is_provider:
            return HttpResponseRedirect("/app/course/{}/view".format(course.id))
