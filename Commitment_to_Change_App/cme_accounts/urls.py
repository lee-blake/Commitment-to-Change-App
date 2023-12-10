from django.urls import path

from . import views

urlpatterns = [
    path(
        "login/",
        views.SignInView.as_view(redirect_authenticated_user=True),
        name="login"
    ),
    path(
        "logout/",
        views.SignOutView.as_view(),
        name="logout"
    ),
    path(
        "password-reset/",
        views.ResetPasswordView.as_view(),
        name="reset password"
    ),
    path(
        "password-reset/sent/",
        views.AwaitingResetEmailView.as_view(),
        name="awaiting reset email"
    ),
    path(
        "reset/<uidb64>/<token>/", 
        views.ResetPasswordConfirmView.as_view(),
        name="confirm reset password"
    ),
    path(
        "password-reset/done/", 
        views.ResetPasswordCompleteView.as_view(),
        name="password reset complete"
    ),
]
