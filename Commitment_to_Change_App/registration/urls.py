from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterTypeChoiceView.as_view(), name="register type choice"),
    path("register/clinician/", views.RegisterClinicianView.as_view(), name="register clinician"),
    path("register/provider/", views.RegisterProviderView.as_view(), name="register provider"),
]