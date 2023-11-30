from django_registration.forms import RegistrationForm

from cme_accounts.models import User
from commitments.models import ClinicianProfile, ProviderProfile


class ClinicianRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.instance.is_active = False
        self.instance.is_clinician = True

    def save(self, commit=True):
        """Saves the form. Only saves to the database if commit=True.

        Returns the newly created ClinicianProfile. The reason for this is if the User is returned
        instead, a ClinicianProfile may not be created if the programmer then calls save on the
        User instance. Since the profile contains a pointer to the unsaved User, returning the
        profile is preferred due to preserving the possibility to save correctly.
        
        This may be unintuitive given the form instance is a User, but it is preferable to
        either throwing an error on commit=False (also unintuitive) or not informing the
        programmer that they need to save the profile too (will lead to serious bugs)."""
        user = RegistrationForm.save(self, commit)
        profile = ClinicianProfile(user=user)
        if commit:
            profile.save()
        return profile


class ProviderRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.instance.is_active = False
        self.instance.is_provider = True

    def save(self, commit=True):
        """Saves the form. Only saves to the database if commit=True.

        Returns the newly created ProviderProfile. The reason for this is if the User is returned
        instead, a ProviderProfile may not be created if the programmer then calls save on the
        User instance. Since the profile contains a pointer to the unsaved User, returning the
        profile is preferred due to preserving the possibility to save correctly.
        
        This may be unintuitive given the form instance is a User, but it is preferable to
        either throwing an error on commit=False (also unintuitive) or not informing the
        programmer that they need to save the profile too (will lead to serious bugs)."""
        user = RegistrationForm.save(self, commit)
        profile = ProviderProfile(user=user)
        if commit:
            profile.save()
        return profile
