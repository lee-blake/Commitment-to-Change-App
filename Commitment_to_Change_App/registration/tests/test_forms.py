import pytest

from cme_accounts.models import User
from registration.forms import ClinicianRegistrationForm, ProviderRegistrationForm


@pytest.mark.django_db
class TestClinicianRegistrationForm:
    """Tests for ClinicianRegistrationForm"""

    class TestInit:
        """Tests for ClinicianRegistrationForm.__init__"""

        def test_instance_is_marked_as_clinician(self):
            form = ClinicianRegistrationForm()
            assert form.instance.is_clinician

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


@pytest.mark.django_db
class TestProviderRegistrationForm:
    """Tests for ProviderRegistrationForm"""

    class TestInit:
        """Tests for ProviderRegistrationForm.__init__"""

        def test_instance_is_marked_as_provider(self):
            form = ProviderRegistrationForm()
            assert form.instance.is_provider

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
