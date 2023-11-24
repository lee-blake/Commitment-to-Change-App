import re

import pytest

from django.core import mail
from django.shortcuts import reverse

from django_registration.backends.activation.views import ActivationView, RegistrationView

from cme_accounts.models import User
from commitments.models import ClinicianProfile, ProviderProfile


@pytest.fixture(name="captured_email")
def fixture_captured_email(settings):
    """This fixture ensures that Django uses the memory backend for email during tests. 
    If a test case will send an email, you should call this to ensure email is not sent
    out incorrectly.
    """
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    # This attribute does exist if the locmem backend is set - Django sets it at runtime.
    return mail.outbox #pylint: disable=no-member


@pytest.mark.django_db
class TestRegisterClinicianView:
    """Tests for RegisterClinicianView"""

    class TestGet:
        """Tests for RegisterClinicianView.get

        Even though we do not override this method, we should verify that the templates render
        correctly for the users."""

        def test_shows_post_form_pointing_to_this_view(self, client):
            target_url = reverse("register clinician")
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        def test_shows_required_form_fields(self, client):
            target_url = reverse("register clinician")
            html = client.get(target_url).content.decode()
            assert "name=\"username\"" in html
            assert "name=\"email\"" in html
            assert "name=\"password1\"" in html
            assert "name=\"password2\"" in html


    class TestPost:
        """Tests for RegisterClinicianView.post

        Even though we do not override this method, we test RegisterClinicianView.register through 
        this method because RegisterClinicianView.register requires a request."""

        def test_invalid_request_returns_the_get_page_with_error_notes(self, client):
            target_url = reverse("register clinician")
            html = client.post(
                target_url,
                {}
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)
            error_notes_regex = re.compile(
                r"\<ul[^\>]*class=\"[^\"]*errorlist[^\"]*\"[^\>]*>"
            )
            assert error_notes_regex.search(html)

        def test_valid_request_creates_inactive_clinician_user_with_profile(
            self, client, captured_email #pylint: disable=unused-argument
        ):
            target_url = reverse("register clinician")
            client.post(
                target_url,
                {
                    "username": "valid_username",
                    "email": "valid@email.localhost",
                    "password1": "passw0rd!",
                    "password2": "passw0rd!"
                }
            )
            user = User.objects.get(username="valid_username")
            assert not user.is_active
            assert user.is_clinician
            assert ClinicianProfile.objects.filter(user=user).exists()

        def test_valid_request_sends_email_with_verification_link(self, client, captured_email):
            target_url = reverse("register clinician")
            client.post(
                target_url,
                {
                    "username": "valid_username",
                    "email": "valid@email.localhost",
                    "password1": "passw0rd!",
                    "password2": "passw0rd!"
                }
            )
            assert len(captured_email) == 1
            assert captured_email[0].to == ["valid@email.localhost"]
            site_hostname_regex = r"https?\:\/\/[\w\.\:]*"
            relative_url_regex = reverse(
                "activate account",
                kwargs={"activation_key": "NEVER-APPEARS-IN-ANY-URL"}
            ).replace("NEVER-APPEARS-IN-ANY-URL", r"([\w\:\-]+)")
            activation_link_regex = re.compile(
                site_hostname_regex + relative_url_regex
            )
            match = activation_link_regex.search(captured_email[0].body)
            assert match
            activation_key = match.group(1)
            try:
                # We don't want to depend on an entire ActivationView object for our test.
                # Calling with a None works fine if the key is valid and throws an AttributeError
                # if it is not. In this way, we can validate the code without potentially
                # touching the database again.
                validated_username = ActivationView.validate_key(None, activation_key)
                assert validated_username == "valid_username"
            except AttributeError:
                raise ValueError( # pylint: disable=raise-missing-from
                    "The email link was not a valid activation link!"
                )

        def test_valid_request_redirects_to_awaiting_activation_page(
            self, client, captured_email #pylint: disable=unused-argument
        ):
            target_url = reverse("register clinician")
            response = client.post(
                target_url,
                {
                    "username": "valid_username",
                    "email": "valid@email.localhost",
                    "password1": "passw0rd!",
                    "password2": "passw0rd!"
                }
            )
            assert response.status_code == 302
            assert response.url == reverse("awaiting activation")


@pytest.mark.django_db
class TestRegisterProviderView:
    """Tests for RegisterProviderView"""

    class TestGet:
        """Tests for RegisterProviderView.get

        Even though we do not override this method, we should verify that the templates render
        correctly for the users."""

        def test_shows_post_form_pointing_to_this_view(self, client):
            target_url = reverse("register provider")
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        def test_shows_required_form_fields(self, client):
            target_url = reverse("register provider")
            html = client.get(target_url).content.decode()
            assert "name=\"username\"" in html
            assert "name=\"email\"" in html
            assert "name=\"password1\"" in html
            assert "name=\"password2\"" in html


    class TestPost:
        """Tests for RegisterProviderView.post

        Even though we do not override this method, we test RegisterProviderView.register through 
        this method because RegisterProviderView.register requires a request."""

        def test_invalid_request_returns_the_get_page_with_error_notes(self, client):
            target_url = reverse("register provider")
            html = client.post(
                target_url,
                {}
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)
            error_notes_regex = re.compile(
                r"\<ul[^\>]*class=\"[^\"]*errorlist[^\"]*\"[^\>]*>"
            )
            assert error_notes_regex.search(html)

        def test_valid_request_creates_inactive_provider_user_with_profile(
            self, client, captured_email #pylint: disable=unused-argument
        ):
            target_url = reverse("register provider")
            client.post(
                target_url,
                {
                    "username": "valid_username",
                    "email": "valid@email.localhost",
                    "password1": "passw0rd!",
                    "password2": "passw0rd!"
                }
            )
            user = User.objects.get(username="valid_username")
            assert not user.is_active
            assert user.is_provider
            assert ProviderProfile.objects.filter(user=user).exists()

        def test_valid_request_sends_email_with_verification_link(self, client, captured_email):
            target_url = reverse("register provider")
            client.post(
                target_url,
                {
                    "username": "valid_username",
                    "email": "valid@email.localhost",
                    "password1": "passw0rd!",
                    "password2": "passw0rd!"
                }
            )
            assert len(captured_email) == 1
            assert captured_email[0].to == ["valid@email.localhost"]
            site_hostname_regex = r"https?\:\/\/[\w\.\:]*"
            relative_url_regex = reverse(
                "activate account",
                kwargs={"activation_key": "NEVER-APPEARS-IN-ANY-URL"}
            ).replace("NEVER-APPEARS-IN-ANY-URL", r"(?P<activation_key>[\w\:\-]+)")
            activation_link_regex = re.compile(
                site_hostname_regex + relative_url_regex
            )
            match = activation_link_regex.search(captured_email[0].body)
            assert match
            activation_key = match.group(1)
            try:
                # We don't want to depend on an entire ActivationView object for our test.
                # Calling with a None works fine if the key is valid and throws an AttributeError
                # if it is not. In this way, we can validate the code without potentially
                # touching the database again.
                validated_username = ActivationView.validate_key(None, activation_key)
                assert validated_username == "valid_username"
            except AttributeError:
                raise ValueError( # pylint: disable=raise-missing-from
                    "The email link was not a valid activation link!"
                )

        def test_valid_request_redirects_to_awaiting_activation_page(
            self, client, captured_email #pylint: disable=unused-argument
        ):
            target_url = reverse("register provider")
            response = client.post(
                target_url,
                {
                    "username": "valid_username",
                    "email": "valid@email.localhost",
                    "password1": "passw0rd!",
                    "password2": "passw0rd!"
                }
            )
            assert response.status_code == 302
            assert response.url == reverse("awaiting activation")


@pytest.mark.django_db
class TestActivateAccountView:
    """Tests for ActivateAccountView"""

    class TestGet:
        """Tests for ActivateAccountView.get"""

        @pytest.fixture(name="inactive_user")
        def fixture_inactive_user(self):
            return User.objects.create(
                username="test_username",
                email="test@email.localhost",
                password="password",
                is_active=False
            )

        @pytest.fixture(name="valid_activation_key")
        def fixture_valid_activation_key(self, inactive_user):
            # We only need to get a key here, so we don't actually create a RegistrationView
            # object and instead pass None.
            return RegistrationView.get_activation_key(None, inactive_user)

        @pytest.fixture(name="expired_activation_key")
        def fixture_expired_activation_key(self, settings, valid_activation_key):
            # All keys will expire with this setting.
            settings.ACCOUNT_ACTIVATION_DAYS = 0
            return valid_activation_key

        def test_valid_key_activates_user(self, client, inactive_user, valid_activation_key):
            target_url = reverse(
                "activate account",
                kwargs={"activation_key": valid_activation_key}
            )
            client.get(target_url)
            reloaded_user = User.objects.get(id=inactive_user.id)
            assert reloaded_user.is_active

        def test_valid_key_redirects_correctly(self, client, valid_activation_key):
            target_url = reverse(
                "activate account",
                kwargs={"activation_key": valid_activation_key}
            )
            response = client.get(target_url)
            assert response.status_code == 302
            assert response.url == reverse("activation complete")

        def test_expired_key_returns_an_appropriate_message(
            self, client, expired_activation_key
        ):
            target_url = reverse(
                "activate account",
                kwargs={"activation_key": expired_activation_key}
            )
            html = client.get(target_url).content.decode()
            assert "Activation Failed" in html
            assert "expired" in html

        def test_invalid_key_returns_an_appropriate_message(
            self, client
        ):
            target_url = reverse(
                "activate account",
                kwargs={"activation_key": "this-is-not-a-key"}
            )
            html = client.get(target_url).content.decode()
            assert "Activation Failed" in html
            assert "invalid" in html and "activation key" in html

        def test_bad_username_returns_an_appropriate_message(
            self, client, inactive_user, valid_activation_key
        ):
            # Deleting the user will make the key contain a bad (nonexistent) username.
            inactive_user.delete()
            target_url = reverse(
                "activate account",
                kwargs={"activation_key": valid_activation_key}
            )
            html = client.get(target_url).content.decode()
            assert "Activation Failed" in html
            assert "invalid" in html and "account" in html

        def test_already_activated_returns_an_appropriate_message(
            self, client, inactive_user, valid_activation_key
        ):
            inactive_user.is_active = True
            inactive_user.save()
            target_url = reverse(
                "activate account",
                kwargs={"activation_key": valid_activation_key}
            )
            html = client.get(target_url).content.decode()
            assert "Activation Failed" in html
            assert "already been activated" in html
