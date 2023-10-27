# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

from .models import User


def display_logged_in_user(request):
    if request.user.is_authenticated:
        return HttpResponse("Logged in as {}".format(request.user.username))
    else:
        return HttpResponse("Not logged in")


def create_user_target(request):
    username = request.GET.get("username")
    password = request.GET.get("password")
    email = request.GET.get("email")
    User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    return HttpResponse("User {} created.".format(username))


def do_login(request):
    username = request.GET.get("username")
    password = request.GET.get("password")
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return HttpResponse("Login successful")
    else:
        return HttpResponse("Login failed")


def do_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponse("Logout successful")
    else:
        return HttpResponse("Nobody was logged in")
