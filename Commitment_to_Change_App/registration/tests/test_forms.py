import pytest

from cme_accounts.models import User
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


    class TestSave:
        """Tests for ProviderRegistrationForm.save"""

        def test_valid_form_only_saves_as_provider(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!"
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
                "password2": "passw0rd!"
            }
            form = ProviderRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            assert not user.is_active

        def test_valid_form_creates_provider_profile(self):
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!"
            }
            form = ProviderRegistrationForm(form_data)
            form.save()
            user = User.objects.get(username="test-form-username")
            assert ProviderProfile.objects.filter(user=user).exists()

        def test_noncommital_save_preserves_access_to_both_unsaved_objects(self):
            """Verify that if the form is saved noncommitally, the programmer can still
            access both the user and the profile to save them without losing data."""
            form_data = {
                "username": "test-form-username",
                "email": "email@test.email",
                "password1": "passw0rd!",
                "password2": "passw0rd!"
            }
            form = ProviderRegistrationForm(form_data)
            profile = form.save(commit=False)
            assert isinstance(profile, ProviderProfile)
            assert profile.user
            assert profile.user.username == "test-form-username"
