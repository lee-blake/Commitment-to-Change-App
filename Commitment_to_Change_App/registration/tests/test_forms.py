import pytest

from django.core.exceptions import ValidationError

from cme_accounts.models import User
from commitments.forms import ClinicianProfileForm, ProviderProfileForm
from commitments.models import ClinicianProfile, ProviderProfile
from registration.forms import ClinicianRegistrationForm, ProviderRegistrationForm

@pytest.mark.django_db
class TestClinicianRegistrationForm:
    """Tests for ClinicianRegistrationForm"""

    class TestInit:
        """Tests for ClinicianRegistrationForm.__init__"""

        def test_instance_is_marked_as_clinician(self):
            form = ClinicianRegistrationForm()
            assert form.instance.is_clinician

        def test_instance_is_marked_as_inactive(self):
            form = ClinicianRegistrationForm()
            assert not form.instance.is_active

        def test_form_has_clinician_profile_form_fields(self):
            form = ClinicianRegistrationForm()
            profile_form_fields = ClinicianProfileForm().fields.keys()
            for field in profile_form_fields:
                assert field in form.fields.keys()


    class TestIsValid:
        """Tests for ClinicianRegistrationForm.is_valid"""

        def test_clean_calls_clean_for_clinician_profile_form(self):
            """Tests that data validation for the ClinicianProfileForm extends beyond
            the field level validation provided by injecting its fields into the 
            ClinicianRegistrationForm. This is necessary for if we ever have two fields
            where validation is a relation to each other (for example, start and end dates).

            Presently there are no such fields that would need any validation, and therefore
            there is no way to trip the ClinicianProfileForm::clean method. For now, we will 
            instead inject one that will always fail and verify that it occurs when the parent 
            clean is called.
            """
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!",
            }
            form = ClinicianRegistrationForm(form_data)
            def fail_clean():
                raise ValidationError("ClinicianProfileForm::clean was called!")
            # Patch in the method that will raise a ValidationError
            form._profile_form.clean = fail_clean #pylint: disable=protected-access
            assert not form.is_valid()
            # Verify that the validation error will show in the errorlist
            assert "ClinicianProfileForm::clean was called!" in form.errors.as_ul()


    class TestSave:
        """Tests for ClinicianRegistrationForm.save"""

        def test_valid_form_only_saves_as_clinician(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!"
            }
            form = ClinicianRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            assert user.is_clinician
            assert not user.is_provider

        def test_valid_form_saves_as_inactive(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!"
            }
            form = ClinicianRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            assert not user.is_active

        def test_valid_form_creates_clinician_profile(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!"
            }
            form = ClinicianRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            assert ClinicianProfile.objects.filter(user=user).exists()

        def test_valid_form_creates_clinician_profile_with_correct_full_name(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!",
                "first_name": "Adam",
                "last_name": "Smith"
            }
            form = ClinicianRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            profile = ClinicianProfile.objects.get(user=user)
            assert profile.first_name == "Adam"
            assert profile.last_name == "Smith"

        def test_valid_form_creates_clinician_profile_with_correct_institution(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!",
                "institution": "Stanford CME"
            }
            form = ClinicianRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            profile = ClinicianProfile.objects.get(user=user)
            assert profile.institution == "Stanford CME"

        def test_noncommital_save_preserves_access_to_both_unsaved_objects(self):
            """Verify that if the form is saved noncommitally, the programmer can still
            access both the user and the profile to save them without losing data."""
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!"
            }
            form = ClinicianRegistrationForm(form_data)
            profile = form.save(commit=False)
            assert isinstance(profile, ClinicianProfile)
            assert profile.user
            assert profile.user.username == "test-form-username"



@pytest.mark.django_db
class TestProviderRegistrationForm:
    """Tests for ProviderRegistrationForm"""

    class TestInit:
        """Tests for ProviderRegistrationForm.__init__"""

        def test_instance_is_marked_as_provider(self):
            form = ProviderRegistrationForm()
            assert form.instance.is_provider

        def test_instance_is_marked_as_inactive(self):
            form = ProviderRegistrationForm()
            assert not form.instance.is_active

        def test_form_has_provider_profile_form_fields(self):
            form = ProviderRegistrationForm()
            profile_form_fields = ProviderProfileForm().fields.keys()
            for field in profile_form_fields:
                assert field in form.fields.keys()


    class TestIsValid:
        """Tests for ProviderRegistrationForm.is_valid"""

        def test_clean_calls_clean_for_provider_profile_form(self):
            """Tests that data validation for the ProviderProfileForm extends beyond
            the field level validation provided by injecting its fields into the 
            ProviderRegistrationForm. This is necessary for if we ever have two fields
            where validation is a relation to each other (for example, start and end dates).

            Presently there are no such fields that would need any validation, and therefore
            there is no way to trip the ProviderProfileForm::clean method. For now, we will 
            instead inject one that will always fail and verify that it occurs when the parent 
            clean is called.
            """
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!",
                "institution": "Stanford CME"
            }
            form = ProviderRegistrationForm(form_data)
            def fail_clean():
                raise ValidationError("ProviderProfileForm::clean was called!")
            # Patch in the method that will raise a ValidationError
            form._profile_form.clean = fail_clean #pylint: disable=protected-access
            assert not form.is_valid()
            # Verify that the validation error will show in the errorlist
            assert "ProviderProfileForm::clean was called!" in form.errors.as_ul()


    class TestSave:
        """Tests for ProviderRegistrationForm.save"""

        def test_valid_form_only_saves_as_provider(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!",
                "institution": "Stanford CME"
            }
            form = ProviderRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            assert not user.is_clinician
            assert user.is_provider

        def test_valid_form_saves_as_inactive(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!",
                "institution": "Stanford CME"
            }
            form = ProviderRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            assert not user.is_active

        def test_valid_form_creates_provider_profile_with_correct_institution(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!",
                "institution": "Stanford CME"
            }
            form = ProviderRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            profile = ProviderProfile.objects.get(user=user)
            assert profile.institution == "Stanford CME"

        def test_noncommital_save_preserves_access_to_both_unsaved_objects(self):
            """Verify that if the form is saved noncommitally, the programmer can still
            access both the user and the profile to save them without losing data."""
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!",
                "institution": "Stanford CME"
            }
            form = ProviderRegistrationForm(form_data)
            profile = form.save(commit=False)
            assert isinstance(profile, ProviderProfile)
            assert profile.user
            assert profile.user.username == "test-form-username"
