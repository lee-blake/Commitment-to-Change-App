"""Tests for dashboard views."""

import datetime
import re

import pytest

from django.urls import reverse

from commitments.models import Course


@pytest.mark.django_db
class TestProviderDashboardView:
    """Tests for ProviderDashboardView"""



    class TestGet:
        """Tests for ProviderDashboardView.get"""

        # TODO This is very definitely a duplicate of a fixture of the same name
        # in another testing branch. This one should supercede the other because
        # it contains extra fields for dashboard testing.
        @pytest.fixture(name="courses_owned_by_saved_provider_profile")
        def fixture_courses_owned_by_saved_provider_profile(
            self, saved_provider_profile, enrolled_course
        ):
            return (
                enrolled_course,
                Course.objects.create(
                    owner=saved_provider_profile,
                    title="Owned course for testing provider dashboard",
                    description="This should show in the dashboard",
                    identifier="OWNED2",
                    start_date=datetime.date.fromisoformat("1900-01-01")
                ),
                Course.objects.create(
                    owner=saved_provider_profile,
                    title="Another course for testing provider dashboard",
                    description="This should also show in the dashboard",
                    end_date=datetime.date.fromisoformat("2021-06-01")
                ),
            )

        # TODO Add tests to cover all Iteration 1 functionality
        # The tests I have added here only cover new code and adding those tests would
        # make this feature branch even more cumbersome than it is already. - Lee

        def test_all_owned_courses_show_existent_unique_identifiers_in_page(
            self, client, saved_provider_profile, courses_owned_by_saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            for course in courses_owned_by_saved_provider_profile:
                if course.identifier:
                    assert course.identifier in html

        def test_all_owned_courses_show_existent_start_dates_in_page(
            self, client, saved_provider_profile, courses_owned_by_saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            for course in courses_owned_by_saved_provider_profile:
                if course.start_date:
                    # TODO this should be replaced with a more robust regex scraping of dates.
                    iso_format = str(course.start_date)
                    slash_format = course.start_date.strftime("%-m/%-d/%Y")
                    spelled_month_format = course.start_date.strftime("%B %-d, %Y")
                    short_month_format = course.start_date.strftime("%b. %-d, %Y")
                    assert iso_format in html \
                        or slash_format in html \
                        or spelled_month_format in html \
                        or short_month_format in html

        def test_all_owned_courses_show_existent_end_dates_in_page(
            self, client, saved_provider_profile, courses_owned_by_saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            for course in courses_owned_by_saved_provider_profile:
                if course.end_date:
                    # TODO this should be replaced with a more robust regex scraping of dates.
                    iso_format = str(course.end_date)
                    slash_format = course.end_date.strftime("%-m/%-d/%Y")
                    spelled_month_format = course.end_date.strftime("%B %-d, %Y")
                    short_month_format = course.end_date.strftime("%b. %-d, %Y")
                    assert iso_format in html \
                        or slash_format in html \
                        or spelled_month_format in html \
                        or short_month_format in html

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
