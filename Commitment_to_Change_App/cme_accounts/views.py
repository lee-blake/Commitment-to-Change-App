from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, \
    PasswordResetConfirmView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy


class SignInView(LoginView):
    template_name = "accounts/login.html"


class SignOutView(LogoutView):
    template_name = "accounts/logged_out.html"


class ResetPasswordView(PasswordResetView):
    template_name = "accounts/reset_password.html"
    subject_template_name = "accounts/password_reset_email_subject.txt"
    email_template_name = "accounts/password_reset_email_body.txt"
    success_url = reverse_lazy("awaiting reset email")


class AwaitingResetEmailView(TemplateView):
    template_name = "accounts/awaiting_reset_email.html"


class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = "accounts/reset_password_confirm.html"
    success_url = reverse_lazy("password reset complete")


class ResetPasswordCompleteView(TemplateView):
    template_name = "accounts/reset_password_complete.html"
