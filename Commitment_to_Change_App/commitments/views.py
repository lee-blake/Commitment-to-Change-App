import datetime
import random

from django.http import HttpResponse
from django.shortcuts import render

from .models import Commitment

def index(request):
    return HttpResponse("This is the index route.")

def template_demo(request):
    num = random.randint(1, 100)
    moment = datetime.datetime.now()
    context = { "random_number": num, "now": moment }
    return render(request, "commitments/template_demo.html", context)

def test_models_show_details(request):
    x = Commitment.objects.get(id=1)
    return HttpResponse("{}<br>{}".format(x.title, x.description))

def test_models_change_title(request):
    x = Commitment.objects.get(id=1)
    x.title = "lol. lmao even."
    x.save()
    return HttpResponse("changed title")

def test_models_change_description(request):
    x = Commitment.objects.get(id=1)
    print(x.description)
    x.double_description()
    print(x.description)
    x.save()
    return HttpResponse("changed description")

def test_models_list_commitments(request):
    commitments = Commitment.objects.all()
    responseTable = "<table>"
    responseTable += "<tr><th>ID</th><th>Title</th><th>Description</th></tr>"
    for commitment in commitments:
        responseTable += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(commitment.id, commitment.title, commitment.description)
    responseTable += "</table>"
    return HttpResponse(responseTable)

def test_models_create_commitment(request):
    # POST is the same, just replace GET. GET is better for experimenting 
    # manually but we should use POST when we actually implement stuff.
    t = request.GET.get("title", "defaultTitle")
    d = request.GET.get("description", "defaultDescription")
    x = Commitment.objects.create(title=t, description=d)
    return HttpResponse("Commitment {} created".format(x.id))
