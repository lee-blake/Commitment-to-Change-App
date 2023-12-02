"""Tests for dashboard views."""

import re

import pytest

from django.urls import reverse


@pytest.mark.django_db
class TestProviderDashboardView:
    """Tests for ProviderDashboardView"""

    class TestGet:
        """Tests for ProviderDashboardView.get"""

        # TODO Add tests to cover all Iteration 1 functionality
        # The tests I have added here only cover new code and adding those tests would
        # make this feature branch even more cumbersome than it is already. - Lee

        def test_provider_dashboard_links_to_create_commitment_template(
            self, client, saved_provider_profile,
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            create_commitment_template_link = reverse("create CommitmentTemplate")
            create_commitment_template_link_regex = re.compile(
                r"\<a\s[^\>]*href=\"" + create_commitment_template_link + r"\"[^\>]*\>"
            )
            assert create_commitment_template_link_regex.search(html)

        def test_provider_dashboard_lists_commitment_templates(
            self, client, saved_provider_profile, commitment_template_1, commitment_template_2
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            assert commitment_template_1.title in html
            assert commitment_template_2.title in html

        def test_provider_dashboard_links_to_commitment_templates(
            self, client, saved_provider_profile, commitment_template_1, commitment_template_2
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            commitment_template_1_view_link = reverse(
                "view CommitmentTemplate",
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
            commitment_template_1_link_regex = re.compile(
                r"\<a\s[^\>]*href=\"" + commitment_template_1_view_link + r"\"[^\>]*\>"
            )
            assert commitment_template_1_link_regex.search(html)
            commitment_template_2_view_link = reverse(
                "view CommitmentTemplate",
                kwargs={"commitment_template_id": commitment_template_2.id}
            )
            commitment_template_2_link_regex = re.compile(
                r"\<a\s[^\>]*href=\"" + commitment_template_2_view_link + r"\"[^\>]*\>"
            )
            assert commitment_template_2_link_regex.search(html)
