# Create your views here.
from django.http import HttpResponse


def display_logged_in_user(request):
    if request.user.is_authenticated:
        return HttpResponse("Logged in as {}".format(request.user.username))
    else:
        return HttpResponse("Not logged in")
