"""Tests for dashboard views."""

import datetime
import re

import pytest

from django.urls import reverse

from commitments.enums import CommitmentStatus
from commitments.models import Commitment, Course
from commitments.tests.helpers import convert_date_to_general_regex


@pytest.mark.django_db
class TestClinicianDashboardView:
    """Tests for ClinicianDashboardView"""

    class TestGet:
        """Tests for ClinicianDashboardView.get"""

        @pytest.fixture(name="commitments_owned_by_saved_clinician_profile")
        def fixture_commitments_owned_by_saved_clinician_profile(self, saved_clinician_profile):
            return (
                Commitment.objects.create(
                    owner=saved_clinician_profile,
                    title="First owned commitment",
                    description="First commitment to test the dashboard with",
                    deadline=datetime.date.today(),
                    status=CommitmentStatus.IN_PROGRESS
                ),
                Commitment.objects.create(
                    owner=saved_clinician_profile,
                    title="Another dashboard commitment",
                    description="Second commitment to test the dashboard with",
                    deadline=datetime.date.today(),
                    status=CommitmentStatus.COMPLETE
                ),
                Commitment.objects.create(
                    owner=saved_clinician_profile,
                    title="Last chance commitment to break the dashboard",
                    description="Third commitment to test the dashboard with",
                    deadline=datetime.date.today(),
                    status=CommitmentStatus.DISCONTINUED
                ),
            )

        @pytest.fixture(name="courses_enrolling_only_saved_clinician_profile")
        def fixture_courses_enrolling_only_saved_clinician_profile(
            self, saved_provider_profile, saved_clinician_profile, enrolled_course
        ):
            courses =  (
                enrolled_course,
                Course.objects.create(
                    owner=saved_provider_profile,
                    title="Second course for the dashboard",
                    description="Only saved_clinician_profile is a student"
                ),
                Course.objects.create(
                    owner=saved_provider_profile,
                    title="This course should show in the dashboard too",
                    description="Only saved_clinician_profile is a student and this is the last one"
                ),
            )
            courses[1].students.add(saved_clinician_profile)
            courses[2].students.add(saved_clinician_profile)
            return courses

        def test_rejects_provider_users_with_403(self, client, saved_provider_profile):
            client.force_login(saved_provider_profile.user)
            response = client.get(reverse("clinician dashboard"))
            assert response.status_code == 403

        def test_all_owned_commitments_show_links_in_page(
            self, client, saved_clinician_profile, commitments_owned_by_saved_clinician_profile
        ):
            client.force_login(saved_clinician_profile.user)
            html = client.get(reverse("clinician dashboard")).content.decode()
            for commitment in commitments_owned_by_saved_clinician_profile:
                commitment_view_url = reverse(
                    "view Commitment",
                    kwargs={"commitment_id": commitment.id}
                )
                commitment_view_link = f"href=\"{commitment_view_url}\""
                assert commitment_view_link in html

        def test_unowned_commitments_do_not_show_in_page(
            self, client, other_clinician_profile, commitments_owned_by_saved_clinician_profile
        ):
            client.force_login(other_clinician_profile.user)
            html = client.get(reverse("clinician dashboard")).content.decode()
            for commitment in commitments_owned_by_saved_clinician_profile:
                commitment_view_url = reverse(
                    "view Commitment",
                    kwargs={"commitment_id": commitment.id}
                )
                commitment_view_link = f"href=\"{commitment_view_url}\""
                assert commitment_view_link not in html
                assert commitment.title not in html

        def test_make_commitment_url_linked_in_page(
            self, client, saved_clinician_profile
        ):
            client.force_login(saved_clinician_profile.user)
            html = client.get(reverse("clinician dashboard")).content.decode()
            make_commitment_url = reverse("create Commitment")
            make_commitment_link = f"href=\"{make_commitment_url}\""
            assert make_commitment_link in html

        def test_all_enrolled_courses_show_links_in_page(
            self, client, saved_clinician_profile, courses_enrolling_only_saved_clinician_profile
        ):
            client.force_login(saved_clinician_profile.user)
            html = client.get(reverse("clinician dashboard")).content.decode()
            for course in courses_enrolling_only_saved_clinician_profile:
                course_view_url = reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
                course_link = f"href=\"{course_view_url}\""
                assert course_link in html

        def test_unenrolled_courses_do_not_show_in_page(
            self, client, other_clinician_profile, courses_enrolling_only_saved_clinician_profile
        ):
            client.force_login(other_clinician_profile.user)
            html = client.get(reverse("clinician dashboard")).content.decode()
            for course in courses_enrolling_only_saved_clinician_profile:
                course_view_url = reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
                course_link = f"href=\"{course_view_url}\""
                assert course_link not in html
                assert course.title not in html


    class TestPost:
        """Tests for ClinicianDashboardView.post"""

        def test_post_rejected_with_405(self, client, saved_clinician_profile):
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                reverse("clinician dashboard"),
                {}
            )
            assert response.status_code == 405


@pytest.mark.django_db
class TestProviderDashboardView:
    """Tests for ProviderDashboardView"""



    class TestGet:
        """Tests for ProviderDashboardView.get"""

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

        def test_provider_dashboard_links_to_create_course(
            self, client, saved_provider_profile,
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            create_course_link = reverse("create course")
            create_course_link_regex = re.compile(
                r"\<a\s[^\>]*href=\"" + create_course_link + r"\"[^\>]*\>"
            )
            assert create_course_link_regex.search(html)

        def test_all_owned_courses_show_links_in_page(
            self, client, saved_provider_profile, courses_owned_by_saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            for course in courses_owned_by_saved_provider_profile:
                course_view_url = reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
                course_link = f"href=\"{course_view_url}\""
                assert course_link in html

        def test_no_unowned_courses_show_in_page(
            self, client, other_provider_profile, courses_owned_by_saved_provider_profile
        ):
            client.force_login(other_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            for course in courses_owned_by_saved_provider_profile:
                course_view_url = reverse(
                    "view course",
                    kwargs={"course_id": course.id}
                )
                course_link = f"href=\"{course_view_url}\""
                assert course_link not in html
                assert course.title not in html

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
                    date_regex = convert_date_to_general_regex(course.start_date)
                    assert date_regex.search(html)

        def test_all_owned_courses_show_existent_end_dates_in_page(
            self, client, saved_provider_profile, courses_owned_by_saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("provider dashboard")).content.decode()
            for course in courses_owned_by_saved_provider_profile:
                if course.end_date:
                    date_regex = convert_date_to_general_regex(course.end_date)
                    assert date_regex.search(html)

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

    class TestPost:
        """Tests for ProviderDashboardView.post"""

        def test_post_rejected_with_405(self, client, saved_provider_profile):
            client.force_login(saved_provider_profile.user)
            response = client.post(
                reverse("provider dashboard"),
                {}
            )
            assert response.status_code == 405
