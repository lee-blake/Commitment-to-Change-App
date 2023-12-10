from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django_registration.backends.activation.views import ActivationView, RegistrationView

from registration.forms import ClinicianRegistrationForm, ProviderRegistrationForm


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
    form_class = ClinicianRegistrationForm

    def create_inactive_user(self, form):
        """Creates the inactive user and sends an email with activation instructions.

        Inherited from RegistrationView.

        This must be overriden to be able to save a ClinicianProfile because the original
        implementation only calls a save(commit=True) on the user, not the form. To save the profile
        form data we need to change it to save the form and set the user inactive in the form.
        Since we also return the profile when saving, we also need to adjust for that."""
        new_user = form.save().user
        self.send_activation_email(new_user)
        return new_user


class RegisterProviderView(RegistrationView):
    template_name = "registration/register_provider.html"
    email_subject_template = "registration/registration_email_subject.txt"
    email_body_template = "registration/registration_email_body.txt"
    success_url = reverse_lazy("awaiting activation")
    form_class = ProviderRegistrationForm

    def create_inactive_user(self, form):
        """Creates the inactive user and sends an email with activation instructions.

        Inherited from RegistrationView.

        This must be overriden to be able to save a ProviderProfile because the original
        implementation only calls a save(commit=True) on the user, not the form. To save the profile
        form data we need to change it to save the form and set the user inactive in the form.
        Since we also return the profile when saving, we also need to adjust for that."""
        new_user = form.save().user
        self.send_activation_email(new_user)
        return new_user


class AwaitingActivationView(TemplateView):
    template_name = "registration/awaiting_activation.html"


class ActivateAccountView(ActivationView):
    template_name = "registration/activation_failed.html"
    success_url = reverse_lazy("activation complete")


class ActivationCompleteView(TemplateView):
    template_name = "registration/activation_complete.html"
