import re

import pytest

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.core import mail

from cme_accounts.models import User
from cme_accounts.views import ResetPasswordView, ResetPasswordConfirmView


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
class TestSignInView:
    """Tests for SignInView"""

    @pytest.fixture(name="user_to_login")
    def fixture_user_to_login(self):
        # We need to use set_password to generate the pbkdf2 hash that Django uses in its
        # authentication. Otherwise, the login page will always fail. The password attribute
        # is then set to that hash, so we can't use it in requrests - which is why we set the
        # raw_password attribute.
        user = User(
            username="valid user",
            email="fake@email.localhost",
            password="testP@ssw0rd"
        )
        user.set_password(user.password)
        user.save()
        user.raw_password = "testP@ssw0rd"
        return user

    class TestGet:
        """Tests for SignInView.get"""
        def test_shows_post_form_pointing_to_this_view(self, client):
            target_url = reverse("login")
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
            target_url = reverse("login")
            html = client.get(target_url).content.decode()
            assert "name=\"username\"" in html
            assert "name=\"password\"" in html

        def test_shows_link_to_reset_password(self, client):
            target_url = reverse("login")
            html = client.get(target_url).content.decode()
            assert "href=\"" + reverse("reset password") + "\"" in html


    class TestPost:
        """Tests for SignInView.post"""

        def test_invalid_request_shows_get_form_with_error_notes(self, client):
            target_url = reverse("login")
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

        def test_invalid_credentials_show_get_form_with_error_notes(self, client, user_to_login):
            target_url = reverse("login")
            html = client.post(
                target_url,
                {
                    "username": user_to_login.username,
                    "password": user_to_login.raw_password + "wrong"
                }
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)
            error_notes_regex = re.compile(
                r"\<ul[^\>]*class=\"[^\"]*errorlist[^\"]*\"[^\>]*>"
            )
            assert error_notes_regex.search(html)

        def test_invalid_credentials_do_not_log_in_user(self, client, user_to_login):
            target_url = reverse("login")
            client.post(
                target_url,
                {
                    "username": user_to_login.username,
                    "password": user_to_login.raw_password + "wrong"
                }
            )
            # Django does not have a nice way to check if the user is logged in from a client
            # request. This will have to do.
            assert not "_auth_user_id" in client.session

        def test_valid_login_does_log_in_user(self, client, user_to_login):
            target_url = reverse("login")
            client.post(
                target_url,
                {
                    "username": user_to_login.username,
                    "password": user_to_login.raw_password
                }
            )
            # Django does not have a nice way to check if the user is logged in from a client
            # request. This will have to do.
            assert "_auth_user_id" in client.session
            assert int(client.session["_auth_user_id"]) == user_to_login.id


@pytest.mark.django_db
class TestSignOutView:
    """Tests for SignOutView"""

    @pytest.fixture(name="valid_user")
    def fixture_valid_user(self):
        return User.objects.create(
            username="username",
            email="a@b.localhost",
            password="password"
        )

    class TestGet:
        """Tests for SignOutView.get

        get is disallowed by Django. The only test here verifies that it returns an appropriate error.
        """

        def test_get_returns_405(self, client, valid_user):
            target_url = reverse("logout")
            client.force_login(valid_user)
            response = client.get(target_url)
            assert response.status_code == 405


    class TestPost:
        """Tests for SignOutView.post"""

        def test_post_request_logs_out(self, client, valid_user):
            client.force_login(valid_user)
            client.post(reverse("logout"))
            # Django does not have a nice way to check if the user is logged in from a client
            # request. This will have to do.
            assert "_auth_user_id" not in client.session

        def test_post_request_returns_page_indicating_logout(self, client, valid_user):
            client.force_login(valid_user)
            html = client.post(reverse("logout")).content.decode()
            assert "You have successfully logged out" in html


@pytest.mark.django_db
class TestResetPasswordView:
    """Tests for ResetPasswordView"""

    class TestGet:
        """Tests for ResetPasswordView.get

        Even though we do not override this method, we should verify that the templates render
        correctly for the users."""

        def test_shows_post_form_pointing_to_this_view(self, client):
            target_url = reverse("reset password")
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
            target_url = reverse("reset password")
            html = client.get(target_url).content.decode()
            assert "name=\"email\"" in html


    class TestPost:
        """Tests for ResetPasswordView.post

        Even though we do not override this method, we should verify that the templates render
        correctly for the users."""

        @pytest.fixture(name="user_to_reset")
        def fixture_user_to_reset(self):
            return User.objects.create(
                username="username",
                email="test@email.localhost",
                password="password"
            )

        def test_invalid_request_returns_the_get_page_with_error_notes(self, client):
            target_url = reverse("reset password")
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

        def test_valid_request_sends_email_with_valid_reset_link(
            self, client, user_to_reset, captured_email
        ):
            target_url = reverse("reset password")
            client.post(
                target_url,
                {"email": user_to_reset.email}
            )
            assert len(captured_email) == 1
            reset_mail = captured_email[0]
            assert reset_mail.to == ["test@email.localhost"]
            site_hostname_regex = r"https?\:\/\/[\w\.\:]*"
            # uidb64 is always base64, token is always base36, so these regexes will work.
            relative_url_regex = reverse(
                "confirm reset password",
                kwargs={
                    "uidb64": "UIDB64",
                    "token": "TOKEN"
                }
            ).replace("UIDB64", r"([\w\%\-]+)").replace("TOKEN", r"([\w\-]+)")
            reset_link_regex = re.compile(
                site_hostname_regex + relative_url_regex
            )
            match = reset_link_regex.search(reset_mail.body)
            assert match
            sent_token = match.group(2)
            # Verify the token is valid using the class used to generate it.
            # We can't guarantee the other view will work fine so it is better to verify that
            # in the consistency checks while verifying only that this view thinks it is OK.
            assert ResetPasswordView.token_generator.check_token(user_to_reset, sent_token)


        def test_valid_request_redirects_to_awaiting_email_url(
            self, client, user_to_reset, captured_email #pylint: disable=unused-argument
        ):
            target_url = reverse("reset password")
            response = client.post(
                target_url,
                {"email": user_to_reset.email}
            )
            assert response.status_code == 302
            assert response.url == reverse("awaiting reset email")


class TestAwaitingResetEmailViewView:
    """Tests for AwaitingResetEmailViewView"""

    def test_get_returns_correct_page(self, client):
        response = client.get(reverse("awaiting reset email"))
        assert response.status_code == 200
        html = response.content.decode()
        assert "Password reset email sent" in html


@pytest.mark.django_db
class TestResetPasswordConfirmView:
    """Tests for ResetPasswordConfirmView"""

    @pytest.fixture(name="user_to_reset")
    def fixture_user_to_reset(self):
        return User.objects.create(
            username="username",
            email="test@email.localhost",
            password="password"
        )

    @pytest.fixture(name="valid_reset_url_kwargs")
    def fixture_valid_reset_url_kwargs(self, user_to_reset):
        # We don't want to depend on the output of PasswordResetView outside of consistency
        # tests. Instead, because we inherit from PasswordResetConfirmView, we can use the
        # methods that the view uses to generate a token.
        uidb64 = urlsafe_base64_encode(force_bytes(user_to_reset.pk))
        token = ResetPasswordConfirmView.token_generator.make_token(user_to_reset)
        return {
            "uidb64": uidb64,
            "token": token
        }


    class TestGet:
        """Tests for ResetPasswordConfirmView.get

        Even though we do not override this method, we should verify that the templates render
        correctly for the users."""

        def test_invalid_uid_returns_error_and_no_form(self, client, valid_reset_url_kwargs):
            target_url = reverse(
                "confirm reset password",
                kwargs={
                    "uidb64": "B",
                    "token": valid_reset_url_kwargs["token"]
                }
            )
            # Django does a redirect in this view for security reasons and we should follow.
            html = client.get(target_url, follow=True).content.decode()
            assert "<form" not in html
            assert "Invalid token" in html

        def test_invalid_token_returns_error_and_no_form(self, client, valid_reset_url_kwargs):
            target_url = reverse(
                "confirm reset password",
                kwargs={
                    "uidb64": valid_reset_url_kwargs["uidb64"],
                    "token": "%%%%"
                }
            )
            # Django does a redirect in this view for security reasons and we should follow.
            html = client.get(target_url, follow=True).content.decode()
            assert "<form" not in html
            assert "Invalid token" in html

        def test_shows_post_form_pointing_to_this_view(self, client, valid_reset_url_kwargs):
            target_url = reverse(
                "confirm reset password",
                kwargs=valid_reset_url_kwargs
            )
            # Django does a redirect in this view for security reasons and we should follow.
            html = client.get(target_url, follow=True).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*method=\"(post|POST)\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            # Django messes with the urls, which makes manually setting the action attribute of
            # the form ill-advised. Verify it is not present instead of verify the value.
            assert "action=\"" not in match.group()

        def test_shows_required_form_fields(self, client, valid_reset_url_kwargs):
            target_url = reverse(
                "confirm reset password",
                kwargs=valid_reset_url_kwargs
            )
            # Django does a redirect in this view for security reasons and we should follow.
            html = client.get(target_url, follow=True).content.decode()
            assert "name=\"new_password1\"" in html
            assert "name=\"new_password2\"" in html

    class TestPost:
        """Tests for ResetPasswordConfirmView.post

        Even though we do not override this method, we should verify that the templates render
        correctly for the users."""

        def test_invalid_post_data_shows_get_with_error_messages(
            self, client, valid_reset_url_kwargs
        ):
            get_url = reverse(
                "confirm reset password",
                kwargs=valid_reset_url_kwargs
            )
            # Django does a redirect in the get view for security reasons, storing data in
            # the session key for a post. We need to do this and use the redirected url or
            # things will not work.
            target_url = client.get(get_url).url
            html = client.post(
                target_url,
                {
                    "new_password1": "p@ssword17",
                    "new_password2": "does_not_match"
                }
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*method=\"(post|POST)\"[^\>]*\>"
            )
            assert form_regex.search(html)
            error_notes_regex = re.compile(
                r"\<ul[^\>]*class=\"[^\"]*errorlist[^\"]*\"[^\>]*>"
            )
            assert error_notes_regex.search(html)

        def test_valid_post_data_resets_password(
            self, client, user_to_reset, valid_reset_url_kwargs
        ):
            get_url = reverse(
                "confirm reset password",
                kwargs=valid_reset_url_kwargs
            )
            # Django does a redirect in the get view for security reasons, storing data in
            # the session key for a post. We need to do this and use the redirected url or
            # things will not work.
            target_url = client.get(get_url).url
            client.post(
                target_url,
                {
                    "new_password1": "p@ssword17",
                    "new_password2": "p@ssword17"
                }
            )
            assert client.login(username=user_to_reset.username, password="p@ssword17")

        def test_valid_post_data_redirects_correctly(self, client, valid_reset_url_kwargs):
            get_url = reverse(
                "confirm reset password",
                kwargs=valid_reset_url_kwargs
            )
            # Django does a redirect in the get view for security reasons, storing data in
            # the session key for a post. We need to do this and use the redirected url or
            # things will not work.
            target_url = client.get(get_url).url
            response = client.post(
                target_url,
                {
                    "new_password1": "p@ssword17",
                    "new_password2": "p@ssword17"
                }
            )
            assert response.status_code == 302
            assert response.url == reverse("password reset complete")


class TestResetPasswordCompleteView:
    """Tests for ResetPasswordCompleteView"""

    def test_get_returns_correct_page(self, client):
        response = client.get(reverse("password reset complete"))
        assert response.status_code == 200
        html = response.content.decode()
        assert "Password reset complete" in html


class TestConsistencyInPasswordReset:
    """Tests that the password reset cycle works as a whole"""

    @pytest.fixture(name="user_to_reset")
    def fixture_user_to_reset(self):
        return User.objects.create(
            username="username",
            email="test@email.localhost",
            password="password"
        )

    def test_both_password_reset_form_views_share_same_token_generator(self):
        """If the two views do not have the same token generator, then tokens generated
        by one will likely be invalid for the other. They should be the same, or else 
        we should not be inheriting from Django's authentication views."""
        assert ResetPasswordView.token_generator == ResetPasswordConfirmView.token_generator

    @pytest.mark.django_db
    def test_password_reset_cycle_works_via_views(self, client, user_to_reset, captured_email):
        # Make sure this doesn't pass due to a bug in our login.
        assert not client.login(username=user_to_reset.username, password="p@ssword17")
        client.post(
            reverse("reset password"),
            {"email": user_to_reset.email}
        )
        site_hostname_regex = r"https?\:\/\/[\w\.\:]*"
        # uidb64 is always base64, token is always base36, so these regexes will work.
        relative_url_regex = reverse(
            "confirm reset password",
            kwargs={
                "uidb64": "UIDB64",
                "token": "TOKEN"
                }
        ).replace("UIDB64", r"[\w\%\-]+").replace("TOKEN", r"[\w\-]+")
        reset_link_regex = re.compile(
            site_hostname_regex + "(" + relative_url_regex + ")"
        )
        reset_confirm_get_url = reset_link_regex.search(captured_email[0].body).group()
        # Django does a redirect in the get view for security reasons, storing data in
        # the session key for a post. We need to do this and use the redirected url or
        # things will not work.
        reset_confirm_post_url = client.get(reset_confirm_get_url).url
        client.post(
            reset_confirm_post_url,
            {
                "new_password1": "p@ssword17",
                "new_password2": "p@ssword17"
            }
        )
        assert client.login(username=user_to_reset.username, password="p@ssword17")
