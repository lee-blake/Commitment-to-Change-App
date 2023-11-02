from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse

from .models import User


class SignInView(LoginView):
    template_name = "accounts/login.html"


class SignOutView(LogoutView):
    template_name = "accounts/logged_out.html"


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
