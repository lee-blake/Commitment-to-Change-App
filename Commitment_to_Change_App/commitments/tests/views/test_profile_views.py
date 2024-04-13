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
