from django.contrib.auth.views import LoginView, LogoutView


class SignInView(LoginView):
    template_name = "accounts/login.html"


class SignOutView(LogoutView):
    template_name = "accounts/logged_out.html"
