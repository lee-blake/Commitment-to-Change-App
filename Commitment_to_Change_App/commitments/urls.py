from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterTypeChoiceView.as_view(), name="register type choice"),
    path("register/clinician/", views.RegisterClinicianView.as_view(), name="register clinician"),
    path("register/provider/", views.RegisterProviderView.as_view(), name="register provider"),
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
     path(
          "commitment-template/create/", 
          views.CreateCommitmentTemplateView.as_view(),
          name="create CommitmentTemplate"
     ),
     path(
          "commitment-template/<int:commitment_template_id>/view/",
          views.ViewCommitmentTemplateView.as_view(),
          name="view CommitmentTemplate"
     ),
     path(
          "course/<int:course_id>/suggested-commitments/select/",
          views.CourseChangeSuggestedCommitmentsView.as_view(),
          name="change Course suggested commitments"
     ),
     path(
          "course/<int:course_id>/suggested-commitments/<int:commitment_template_id>/create-from/",
          views.CreateFromSuggestedCommitmentView.as_view(),
          name="create Commitment from suggested commitment"
     ),
     path(
          "commitment-template/<int:commitment_template_id>/delete/",
          views.DeleteCommitmentTemplateView.as_view(),
          name="delete CommitmentTemplate"
     ),
     path(
          "commitment-template/<int:commitment_template_id>/edit/",
          views.EditCommitmentTemplateView.as_view(),
          name="edit CommitmentTemplate"
     ),
]
