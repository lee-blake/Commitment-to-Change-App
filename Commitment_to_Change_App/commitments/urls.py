from django.urls import path

from . import views

urlpatterns = [
    path("register/clinician/", views.RegisterClinicianView.as_view(), name="register clinician"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("commitment/<int:commitment_id>/view/", views.view_commitment, name="view commitment"),
    path(
        "commitment/<int:commitment_id>/complete/",
        views.CompleteCommitmentView.as_view(),
        name="complete commitment"
    ),
    path(
        "commitment/<int:commitment_id>/discontinued/",
        views.discontinued_commitment_target,
        name="discontinued commitment target"
    ),

    path(
        "commitment/make/", views.MakeCommitmentView.as_view(), name="make commitment"
    ),
    path(
        "commitment/<int:commitment_id>/edit/", views.EditCommitmentView.as_view(), name="edit commitment"
    ),
]
