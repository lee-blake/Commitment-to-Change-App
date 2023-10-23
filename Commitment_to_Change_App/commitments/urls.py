from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("template_demo", views.template_demo, name="template demo"),
    path("model_details", views.test_models_show_details, name="model details"),
    path("model_change_title", views.test_models_change_title, name="change title"),
    path("model_change_description", views.test_models_change_description, name="change description"),
    path("model_list_all", views.test_models_list_commitments, name="list all commitments"),
    path("model_create", views.test_models_create_commitment, name="create commitment"),
]

