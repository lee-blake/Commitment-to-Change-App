import datetime

import cme_accounts.forms
import cme_accounts.models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View

from .forms import CommitmentForm, DeleteCommitmentForm
from .models import Commitment, ClinicianProfile


@login_required
def dashboard(request):
    profile = ClinicianProfile.objects.get(user=request.user)
    commitments = Commitment.objects.filter(owner=profile)
    for commitment in commitments:
        commitment.mark_expired_if_deadline_has_passed(datetime.date.today())

    in_progress = list(filter(lambda x: x.status == 0, commitments))
    completed = list(filter(lambda x: x.status == 1, commitments))
    expired = list(filter(lambda x: x.status == 2, commitments))
    discontinued = list(filter(lambda x: x.status == 3, commitments))

    context = {
        'in_progress_commitments': in_progress,
        'expired_commitments': expired,
        'completed_commitments': completed,
        'discontinued_commitments': discontinued,
    }

    return render(request, "commitments/dashboard.html", context)


def view_commitment(request, commitment_id):
    commitment = get_object_or_404(Commitment, id=commitment_id)
    commitment.mark_expired_if_deadline_has_passed(datetime.date.today())
    context = {"commitment": commitment}
    if request.user.is_authenticated and request.user == commitment.owner.user:
        return render(request, "commitments/view_commitment.html", context)
    else:
        return render(request, "commitments/share_commitment.html", context)


class MakeCommitmentView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        form = CommitmentForm()
        return render(request, "commitments/make_commitment.html", context={"form": form})

    @staticmethod
    def post(request, *args, **kwargs):
        form = CommitmentForm(request.POST)
        if form.is_valid():
            form.instance.owner = ClinicianProfile.objects.get(user=request.user)
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
            return HttpResponseBadRequest("Delete key must be set 'true' to be deleted")


class EditCommitmentView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, commitment_id):
        profile = ClinicianProfile.objects.get(user=request.user)
        commitment = get_object_or_404(Commitment, id=commitment_id, owner=profile)
        commitment.mark_expired_if_deadline_has_passed(datetime.date.today())
        form = CommitmentForm(instance=commitment)
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
        form = CommitmentForm(request.POST, instance=commitment)
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
            return HttpResponseBadRequest("Complete key must be set to true to complete a commitment")

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
            return HttpResponseBadRequest("Discontinue key must be set to true to discontinue a commitment")

    @staticmethod
    def get(request, commitment_id):
        return HttpResponseNotAllowed(['POST'])


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
            user = form.save()
            ClinicianProfile.objects.create(user=user)
            return HttpResponse("User creation successful.<br><a href=\"/accounts/login/\">Log In</a>")
        else:
            return render(request, "commitments/register_clinician.html", context={"form": form})
