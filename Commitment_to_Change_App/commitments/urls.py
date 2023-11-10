from django.urls import path

from . import views

urlpatterns = [
    path("register/clinician/", views.RegisterClinicianView.as_view(), name="register clinician"),
    path("register/provider/", views.RegisterProviderView.as_view(), name="register provider"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("commitment/<int:commitment_id>/view/", views.view_commitment, name="view commitment"),
    path("commitment/<int:commitment_id>/share/", views.view_commitment, name="share commitment"),
    path("commitment/<int:commitment_id>/complete/", views.CompleteCommitmentView.as_view(),
         name="complete commitment"),
    path("commitment/<int:commitment_id>/discontinue/", views.DiscontinueCommitmentView.as_view(),
         name="discontinue commitment"),
    path("commitment/<int:commitment_id>/reopen/", views.ReopenCommitmentView.as_view(), name="reopen commitment"),
    path("commitment/make/", views.MakeCommitmentView.as_view(), name="make commitment"),
    path("commitment/<int:commitment_id>/delete/", views.DeleteCommitmentView.as_view(), name="delete commitment"),
    path("commitment/<int:commitment_id>/edit/", views.EditCommitmentView.as_view(), name="edit commitment"),
]
