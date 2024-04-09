from django.urls import path

from commitments import views

urlpatterns = [
     path(
          "dashboard/",
          views.DashboardRedirectingView.as_view(),
          name="dashboard"
     ),
     path(
          "dashboard/clinician/",
          views.ClinicianDashboardView.as_view(),
          name="clinician dashboard"
     ),
     path(
          "dashboard/provider/",
          views.ProviderDashboardView.as_view(),
          name="provider dashboard"
     ),

     path(
          "commitment/make/",
          views.CreateCommitmentView.as_view(),
          name="create Commitment"
     ),
     path(
          "commitment/<int:commitment_id>/view/", 
          views.ViewCommitmentView.as_view(),
          name="view Commitment"
     ),
     path(
          "commitment/<int:commitment_id>/edit/",
          views.EditCommitmentView.as_view(),
          name="edit Commitment"
     ),
     path(
          "commitment/<int:commitment_id>/delete/",
          views.DeleteCommitmentView.as_view(),
          name="delete Commitment"
     ),
     path(
          "commitment/<int:commitment_id>/complete/",
          views.CompleteCommitmentView.as_view(),
         name="complete Commitment"
     ),
     path(
          "commitment/<int:commitment_id>/discontinue/",
          views.DiscontinueCommitmentView.as_view(),
         name="discontinue Commitment"
     ),
     path(
          "commitment/<int:commitment_id>/reopen/",
          views.ReopenCommitmentView.as_view(),
          name="reopen Commitment"
     ),
     path(
          "course/<int:course_id>/suggested-commitments/<int:commitment_template_id>/create-from/",
          views.CreateFromSuggestedCommitmentView.as_view(),
          name="create Commitment from suggested commitment"
     ),

     path(
          "course/create/",
          views.CreateCourseView.as_view(),
          name="create Course"
     ),
     path(
          "course/<int:course_id>/view/",
          views.ViewCourseView.as_view(),
          name="view Course"
     ),
     path(
          "course/<int:course_id>/edit/",
          views.EditCourseView.as_view(),
          name="edit Course"
     ),
     path(
          "course/<int:course_id>/suggested-commitments/select/",
          views.CourseChangeSuggestedCommitmentsView.as_view(),
          name="change Course suggested commitments"
     ),
     path(
          "course/<int:course_id>/associated-commitments/download-csv",
          views.DownloadCourseCommitmentsCSVView.as_view(),
          name="download Course Commitments as csv"
     ),
     path(
          "course/<int:course_id>/join/<str:join_code>/",
          views.JoinCourseView.as_view(),
          name="join Course"
     ),

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
          "commitment-template/<int:commitment_template_id>/edit/",
          views.EditCommitmentTemplateView.as_view(),
          name="edit CommitmentTemplate"
     ),
     path(
          "commitment-template/<int:commitment_template_id>/delete/",
          views.DeleteCommitmentTemplateView.as_view(),
          name="delete CommitmentTemplate"
     ),

     path(
          "statistics/courses/aggregate/",
          views.AggregateCourseStatisticsCSVDownloadView.as_view(),
          name="download aggregate Course statistics as csv"
     ),
     path(
         "statistics/commitment-templates/aggregate/",
          views.AggregateCommitmentTemplateStatisticsCSVDownloadView.as_view(),
          name="download aggregate CommitmentTemplate statistics as csv"
     ),
     path(
          "statistics/dashboard/",
          views.StatisticsOverviewView.as_view(),
          name="statistics overview"
     ),

     path(
          "commitment/<int:commitment_id>/reminders/create/",
          views.CreateCommitmentReminderEmailView.as_view(),
          name="create CommitmentReminderEmail"
     ),
     path(
          "commitment/<int:commitment_id>/reminders/view-all/",
          views.ViewCommitmentReminderEmailsView.as_view(),
          name="view CommitmentReminderEmails"
     ),
     path(
          "commitment/<int:commitment_id>/reminders/<int:reminder_email_id>/delete/",
          views.DeleteCommitmentReminderEmailView.as_view(),
          name="delete CommitmentReminderEmail"
     ),
     path(
          "commitment/<int:commitment_id>/reminders/clear/",
          views.ClearCommitmentReminderEmailsView.as_view(),
          name="clear CommitmentReminderEmails"
     ),

     path(
          "commitment/<int:commitment_id>/reminders/create/recurring/",
          views.CreateRecurringReminderEmailView.as_view(),
          name="create RecurringReminderEmail"
     ),
     path(
          "commitment/<int:commitment_id>/reminders/recurring/delete/",
          views.DeleteRecurringReminderEmailView.as_view(),
          name="delete RecurringReminderEmail"
     ),
]
