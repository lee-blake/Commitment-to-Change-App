from django.shortcuts import render
from django.views import View

import cme_accounts.forms
import cme_accounts.models

from commitments.models import ClinicianProfile, ProviderProfile


class RegisterTypeChoiceView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "registration/must_log_out.html")
        return render(request, "registration/register_choice.html")


class RegisterClinicianView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "registration/must_log_out.html")
        form = cme_accounts.forms.CustomUserCreationForm()
        return render(request, "registration/register_clinician.html", context={"form": form})

    @staticmethod
    def post(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "registration/must_log_out.html")
        form = cme_accounts.forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.instance.is_clinician = True
            user = form.save()
            ClinicianProfile.objects.create(user=user)
            return render(request, "registration/register_successful.html")
        else:
            return render(request, "registration/register_clinician.html", context={"form": form})


class RegisterProviderView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "registration/must_log_out.html")
        form = cme_accounts.forms.CustomUserCreationForm()
        return render(request, "registration/register_provider.html", context={"form": form})

    @staticmethod
    def post(request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "registration/must_log_out.html")
        form = cme_accounts.forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.instance.is_provider = True
            user = form.save()
            ProviderProfile.objects.create(user=user)
            return render(request, "registration/register_successful.html")
        else:
            return render(request, "registration/register_provider.html", context={"form": form})
