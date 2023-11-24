from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.DashboardRedirectingView.as_view(), name="dashboard"),
    path("dashboard/clinician/", views.ClinicianDashboardView.as_view(), name="clinician dashboard"),
    path("dashboard/provider/", views.ProviderDashboardView.as_view(), name="provider dashboard"),
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
    path("course/create/", views.CreateCourseView.as_view(), name="create course"),
    path("course/<int:course_id>/edit/", views.EditCourseView.as_view(), name="edit course"),
    path("course/<int:course_id>/view/", views.ViewCourseView.as_view(), name="view course"),
    path("course/<int:course_id>/join/<str:join_code>/", views.JoinCourseView.as_view(), name="join course"),
]
