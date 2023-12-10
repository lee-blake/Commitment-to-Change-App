from django.urls import path

from registration import views

urlpatterns = [
    path(
        "register/", 
        views.RegisterTypeChoiceView.as_view(),
        name="register type choice"
    ),
    path(
        "register/clinician/",
        views.RegisterClinicianView.as_view(),
        name="register clinician"
    ),
    path(
        "register/provider/",
        views.RegisterProviderView.as_view(),
        name="register provider"
    ),
    path(
        "register/success/",
        views.AwaitingActivationView.as_view(),
        name="awaiting activation"
    ),
    path(
        "activate/key/<str:activation_key>/", 
        views.ActivateAccountView.as_view(),
        name="activate account"
    ),
    path(
        "activate/success/",
        views.ActivationCompleteView.as_view(),
        name="activation complete"
    ),
]
