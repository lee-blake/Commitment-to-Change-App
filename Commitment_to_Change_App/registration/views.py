from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django_registration.backends.activation.views import ActivationView, RegistrationView

from commitments.models import ClinicianProfile, ProviderProfile


class RegisterTypeChoiceView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "registration/must_log_out.html")
        return render(request, "registration/register_choice.html")


class RegisterClinicianView(RegistrationView):

    template_name = "registration/register_clinician.html"
    email_subject_template = "registration/registration_email_subject.txt"
    email_body_template = "registration/registration_email_body.txt"
    success_url = reverse_lazy("awaiting activation")

    def register(self, form):
        user = RegistrationView.register(self, form)
        ClinicianProfile.objects.create(user=user)
        return user


class RegisterProviderView(RegistrationView):

    template_name = "registration/register_provider.html"
    email_subject_template = "registration/registration_email_subject.txt"
    email_body_template = "registration/registration_email_body.txt"
    success_url = reverse_lazy("awaiting activation")

    def register(self, form):
        user = RegistrationView.register(self, form)
        ProviderProfile.objects.create(user=user)
        return user


class AwaitingActivationView(TemplateView):

    template_name = "registration/awaiting_activation.html"


class ActivateAccountView(ActivationView):

    template_name = "registration/activation_failed.html"
    success_url = reverse_lazy("activation complete")


class ActivationCompleteView(TemplateView):

    template_name = "registration/activation_complete.html"
