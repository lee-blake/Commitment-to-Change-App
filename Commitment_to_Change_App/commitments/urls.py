from django.urls import path

from . import views, demo_views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name= "dashboard"),
    path("show_all_commitments", views.show_all_commitments, name="show all commitments"),
    path("commitment/<int:commitment_id>/view", views.view_commitment, name="view commitment"),
    path("commitment/new", views.create_commitment_form, name="create commitment form"),
    path("commitment/create", views.create_commitment_target, name="create commitment target"),

    path("demo/template_demo", demo_views.template_demo, name="template demo"),
]
