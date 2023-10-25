from django.urls import path

from . import views, demo_views

urlpatterns = [
    path("", views.index, name="index"),
    path("show_all_commitments", views.show_all_commitments, name="show all commitments"),
    path("commitment/<int:commitment_id>/view", views.view_commitment, name="view commitment"),
    path("commitment/create", views.create_commitment, name="create commitment"),

    path("demo/template_demo", demo_views.template_demo, name="template demo"),
]
