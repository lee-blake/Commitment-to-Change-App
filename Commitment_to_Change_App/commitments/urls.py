from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("template_demo", views.template_demo, name="template demo"),
]

