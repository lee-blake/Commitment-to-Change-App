from django.urls import path

from . import views, demo_views

urlpatterns = [
    path("", views.index, name="index"),
    path("show_all_commitments", views.show_all_commitments, name="show all commitments"),
    path("commitment/<int:commitment_id>/view", views.view_commitment, name="view commitment"),
    path("commitment/create", views.create_commitment, name="create commitment"),

    path("demo/template_demo", demo_views.template_demo, name="template demo"),
    path("demo/model_details", demo_views.test_models_show_details, name="model details"),
    path("demo/model_change_title", demo_views.test_models_change_title, name="change title"),
    path("demo/model_change_description", demo_views.test_models_change_description, name="change description"),
    path("demo/model_list_all", demo_views.test_models_list_commitments, name="list all commitments"),
    path("demo/model_create", demo_views.test_models_create_commitment, name="create commitment"),
]
