from django.urls import path

from . import views
from .forms import ClinicianRegistrationForm, ProviderRegistrationForm

urlpatterns = [
    path("register/", views.RegisterTypeChoiceView.as_view(), name="register type choice"),
    path("register/clinician/", views.RegisterClinicianView.as_view(
        form_class=ClinicianRegistrationForm
    ), name="register clinician"),
    path("register/provider/", views.RegisterProviderView.as_view(
        form_class=ProviderRegistrationForm
    ), name="register provider"),
    path("register/success/", views.AwaitingActivationView.as_view(), name="awaiting activation"),
    path(
        "activate/key/<str:activation_key>/", 
        views.ActivateAccountView.as_view(),
        name="activate account"
    ),
    path("activate/success/", views.ActivationCompleteView.as_view(), name="activation complete"),
]
