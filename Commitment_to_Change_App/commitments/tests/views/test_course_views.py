"""Tests for views relating to Course objects."""

import csv
import datetime
import io
import re

import pytest

from django.urls import reverse

from commitments.enums import CommitmentStatus
from commitments.models import Commitment, Course


@pytest.mark.django_db
class TestCreateCourseView:
    """Tests for CreateCourseView"""

    class TestGet:
        """Tests for CreateCourseView.get"""

        def test_rejects_clinician_accounts_with_403(self, client, saved_clinician_user):
            client.force_login(saved_clinician_user)
            response = client.get(
                reverse("create Course")
            )
            assert response.status_code == 403

        def test_shows_post_form_pointing_to_this_view(self, client, saved_provider_user):
            target_url = reverse("create Course")
            client.force_login(saved_provider_user)
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        def test_shows_required_title_field(self, client, saved_provider_user):
            target_url = reverse("create Course")
            client.force_login(saved_provider_user)
            html = client.get(target_url).content.decode()
            title_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"title\"[^\>]*\>"
            )
            title_input_tag_match = title_input_tag_regex.search(html)
            assert title_input_tag_match
            title_input_tag = title_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert required_attribute_regex.search(title_input_tag)

        def test_shows_required_description_field(self, client, saved_provider_user):
            target_url = reverse("create Course")
            client.force_login(saved_provider_user)
            html = client.get(target_url).content.decode()
            description_input_tag_regex = re.compile(
                r"\<textarea[^\>]*name=\"description\"[^\>]*\>"
            )
            description_input_tag_match = description_input_tag_regex.search(html)
            assert description_input_tag_match
            description_input_tag = description_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert required_attribute_regex.search(description_input_tag)

        def test_non_required_unique_identifier_input_shows_in_page(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            identifier_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"identifier\"[^\>]*\>"
            )
            identifier_input_tag_match = identifier_input_tag_regex.search(html)
            assert identifier_input_tag_match
            identifier_input_tag = identifier_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert not required_attribute_regex.search(identifier_input_tag)

        def test_non_required_start_date_input_shows_in_page(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            start_date_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"start_date\"[^\>]*\>"
            )
            start_date_input_tag_match = start_date_input_tag_regex.search(html)
            assert start_date_input_tag_match
            start_date_input_tag = start_date_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert not required_attribute_regex.search(start_date_input_tag)

        def test_non_required_end_date_input_shows_in_page(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            end_date_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"end_date\"[^\>]*\>"
            )
            end_date_input_tag_match = end_date_input_tag_regex.search(html)
            assert end_date_input_tag_match
            end_date_input_tag = end_date_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert not required_attribute_regex.search(end_date_input_tag)


    class TestPost:
        """Tests for CreateCourseView.post"""

        def test_rejects_clinician_accounts_with_403(self, client, saved_clinician_user):
            client.force_login(saved_clinician_user)
            response = client.get(
                reverse("create Course")
            )
            assert response.status_code == 403

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_provider_user
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_user)
            html = client.post(
                target_url,
                {"title": "valid", "description": ""}
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)
            error_notes_regex = re.compile(
                r"\<ul[^\>]*class=\"[^\"]*errorlist[^\"]*\"[^\>]*>"
            )
            assert error_notes_regex.search(html)

        def test_missing_title_does_not_create_course(
            self, client, saved_provider_user
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_user)
            client.post(
                target_url,
                {
                    "description": "missing title"
                }
            )
            assert not Course.objects.filter(description="missing title").exists()

        def test_missing_description_does_not_create_course(
            self, client, saved_provider_user
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_user)
            client.post(
                target_url,
                {
                    "title": "missing description"
                }
            )
            assert not Course.objects.filter(title="missing description").exists()

        def test_valid_request_creates_course_with_right_owner(
            self, client, saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            client.post(
                reverse("create Course"),
                {
                    "title": "new course", 
                    "description": "made for checking valid requests to CreateCourseView"
                }
            )
            course = Course.objects.get(
                title="new course",
                description="made for checking valid requests to CreateCourseView"
            )
            assert course.owner == saved_provider_profile

        def test_valid_request_redirects_to_correct_url(
            self, client, saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            response = client.post(
                reverse("create Course"),
                {
                    "title": "new course", 
                    "description": "made for checking valid requests to CreateCourseView"
                }
            )
            course = Course.objects.get(
                title="new course",
                description="made for checking valid requests to CreateCourseView"
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view Course", 
                kwargs={ "course_id": course.id }
            )

        def test_set_unique_identifier_shows_on_created_course(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "title for testing unique identifier setting",
                    "description": "description for testing unique identifier setting",
                    "identifier": "it has been set"
                }
            )
            course = Course.objects.get(
                title="title for testing unique identifier setting",
                description="description for testing unique identifier setting",
            )
            assert course.identifier == "it has been set"

        def test_not_set_unique_identifier_shows_none_on_created_course(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "title for testing unique identifier setting",
                    "description": "description for testing unique identifier setting"
                }
            )
            course = Course.objects.get(
                title="title for testing unique identifier setting",
                description="description for testing unique identifier setting",
            )
            assert course.identifier is None

        def test_set_start_date_shows_on_created_course(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "title for testing start date setting",
                    "description": "description for testing start date setting",
                    "start_date": "2000-01-01"
                }
            )
            course = Course.objects.get(
                title="title for testing start date setting",
                description="description for testing start date setting",
            )
            assert course.start_date == datetime.date.fromisoformat("2000-01-01")

        def test_not_set_start_date_shows_none_on_created_course(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "title for testing start date setting",
                    "description": "description for testing start date setting"
                }
            )
            course = Course.objects.get(
                title="title for testing start date setting",
                description="description for testing start date setting",
            )
            assert course.start_date is None

        def test_set_end_date_shows_on_created_course(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "title for testing end date setting",
                    "description": "description for testing end date setting",
                    "end_date": "1999-12-31"
                }
            )
            course = Course.objects.get(
                title="title for testing end date setting",
                description="description for testing end date setting",
            )
            assert course.end_date == datetime.date.fromisoformat("1999-12-31")

        def test_not_set_end_date_shows_none_on_created_course(
            self, client, saved_provider_profile
        ):
            target_url = reverse("create Course")
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "title for testing end date setting",
                    "description": "description for testing end date setting"
                }
            )
            course = Course.objects.get(
                title="title for testing end date setting",
                description="description for testing end date setting",
            )
            assert course.end_date is None


@pytest.mark.django_db
class TestViewCourseView:
    """Tests for ViewCourseView"""

    @pytest.fixture(name="associated_commitments")
    def fixture_associated_commitments(self, saved_clinician_profile, enrolled_course):
        return (
            Commitment.objects.create(
                owner=saved_clinician_profile,
                title="First associated test commitment",
                description="This is the first commitment to commitment display for a course.",
                deadline=datetime.date.today(),
                status=CommitmentStatus.IN_PROGRESS,
                associated_course=enrolled_course
            ),
            Commitment.objects.create(
                owner=saved_clinician_profile,
                title="First associated test commitment",
                description="This is the second commitment to commitment display for a course.",
                deadline=datetime.date.today(),
                status=CommitmentStatus.IN_PROGRESS,
                associated_course=enrolled_course
            ),
            Commitment.objects.create(
                owner=saved_clinician_profile,
                title="Third associated test commitment",
                description="This is the third commitment to commitment display for a course.",
                deadline=datetime.date.today(),
                status=CommitmentStatus.IN_PROGRESS,
                associated_course=enrolled_course
            ),
        )

    @pytest.fixture(name="non_associated_commitment")
    def fixture_non_associated_commitment(self, saved_clinician_profile):
        return Commitment.objects.create(
            owner=saved_clinician_profile,
                title="Not associate",
                description="This isn't associated with a course",
                deadline=datetime.date.today(),
                status=CommitmentStatus.IN_PROGRESS,
        )


    class TestGetUnauthorizedView:
        """Tests for ViewCourseView.get that involve unauthorized viewers."""

        def test_rejects_unenrolled_clinician_accounts_with_404(
            self, client, other_clinician_profile, enrolled_course
        ):
            target_url = reverse(
                "view Course",
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "view Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404


    class TestGetOwnerView:
        """Tests for ViewCourseView.get viewing from the perspective of the owner."""

        def test_mandatory_fields_show_in_page_for_provider_1(
            self, client, saved_provider_profile, enrolled_course
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert enrolled_course.title in html
            assert enrolled_course.description in html

        def test_mandatory_fields_show_in_page_for_provider_2(
            self, client, saved_provider_profile
        ):
            new_course = Course.objects.create(
                title="New course for testing",
                description="This is for testing fields show in the page.",
                owner=saved_provider_profile,
                join_code="JOINCODE"
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": new_course.id })
            ).content.decode()
            assert new_course.title in html
            assert new_course.description in html

        def test_join_link_shows_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            join_link = reverse(
                "join Course",
                kwargs={
                    "course_id": enrolled_course.id,
                    "join_code": enrolled_course.join_code
                }
            )
            assert join_link in html

        def test_enrolled_students_list_shows_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course,
            saved_clinician_profile, other_clinician_profile
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            # For now it is always username display. When we change that, we should
            # alter this test to check that the new display method is also respected.
            assert saved_clinician_profile.username in html
            assert other_clinician_profile.username not in html

        @pytest.mark.parametrize("email_address", ["address1@test.email", "address2@localhost"])
        def test_enrolled_student_mailto_links_show_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course,
            saved_clinician_profile, email_address
        ):
            saved_clinician_profile.user.email = email_address
            saved_clinician_profile.user.save()
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert f"mailto:{email_address}" in html

        def test_general_commitment_statistics_show_in_page_for_provider_1(
            self, client, saved_provider_profile,
            enrolled_course, associated_commitments
        ):
            # Test data: 1 IN_PROGRESS, 1 COMPLETE, 1 DISCONTINUED
            associated_commitments[0].status = CommitmentStatus.IN_PROGRESS
            associated_commitments[0].save()
            associated_commitments[1].status = CommitmentStatus.COMPLETE
            associated_commitments[1].save()
            associated_commitments[2].status = CommitmentStatus.DISCONTINUED
            associated_commitments[2].save()
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert "In-progress: 1" in html
            assert "Complete: 1" in html
            assert "Past-due: 0" in html or "Past-due:" not in html
            assert "Discontinued: 1" in html
            assert "Total Commitments: 3" in html

        def test_general_commitment_statistics_show_in_page_for_provider_2(
            self, client, saved_provider_profile,
            enrolled_course, associated_commitments
        ):
            # Fill in the gaps for the statistics to prevent hardcoding/faking the table.
            # Test data: 2 EXPIRED
            associated_commitments[0].status = CommitmentStatus.EXPIRED
            associated_commitments[0].save()
            associated_commitments[1].status = CommitmentStatus.EXPIRED
            associated_commitments[1].save()
            associated_commitments[2].delete()
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            # This can change if we do something other than a table.
            assert "In-progress: 0" in html or "In-progress:" not in html
            assert "Complete: 0" in html or "Complete:" not in html
            assert "Past-due: 2" in html
            assert "Discontinued: 0" in html or "Discontinued:" not in html
            assert "Total Commitments: 2" in html

        def test_course_commitments_csv_download_shows_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            download_link = reverse(
                "download Course Commitments as csv",
                kwargs={
                    "course_id": enrolled_course.id
                }
            )
            assert download_link in html

        def test_institution_name_shows_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert saved_provider_profile.institution in html

        def test_institution_name_shows_in_page_for_clinician(
            self, client, saved_clinician_profile, enrolled_course
        ):
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert enrolled_course.owner.institution in html

        def test_suggested_commitments_show_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            enrolled_course.suggested_commitments.add(
                commitment_template_1, commitment_template_2
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert commitment_template_1.title in html
            assert commitment_template_2.title in html

        def test_select_suggested_commitments_button_shows_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            select_suggested_commitments_link_url = reverse(
                "change Course suggested commitments",
                kwargs={"course_id": enrolled_course.id}
            )
            select_suggested_commitments_link_regex = re.compile(
                r"\<a\s[^\>]*href=\"" + select_suggested_commitments_link_url + r"\"[^\>]*\>"
            )
            assert select_suggested_commitments_link_regex.search(html)

        def test_associated_commitments_show_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course,
            associated_commitments, non_associated_commitment
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            for commitment in associated_commitments:
                assert commitment.title in html
            assert non_associated_commitment.title not in html

        def test_suggested_commitments_stats_show_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course,
            commitment_template_1, make_quick_commitment
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            # We make two commitments with different status, only one of which
            # is for the template - this way we can distinguish the two stats types.
            make_quick_commitment(
                associated_course=enrolled_course,
                source_template=commitment_template_1,
                status=CommitmentStatus.COMPLETE
            )
            make_quick_commitment(
                associated_course=enrolled_course,
                status=CommitmentStatus.DISCONTINUED
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            # Mixed statuses means course stats won't show 100%, so we know this
            # is for suggested commitments if it is present.
            assert re.compile(r"100.0\s*\%").search(html)


    class TestGetStudentView:
        """Tests for ViewCourseView.get viewing from the perspective of a student."""

        def test_mandatory_fields_show_in_page_for_clinician(
            self, client, saved_clinician_profile, enrolled_course
        ):
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert enrolled_course.title in html
            assert enrolled_course.description in html

        def test_enrolled_student_mailto_links_do_not_show_in_page_for_clinician(
            self, client, enrolled_course, saved_clinician_profile
        ):
            saved_clinician_profile.user.email = "notpresent@inpage"
            saved_clinician_profile.user.save()
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert "mailto:notpresent@inpage" not in html

        def test_general_commitment_statistics_show_in_page_for_clinician(
            self, client, saved_clinician_profile,
            enrolled_course, associated_commitments
        ):
            # Test data: 1 IN_PROGRESS, 1 COMPLETE, 1 DISCONTINUED
            associated_commitments[0].status = CommitmentStatus.IN_PROGRESS
            associated_commitments[0].save()
            associated_commitments[1].status = CommitmentStatus.COMPLETE
            associated_commitments[1].save()
            associated_commitments[2].status = CommitmentStatus.DISCONTINUED
            associated_commitments[2].save()
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            # This can change if we do something other than a table.
            assert "In-progress: 1" in html
            assert "Complete: 1" in html
            assert "Past-due: 0" in html or "Past-due:" not in html
            assert "Discontinued: 1" in html
            assert "Total Commitments: 3" in html

        def test_course_commitments_csv_download_does_not_show_in_page_for_student(
            self, client, saved_clinician_profile, enrolled_course
        ):
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            download_link = reverse(
                "download Course Commitments as csv",
                kwargs={
                    "course_id": enrolled_course.id
                }
            )
            assert download_link not in html

        def test_suggested_commitments_show_in_page_for_clinician(
            self, client, saved_clinician_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            enrolled_course.suggested_commitments.add(
                commitment_template_1, commitment_template_2
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert commitment_template_1.title in html
            assert commitment_template_2.title in html

        def test_create_from_suggested_commitment_button_shows_in_page_for_clinician(
            self, client, saved_clinician_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            enrolled_course.suggested_commitments.add(
                commitment_template_1, commitment_template_2
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            create_from_link_url_1 = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            create_from_link_regex_1 = re.compile(
                r"\<a\s[^\>]*href=\"" + create_from_link_url_1 + r"\"[^\>]*\>"
            )
            assert create_from_link_regex_1.search(html)
            create_from_link_url_2 = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_2.id
                }
            )
            create_from_link_regex_2 = re.compile(
                r"\<a\s[^\>]*href=\"" + create_from_link_url_2 + r"\"[^\>]*\>"
            )
            assert create_from_link_regex_2.search(html)

        def test_associated_commitments_show_in_page_for_clinician(
            self, client, saved_clinician_profile, enrolled_course,
            associated_commitments, non_associated_commitment
        ):
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            for commitment in associated_commitments:
                assert commitment.title in html
            assert non_associated_commitment.title not in html

        def test_suggested_commitments_stats_show_in_page_for_clinician(
            self, client, saved_clinician_profile, enrolled_course,
            commitment_template_1, make_quick_commitment
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            # We make two commitments with different status, only one of which
            # is for the template - this way we can distinguish the two stats types.
            make_quick_commitment(
                associated_course=enrolled_course,
                source_template=commitment_template_1,
                status=CommitmentStatus.COMPLETE
            )
            make_quick_commitment(
                associated_course=enrolled_course,
                status=CommitmentStatus.DISCONTINUED
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view Course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            # Mixed statuses means course stats won't show 100%, so we know this
            # is for suggested commitments if it is present.
            assert re.compile(r"100.0\s*\%").search(html)

        def test_alteration_buttons_show_in_page_for_owner(
            self, client, saved_provider_profile, enrolled_course
        ):
            client.force_login(saved_provider_profile.user)
            target_url = reverse(
                "view Course",
                kwargs={"course_id": enrolled_course.id}
            )
            html = client.get(target_url).content.decode()
            delete_button_regex = re.compile(
                r"\<button[^\>]*\>[^\<]*Delete[^\<]*\<\/button\>",
                flags=re.IGNORECASE
            )
            assert delete_button_regex.search(html)
            edit_button_regex = re.compile(
                r"\<button[^\>]*\>[^\<]*Edit[^\<]*\<\/button\>",
                flags=re.IGNORECASE
            )
            assert edit_button_regex.search(html)


    class TestPost:
        """Tests for ViewCourseView.post"""

        def test_rejects_post_with_405(
            self, client, saved_provider_profile, enrolled_course
        ):
            client.force_login(saved_provider_profile.user)
            target_url = reverse(
                "view Course",
                kwargs={"course_id": enrolled_course.id}
            )
            response = client.post(
                target_url, {}
            )
            assert response.status_code == 405


@pytest.mark.django_db
class TestEditCourseView:
    """Tests for EditCourseView"""

    @pytest.fixture(name="existing_course")
    def fixture_existing_course(self, saved_provider_profile):
        return Course.objects.create(
            owner=saved_provider_profile,
            title="Existing title",
            description="Existing description",
            identifier="IDENTIFIER",
            start_date=datetime.date.fromisoformat("2000-01-01"),
            end_date=datetime.date.fromisoformat("2001-01-01")
        )


    class TestGet:
        """Tests for EditCourseView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        def test_mandatory_course_fields_are_filled_by_default(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            title_input_regex = re.compile(
                r"\<input[^\>]*name=\"title\"[^\>]*\>"
            )
            title_input_match = title_input_regex.search(html)
            assert title_input_match
            assert f"value=\"{enrolled_course.title}\"" in title_input_match[0]
            description_input_regex = re.compile(
                r"\<textarea[^\>]*name=\"description\"[^\>]*\>[^\>]*\<\/textarea\>"
            )
            description_input_match = description_input_regex.search(html)
            assert description_input_match
            assert enrolled_course.description in description_input_match[0]

        def test_non_required_unique_identifier_input_shows_in_page_with_default(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            identifier_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"identifier\"[^\>]*\>"
            )
            identifier_input_tag_match = identifier_input_tag_regex.search(html)
            assert identifier_input_tag_match
            identifier_input_tag = identifier_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert not required_attribute_regex.search(identifier_input_tag)
            assert existing_course.identifier in identifier_input_tag

        def test_non_required_start_date_input_shows_in_page(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            start_date_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"start_date\"[^\>]*\>"
            )
            start_date_input_tag_match = start_date_input_tag_regex.search(html)
            assert start_date_input_tag_match
            start_date_input_tag = start_date_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert not required_attribute_regex.search(start_date_input_tag)
            assert str(existing_course.start_date) in start_date_input_tag

        def test_non_required_end_date_input_shows_in_page(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            end_date_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"end_date\"[^\>]*\>"
            )
            end_date_input_tag_match = end_date_input_tag_regex.search(html)
            assert end_date_input_tag_match
            end_date_input_tag = end_date_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert not required_attribute_regex.search(end_date_input_tag)
            assert str(existing_course.end_date) in end_date_input_tag


    class TestPost:
        """Tests for EditCourseView.post"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_bad_request_returns_get_form(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.post(
                target_url,
                {}
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)

        def test_valid_request_alters_course(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "new description"
                }
            )
            reloaded_course = Course.objects.get(
                id=enrolled_course.id
            )
            assert reloaded_course.title == "new title"
            assert reloaded_course.description == "new description"

        def test_valid_request_redirects_correctly(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            response = client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "new description"
                }
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view Course",
                kwargs={"course_id": enrolled_course.id}
            )

        def test_valid_request_does_not_alter_enrolled_students(
            self, client, saved_provider_profile, enrolled_course
        ):
            students_before = list(enrolled_course.students.all())
            assert len(students_before) > 0
            target_url = reverse(
                "edit Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "new description"
                }
            )
            assert len(enrolled_course.students.all()) == len(students_before)
            for student in students_before:
                assert enrolled_course.students.contains(student)

        def test_set_unique_identifier_shows_on_edited_course(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "Existing title",
                    "description": "Existing description",
                    "identifier": "it has been set"
                }
            )
            course = Course.objects.get(id=existing_course.id)
            assert course.identifier == "it has been set"

        def test_not_set_unique_identifier_shows_none_on_created_course(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "Existing title",
                    "description": "Existing description",
                }
            )
            course = Course.objects.get(id=existing_course.id)
            assert course.identifier is None

        def test_set_start_date_shows_on_created_course(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "Existing title",
                    "description": "Existing description",
                    "start_date": "2000-01-01"
                }
            )
            course = Course.objects.get(id=existing_course.id)
            assert course.start_date == datetime.date.fromisoformat("2000-01-01")

        def test_not_set_start_date_shows_none_on_created_course(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "Existing title",
                    "description": "Existing description",
                }
            )
            course = Course.objects.get(id=existing_course.id)
            assert course.start_date is None

        def test_set_end_date_shows_on_created_course(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "Existing title",
                    "description": "Existing description",
                    "end_date": "1999-12-31"
                }
            )
            course = Course.objects.get(id=existing_course.id)
            assert course.end_date == datetime.date.fromisoformat("1999-12-31")

        def test_not_set_end_date_shows_none_on_created_course(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "Existing title",
                    "description": "Existing description",
                }
            )
            course = Course.objects.get(id=existing_course.id)
            assert course.end_date is None

        def test_end_before_start_date_is_rejected(
            self, client, saved_provider_profile, existing_course
        ):
            target_url = reverse(
                "edit Course",
                kwargs={"course_id": existing_course.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "Changed title",
                    "description": "Changed description",
                    "start_date": "2020-12-31",
                    "end_date": "2020-01-01"
                }
            )
            course = Course.objects.get(id=existing_course.id)
            assert course.title != "Changed title"
            assert course.description != "Changed description"
            assert course.start_date != datetime.date.fromisoformat("2020-12-31")
            assert course.end_date != datetime.date.fromisoformat("2020-01-01")


@pytest.mark.django_db
class TestCourseChangeSuggestedCommitmentsView:
    """Tests for CourseChangeSuggestedCommitmentsView"""


    class TestGet:
        """Tests for CourseChangeSuggestedCommitmentsView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        def test_shows_all_commitment_templates_in_form(
            self, client,saved_provider_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            assert commitment_template_1.title in html
            assert commitment_template_2.title in html

        def test_selects_already_suggested_commitment_templates(
            self, client,saved_provider_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            commitment_template_1_checkbox_regex = re.compile(
                r"\<input[^\>]*value=\"" 
                + str(commitment_template_1.id)
                + r"\"[^\>]*\>"
            )
            checkbox_1_match = commitment_template_1_checkbox_regex.search(html)
            assert checkbox_1_match
            assert "suggested_commitments" in checkbox_1_match[0]
            assert "checked" in checkbox_1_match[0]
            commitment_template_2_checkbox_regex = re.compile(
                r"\<input[^\>]*value=\"" 
                + str(commitment_template_2.id)
                + r"\"[^\>]*\>"
            )
            checkbox_2_match = commitment_template_2_checkbox_regex.search(html)
            assert checkbox_2_match
            assert "suggested_commitments" in checkbox_2_match[0]
            assert "checked" not in checkbox_2_match[0]

    class TestPost:
        """Tests for CourseChangeSuggestedCommitmentsView.post"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_bad_request_returns_get_form(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.post(
                target_url,
                {"suggested_commitments": "no"}
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)

        def test_valid_request_changes_suggested_commitments_to_selected(
            self, client, saved_provider_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {"suggested_commitments": [ commitment_template_2.id ]}
            )
            assert enrolled_course.suggested_commitments.filter(
                id=commitment_template_2.id
            ).exists()
            assert not enrolled_course.suggested_commitments.filter(
                id=commitment_template_1.id
            ).exists()

        def test_valid_request_with_none_selected_clears_suggested_commitments(
            self, client, saved_provider_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            enrolled_course.suggested_commitments.add(
                commitment_template_1, commitment_template_2
            )
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {"suggested_commitments": []}
            )
            assert len(enrolled_course.suggested_commitments.all()) == 0

        def test_valid_request_redirects_to_course_page(
            self, client, saved_provider_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            target_url = reverse(
                "change Course suggested commitments", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            response = client.post(
                target_url,
                {"suggested_commitments": [
                    commitment_template_1.id, commitment_template_2.id
                ]}
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view Course", kwargs={ "course_id": enrolled_course.id }
            )


@pytest.mark.django_db
class TestJoinCourseView:
    """Tests for JoinCourseView"""

    class TestGet:
        """Tests for JoinCourseView.get"""

        def test_shows_info_page_to_course_owner(
            self, client, saved_provider_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code
                }
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            assert "Join page for " + non_enrolled_course.title in html

        def test_rejects_other_provider_accounts_with_404(
            self, client, other_provider_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code
                }
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_returns_404_if_join_code_is_wrong(
            self, client, saved_clinician_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code + "wrong"
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_url(
            self, client, saved_clinician_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code
                }
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        def test_hidden_join_field_is_set(
            self, client, saved_clinician_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code
                }
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            hidden_input_regex = re.compile(
                r"\<input[^\>]*name=\"join\"[^\>]*\>"
            )
            match = hidden_input_regex.search(html)
            assert match
            input_tag = match[0]
            nonempty_value_regex = re.compile(r"value=\"[^\"]+\"")
            assert nonempty_value_regex.search(input_tag)


    class TestPost:
        """Tests for JoinCourseView.post"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code
                }
            )
            client.force_login(saved_provider_profile.user)
            response = client.post(target_url, {"join": "true"})
            assert response.status_code == 403

        def test_wrong_join_code_rejects_with_404(
            self, client, saved_clinician_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code + "wrong"
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(target_url, {"join": "true"})
            assert response.status_code == 404

        def test_missing_join_field_returns_get_page_with_error_notes(
            self, client, saved_clinician_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code
                }
            )
            client.force_login(saved_clinician_profile.user)
            html = client.post(target_url, {}).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            assert "errorlist" in html

        def test_good_request_enrolls_student_in_course(
            self, client, saved_clinician_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(target_url, {"join": "true"})
            assert non_enrolled_course.students.contains(saved_clinician_profile)

        def test_good_request_redirects_to_course_page(
            self, client, saved_clinician_profile, non_enrolled_course
        ):
            target_url = reverse(
                "join Course",
                kwargs={
                    "course_id": non_enrolled_course.id,
                    "join_code": non_enrolled_course.join_code
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(target_url, {"join": "true"})
            assert response.status_code == 302
            assert response.url == reverse(
                "view Course",
                kwargs={"course_id": non_enrolled_course.id}
            )


@pytest.mark.django_db
class TestDownloadCourseCommitmentsCSVView:
    """Tests for DownloadCourseCommitmentsCSVView"""

    class TestGet:
        """Tests for DownloadCourseCommitmentsCSVView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "download Course Commitments as csv", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "download Course Commitments as csv", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_course_with_no_commitments_gives_one_line_csv(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "download Course Commitments as csv", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            file_content = b"".join(response.streaming_content).decode()
            csv_reader = csv.reader(io.StringIO(file_content))
            rows = list(csv_reader)
            assert len(rows) == 1
            # Check at least one of the column headers to make sure they're getting written.
            # Changing the index/content here is expected if the csv format changes.
            assert rows[0][0] == "Commitment Title"

        def test_course_with_one_commitment_correctly_writes_row(
            self, client, saved_provider_profile, enrolled_course, saved_clinician_profile
        ):
            Commitment.objects.create(
                title="Sample title",
                description="Sample commitment for csv",
                owner=saved_clinician_profile,
                deadline=datetime.date.today(),
                associated_course=enrolled_course
            )
            target_url = reverse(
                "download Course Commitments as csv", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            file_content = b"".join(response.streaming_content).decode()
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)
            expected_values = {
                "Commitment Title": "Sample title", 
                "Commitment Description": "Sample commitment for csv",
                "Status": "In Progress",
                "Due": str(datetime.date.today()),
                "Owner First Name": "", # None converts to "" in csv
                "Owner Last Name": "",
                "Owner Email": "test@email.me"
            }
            # Check that expected values are a subset of actual values. This allows us to
            # add more headers without changing this test - 7 properties is enough triangulation.
            # DictReader does not have a header row so index 0.
            assert expected_values.items() <= rows[0].items()


    class TestPost:
        """Tests for DownloadCourseCommitmentsCSVView.post

        post does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_post_returns_405(self, client, saved_provider_profile):
            target_url = reverse(
                "download Course Commitments as csv",
                kwargs={"course_id": 1}
            )
            client.force_login(saved_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 405


@pytest.mark.django_db
class TestDeleteCourseView:
    """Tests for DeleteCourseView"""

    class TestGet:
        """Tests for DeleteCourseView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={"course_id": enrolled_course.id}
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={"course_id": enrolled_course.id}
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={"course_id": enrolled_course.id}
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        def test_hidden_delete_field_is_set(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            delete_input_regex = re.compile(
                r"\<input[^\>]*name=\"delete\"[^\>]*\>"
            )
            delete_input_match = delete_input_regex.search(html)
            assert delete_input_match
            assert "type=\"hidden\"" in delete_input_match[0]
            nonempty_value_regex = re.compile(
                r"value=\"[^\"]+\""
            )
            assert nonempty_value_regex.search(delete_input_match[0])


    class TestPost:
        """Tests for DeleteCourseView.post"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={"course_id": enrolled_course.id}
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={"course_id": enrolled_course.id}
            )
            client.force_login(other_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={"course_id": enrolled_course.id}
            )
            client.force_login(saved_provider_profile.user)
            html = client.post(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)
            error_notes_regex = re.compile(
                r"\<ul[^\>]*class=\"[^\"]*errorlist[^\"]*\"[^\>]*>"
            )
            assert error_notes_regex.search(html)

        def test_valid_request_deletes_course(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={"course_id": enrolled_course.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {"delete": "true"}
            )
            assert not Course.objects.filter(id=enrolled_course.id).exists()

        def test_valid_request_redirects_correctly(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "delete Course", 
                kwargs={"course_id": enrolled_course.id}
            )
            client.force_login(saved_provider_profile.user)
            response = client.post(
                target_url,
                {"delete": "true"}
            )
            assert response.status_code == 302
            assert response.url == reverse("provider dashboard")
