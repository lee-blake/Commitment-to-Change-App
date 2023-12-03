from django_registration.forms import RegistrationForm

from cme_accounts.models import User
from commitments.forms import ProviderProfileForm
from commitments.models import ClinicianProfile


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
        self._profile_form = ProviderProfileForm(*args, **kwargs)
        self.fields.update(self._profile_form.fields)

    def clean(self):
        super().clean()
        self._ensure_profile_form_is_cleaned()

    def _ensure_profile_form_is_cleaned(self):
        # A full clean is necessary to ensure the profile form sets up cleaned_data correctly.
        self._profile_form.full_clean()
        # Field-level validation errors are already handled by the updating of the registration
        # form's fields in the constructor. We only onclude the non-field errors to avoid showing
        # the user the same error twice.
        for error in self._profile_form.non_field_errors():
            self.add_error(None, error)

    def save(self, commit=True):
        """Saves the form. Only saves to the database if commit=True.

        Returns the newly created ProviderProfile. The reason for this is if the User is returned
        instead, a ProviderProfile may not be created if the programmer then calls save on the
        User instance. Since the profile contains a pointer to the unsaved User, returning the
        profile is preferred due to preserving the possibility to save correctly.
        
        This may be unintuitive given the form instance is a User, but it is preferable to
        either throwing an error on commit=False (also unintuitive) or not informing the
        programmer that they need to save the profile too (will lead to serious bugs)."""
        user = RegistrationForm.save(self, commit=commit)
        self._profile_form.instance.user = user
        profile = self._profile_form.save(commit=commit)
        return profile
