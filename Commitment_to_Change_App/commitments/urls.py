from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("template_demo", views.template_demo, name="template demo"),
    path("model_details", views.test_models_show_details, name="model details"),
    path("model_change_title", views.test_models_change_title, name="change title"),
    path("model_change_descrption", views.test_models_change_description, name="change description"),
]

