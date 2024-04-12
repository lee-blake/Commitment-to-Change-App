import re

import pytest

from django.urls import reverse

from commitments.models import ClinicianProfile


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
