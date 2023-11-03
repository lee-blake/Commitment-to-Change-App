import datetime

import cme_accounts.models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View

from .forms import CommitmentForm
from .models import Commitment, ClinicianProfile


@login_required
def dashboard(request):
    profile = ClinicianProfile.objects.get(user=request.user)
    commitments = Commitment.objects.filter(owner=profile)
    for commitment in commitments:
        commitment.mark_expired_if_deadline_has_passed(datetime.date.today())
    context = {
        'commitments': commitments,
    }
    return render(request, "commitments/dashboard.html", context)


def view_commitment(request, commitment_id):
    commitment = get_object_or_404(Commitment, id=commitment_id)
    commitment.mark_expired_if_deadline_has_passed(datetime.date.today())

    def status_value_to_string(num):
        match num:
            case 0:
                return "In progress"
            case 1:
                return "Complete"
            case 2:
                return "Expired"
            case _:
                return "no number"

    status = status_value_to_string(commitment.status)
    commitment_context = {
        "id": commitment.id,
        "title": commitment.title,
        "description": commitment.description,
        "deadline": commitment.deadline,
        "status": status,
        "created_date": commitment.created,
        # TODO: created_date currently converts our timestamp with timezone to UTC
        # so if you have 22:00:00-5 (-5 being EST), it will add 5 to convert
        # to UTC, so it becomes 03:00:00
        "last_update": commitment.last_updated
    }
    return render(request, "commitments/view_commitment.html", commitment_context)


def create_commitment_form(request):
    return render(request, "commitments/create_commitment.html")


@login_required
def create_commitment_target(request):
    owner = ClinicianProfile.objects.get(user=request.user)
    title = request.POST.get("title")
    description = request.POST.get("description")
    deadline = datetime.date.fromisoformat(request.POST.get("deadline"))
    commitment = Commitment.objects.create(
        title=title,
        description=description,
        deadline=deadline,
        status=Commitment.CommitmentStatus.IN_PROGRESS,
        owner=owner
    )
    return HttpResponseRedirect("/app/commitment/{}/view".format(commitment.id))


def complete_commitment_target(request, commitment_id):
    commitment = get_object_or_404(Commitment, id=commitment_id)
    # TODO a dedicated method would be better for this
    if request.GET.get("complete") == "true":
        commitment.status = Commitment.CommitmentStatus.COMPLETE
        commitment.save()
        return HttpResponseRedirect("/app/commitment/{}/view".format(commitment_id))
    else:
        return HttpResponse("Complete key must be set to 'true' to mark as complete.")


def register_clinician(request):
    username = request.GET.get("username")
    password = request.GET.get("password")
    email = request.GET.get("email")
    user = cme_accounts.models.User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    profile = ClinicianProfile.objects.create(
        user=user
    )
    return HttpResponse("User {} created with profile {}.".format(username, profile))


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
