from django.urls import path

from . import views

urlpatterns = [
    path("display_logged_in_user", views.display_logged_in_user, name="index"),
]
