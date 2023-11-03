from django.urls import path

from . import views

urlpatterns = [
    path("register/clinician/", views.RegisterClinicianView.as_view(), name="register clinician"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("commitment/<int:commitment_id>/view/", views.view_commitment, name="view commitment"),
    path("commitment/new/", views.create_commitment_form, name="create commitment form"),
    path("commitment/create/", views.create_commitment_target, name="create commitment target"),
    path(
        "commitment/<int:commitment_id>/complete/",
        views.complete_commitment_target,
        name="complete commitment target"
    ),

    path(
        "commitment/make/", views.MakeCommitmentView.as_view(), name="make commitment"
    ),
]
