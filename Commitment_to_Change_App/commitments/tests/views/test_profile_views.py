import re

import pytest

from django.urls import reverse

from cme_accounts.models import User
from commitments.models import ClinicianProfile, ProviderProfile


@pytest.mark.django_db
class TestProfileRedirectingView:
    """Tests for ProfileRedirectingView"""

    class TestGet:
        """Tests for ProfileRedirectingView.get"""

        def test_clinician_user_gets_clinician_profile_redirect(
            self, client, saved_clinician_profile
        ):
            target_url = reverse("view Profile")
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 302
            assert response.url == reverse("view ClinicianProfile")

        def test_provider_user_gets_provider_profile_redirect(
            self, client, saved_provider_profile
        ):
            target_url = reverse("view Profile")
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 302
            assert response.url == reverse("view ProviderProfile")

        def test_non_clinician_or_provider_user_gets_server_error(
            self, client
        ):
            target_url = reverse("view Profile")
            neither_type_user = User.objects.create(
                username="neither",
                email="neither@localhost",
                password="p@ssword11"
            )
            # Tell the Django client return 500 instead of reraising the exception
            client.raise_request_exception = False
            client.force_login(neither_type_user)
            response = client.get(target_url)
            assert response.status_code == 500


    class TestPost:
        """Tests for ProfileRedirectingView.post
        
        post is not defined, tests exist to make sure it does not have unexpected functionality."""

        def test_post_returns_405(self, client, saved_provider_profile):
            target_url = reverse("view Profile")
            client.force_login(saved_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 405


@pytest.mark.django_db
class TestViewClinicianProfileView:
    """Tests for ViewClinicianProfileView"""

    class TestGet:
        """Tests for ViewClinicianProfileView.get"""

        def test_rejects_provider_accounts_with_403(self, client, saved_provider_user):
            target_url = reverse("view ClinicianProfile")
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        @pytest.mark.parametrize(
            "names",
            [("TestFirst", "TestLast"), ("SecondFormer", "SecondLatter")]
        )
        def test_shows_name_fields(self, client, saved_clinician_user, names):
            first_name = names[0]
            last_name = names[1]
            ClinicianProfile.objects.create(
                user=saved_clinician_user,
                first_name=first_name,
                last_name=last_name
            )
            target_url = reverse("view ClinicianProfile")
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            assert first_name in html
            assert last_name in html

        @pytest.mark.parametrize("institution", ["TestInstitution", "SecondProvider"])
        def test_shows_institution_field(self, client, saved_clinician_user, institution):
            ClinicianProfile.objects.create(
                user=saved_clinician_user,
                institution=institution
            )
            target_url = reverse("view ClinicianProfile")
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            assert institution in html

        def test_empty_fields_give_not_provided_instead_of_blank(
            self, client, saved_clinician_user
        ):
            ClinicianProfile.objects.create(
                user=saved_clinician_user
            )
            target_url = reverse("view ClinicianProfile")
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            not_provided_matches = re.compile(
                r"(N|n)ot\s+provided"
            ).findall(html)
            assert len(not_provided_matches) == 3

        def test_not_provided_does_not_show_if_all_fields_provided(
            self, client, saved_clinician_user
        ):
            ClinicianProfile.objects.create(
                user=saved_clinician_user,
                first_name="first",
                last_name="last",
                institution="institution"
            )
            target_url = reverse("view ClinicianProfile")
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            not_provided_matches = re.compile(
                r"(N|n)ot\s+provided"
            ).search(html)
            assert not not_provided_matches

        def test_links_to_change_password_page(
            self, client, saved_clinician_profile
        ):
            target_url = reverse("view ClinicianProfile")
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            link_url = reverse("change password")
            assert link_url in html


    class TestPost:
        """Tests for ViewClinicianProfileView.post"""

        def test_rejects_post_with_405(
            self, client, saved_clinician_profile
        ):
            client.force_login(saved_clinician_profile.user)
            target_url = reverse("view ClinicianProfile")
            response = client.post(
                target_url, {}
            )
            assert response.status_code == 405


@pytest.mark.django_db
class TestEditClinicianProfileView:
    """Tests for EditClinicianProfileView"""

    class TestGet:
        """Tests for EditClinicianProfileView.get"""


        def test_rejects_provider_account_with_403(
            self, client, saved_provider_profile
        ):
            target_url = reverse(
                "edit ClinicianProfile"
            )
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_shows_post_form_pointing_to_this_view(
            self, client, saved_clinician_profile
        ):
            target_url = reverse(
                "edit ClinicianProfile"
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        @pytest.mark.parametrize(
            "names",
            [("TestFirst", "TestLast"), ("SecondFormer", "SecondLatter")]
        )
        def test_name_fields_are_filled_by_default(
            self, client, saved_clinician_profile, names
        ):
            first_name = names[0]
            last_name = names[1]
            saved_clinician_profile.first_name = first_name
            saved_clinician_profile.last_name = last_name
            saved_clinician_profile.save()
            target_url = reverse(
                "edit ClinicianProfile"
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            first_name_input_regex = re.compile(
                r"\<input[^\>]*name=\"first_name\"[^\>]*\>"
            )
            first_name_input_match = first_name_input_regex.search(html)
            assert first_name_input_match
            assert f"value=\"{first_name}\"" in first_name_input_match[0]
            last_name_input_regex = re.compile(
                r"\<input[^\>]*name=\"last_name\"[^\>]*\>"
            )
            last_name_input_match = last_name_input_regex.search(html)
            assert last_name_input_match
            assert f"value=\"{last_name}\"" in last_name_input_match[0]

        @pytest.mark.parametrize("institution", ["TestInstitution", "SecondProvider"])
        def test_institution_field_is_filled_by_default(
            self, client, saved_clinician_profile, institution
        ):
            saved_clinician_profile.institution = institution
            saved_clinician_profile.save()
            target_url = reverse(
                "edit ClinicianProfile"
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            institution_input_regex = re.compile(
                r"\<input[^\>]*name=\"institution\"[^\>]*\>"
            )
            institution_input_match = institution_input_regex.search(html)
            assert institution_input_match
            assert f"value=\"{institution}\"" in institution_input_match[0]


    class TestPost:
        """Tests for EditClinicianProfileView.post"""

        def test_rejects_provider_account_with_403(
            self, client, saved_provider_profile
        ):
            target_url = reverse(
                "edit ClinicianProfile"
            )
            client.force_login(saved_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_valid_request_alters_clinician_profile(
            self, client, saved_clinician_profile
        ):
            saved_clinician_profile.first_name = "old first name"
            saved_clinician_profile.last_name = "old last name"
            saved_clinician_profile.institution = "old institution"
            target_url = reverse(
                "edit ClinicianProfile"
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "first_name": "new first name",
                    "last_name": "new last name",
                    "institution": "new institution"
                }
            )
            reloaded_clinician_profile = ClinicianProfile.objects.get(
                id=saved_clinician_profile.id
            )
            assert reloaded_clinician_profile.first_name == "new first name"
            assert reloaded_clinician_profile.last_name == "new last name"
            assert reloaded_clinician_profile.institution == "new institution"

        def test_valid_request_redirects_correctly(
            self, client, saved_clinician_profile
        ):
            target_url = reverse(
                "edit ClinicianProfile"
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {
                    "first_name": "new first name",
                    "last_name": "new last name",
                    "institution": "new institution"
                }
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view ClinicianProfile",
            )


@pytest.mark.django_db
class TestViewProviderProfileView:
    """Tests for ViewProviderProfileView"""

    class TestGet:
        """Tests for ViewProviderProfileView.get"""

        def test_rejects_clinician_accounts_with_403(self, client, saved_clinician_user):
            target_url = reverse("view ProviderProfile")
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        @pytest.mark.parametrize("institution", ["TestInstitution", "SecondProvider"])
        def test_shows_institution_field(self, client, saved_provider_user, institution):
            ProviderProfile.objects.create(
                user=saved_provider_user,
                institution=institution
            )
            target_url = reverse("view ProviderProfile")
            client.force_login(saved_provider_user)
            html = client.get(target_url).content.decode()
            assert institution in html

        def test_links_to_change_password_page(
            self, client, saved_provider_profile
        ):
            target_url = reverse("view ProviderProfile")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            link_url = reverse("change password")
            assert link_url in html


    class TestPost:
        """Tests for ViewProviderProfileView.post"""

        def test_rejects_post_with_405(
            self, client, saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            target_url = reverse("view ProviderProfile")
            response = client.post(
                target_url, {}
            )
            assert response.status_code == 405
