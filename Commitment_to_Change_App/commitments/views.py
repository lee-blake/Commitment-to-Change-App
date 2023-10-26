import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .models import Commitment


def index(request):
    return HttpResponse("This is the index route.")


def show_all_commitments(request):
    # NOTE: The HTML in this route is particularly bad because there incredible duplication of styling. Better would
    # be to make this into a template. However, we will go with this mess right now because that template is part
    # of the frontend development, and it will be easy to integrate later.
    commitments = Commitment.objects.all()
    response_table = '<table style="border-collapse: collapse; border: 1px solid;">'
    response_table += """<tr>
    <th style="border: 1px solid;">ID</th>
    <th style="border: 1px solid;">Title</th>
    <th style="border: 1px solid;">Description</th>
    <th style="border: 1px solid;">Deadline</th>
    <th style="border: 1px solid;">Status</th>
    <th style="border: 1px solid;">Created</th>
    <th style="border: 1px solid;">Modified</th>
    </tr>"""
    for commitment in commitments:
        def status_value_to_string(num):
            match num:
                case 0:
                    return "In progress"
                case 1:
                    return "Complete"
                case 2:
                    return "Expired"
                case _:
                    return num

        response_table += """<tr>
        <td style="border: 1px solid;">{}</td>
        <td style="border: 1px solid;">{}</td>
        <td style="border: 1px solid;">{}</td>
        <td style="border: 1px solid;">{}</td>
        <td style="border: 1px solid;">{}</td>
        <td style="border: 1px solid;">{}</td>
        <td style="border: 1px solid;">{}</td>
        </tr>""".format(
            commitment.id,
            commitment.title,
            commitment.description,
            commitment.deadline,
            status_value_to_string(commitment.status),
            commitment.created,
            commitment.last_updated
        )
    response_table += "</table>"
    return HttpResponse(response_table)


def view_commitment(request, commitment_id):
    commitment = get_object_or_404(Commitment, id=commitment_id)

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


def create_commitment_target(request):
    title = request.GET.get("title")
    description = request.GET.get("description")
    deadline = datetime.date.fromisoformat(request.GET.get("deadline"))
    commitment = Commitment.objects.create(
        title=title,
        description=description,
        deadline=deadline,
        status=Commitment.CommitmentStatus.IN_PROGRESS
    )
    return HttpResponse(
        """Successfully created a new commitment with id {0}. 
        Here is a <a href="/app/commitment/{0}/view">link</a> to it.""".format(commitment.id)
    )
