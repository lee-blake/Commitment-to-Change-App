import datetime
import random

from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse("This is the index route.")

def template_demo(request):
    num = random.randint(1, 100)
    moment = datetime.datetime.now()
    context = { "random_number": num, "now": moment }
    return render(request, "commitments/template_demo.html", context)


