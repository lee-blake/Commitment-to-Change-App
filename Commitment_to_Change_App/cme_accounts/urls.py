from django.urls import include, path

from . import views

urlpatterns = [

    path("login/", views.SignInView.as_view(), name="login"),
    path("logout/", views.SignOutView.as_view(), name="logout"),
    # This imports all the default Django auth urls. See
    # https://docs.djangoproject.com/en/4.2/topics/auth/default/#module-django.contrib.auth.views
    # They are NOT generally working - we need to write templates for them.
    path("", include("django.contrib.auth.urls")),
    # create currently uses GET to create users and is not suitable for production. It needs a form to be created
    # before we can switch to POST.
    path("create", views.create_user_target, name="create user target"),
]
