from django.urls import include, path

from . import views

urlpatterns = [
    # This imports all the default Django auth urls. See
    # https://docs.djangoproject.com/en/4.2/topics/auth/default/#module-django.contrib.auth.views
    # They are NOT generally working - we need to write templates for them.
    path("", include("django.contrib.auth.urls")),
    # create currently uses GET to create users and is not suitable for production. It needs a form to be created
    # before we can switch to POST.
    path("create", views.create_user_target, name="create user target"),
    path("display_logged_in_user", views.display_logged_in_user, name="index"),
    # do_login and do_logout are 'testing' login and logout views. They use GET and are not suitable for production
    # but are currently useful for basic testing.
    path("do_login", views.do_login, name="login"),
    path("do_logout", views.do_logout, name="logout")
]
