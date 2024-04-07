"""Tests for views relating to Commitment objects."""

import re

from datetime import date, timedelta

import pytest

from django.urls import reverse

from commitments.enums import CommitmentStatus
from commitments.models import Commitment, CommitmentReminderEmail
from commitments.tests.helpers import convert_date_to_general_regex


@pytest.mark.django_db
class TestCreateCommitmentView:
    """Tests for CreateCommitmentView"""

    class TestGet:
        """Tests for CreateCommitmentView.get"""

        def test_rejects_provider_accounts_with_403(self, client, saved_provider_user):
            target_url = reverse("create Commitment")
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_shows_post_form_pointing_to_this_view(self, client, saved_clinician_profile):
            target_url = reverse("create Commitment")
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

        def test_mandatory_commitment_fields_are_required(self, client, saved_clinician_profile):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            title_input_regex = re.compile(
                r"\<input[^\>]*name=\"title\"[^\>]*\>"
            )
            title_input_match = title_input_regex.search(html)
            assert title_input_match
            assert "required" in title_input_match[0]
            description_input_regex = re.compile(
                r"\<textarea[^\>]*name=\"description\"[^\>]*\>[^\>]*\<\/textarea\>"
            )
            description_input_match = description_input_regex.search(html)
            assert description_input_match
            assert "required" in description_input_match[0]
            deadline_input_regex = re.compile(
                r"\<input[^\>]*name=\"deadline\"[^\>]*\>"
            )
            deadline_input_match = deadline_input_regex.search(html)
            assert deadline_input_match
            assert "required" in deadline_input_match[0]

        def test_associated_course_shows_only_enrolled_courses_and_blank(
            self, client, saved_clinician_profile, enrolled_course, non_enrolled_course
        ):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            associated_course_select_regex = re.compile(
                r"\<select[^\>]*name=\"associated_course\"[^\>]*\>"
            )
            associated_course_select_match = associated_course_select_regex.search(html)
            assert associated_course_select_match
            associated_course_select_contents = \
                html.split(associated_course_select_match.group())[1]\
                .split("</select>")[0]
            assert "value=\"\"" in associated_course_select_contents
            assert str(enrolled_course) in associated_course_select_contents
            assert str(non_enrolled_course) not in associated_course_select_contents

        def test_reminder_preset_select_shows_in_page(
            self, client, saved_clinician_profile,
        ):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            reminder_schedule_select_regex = re.compile(
                r"\<select[^\>]*name=\"reminder_schedule\"[^\>]*\>"
            )
            assert reminder_schedule_select_regex.search(html)


    class TestPost:
        """Tests for CreateCommitmentView.post"""

        def test_rejects_provider_accounts_with_403(self, client, saved_provider_user):
            target_url = reverse("create Commitment")
            client.force_login(saved_provider_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_bad_request_returns_get_form_with_error_notes(
            self, client, saved_clinician_profile
        ):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
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

        def test_good_request_creates_commitment(self, client, saved_clinician_profile):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.today()
                }
            )
            assert Commitment.objects.filter(
                title="sample title",
                description="test description",
                deadline=date.today()
            ).exists()

        def test_good_request_redirects_to_view_page(self, client, saved_clinician_profile):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.today()
                }
            )
            commitment = Commitment.objects.get(
                title="sample title",
                description="test description",
                deadline=date.today()
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view Commitment",
                kwargs={"commitment_id": commitment.id}
            )

        def test_empty_titles_are_rejected(self, client, saved_clinician_profile):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "description": "test description",
                    "deadline": date.today()
                }
            )
            assert not Commitment.objects.filter(description="test description").exists()

        def test_empty_descriptions_are_rejected(self, client, saved_clinician_profile):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "sample title",
                    "deadline": date.today()
                }
            )
            assert not Commitment.objects.filter(title="sample title").exists()

        def test_empty_deadlines_are_rejected(self, client, saved_clinician_profile):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description"
                }
            )
            assert not Commitment.objects.filter(title="sample title").exists()

        def test_past_deadlines_are_rejected(self, client, saved_clinician_profile):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.fromisoformat("2000-01-01")
                }
            )
            assert not Commitment.objects.filter(title="sample title").exists()

        def test_enrolled_courses_are_accepted(
            self, client, saved_clinician_profile, enrolled_course
        ):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.today(),
                    "associated_course": enrolled_course.id
                }
            )
            commitment = Commitment.objects.get(
                title="sample title",
                description="test description",
                deadline=date.today()
            )
            assert commitment.associated_course == enrolled_course

        def test_non_enrolled_courses_are_rejected(
            self, client, saved_clinician_profile, non_enrolled_course
        ):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.today(),
                    "associated_course": non_enrolled_course.id
                }
            )
            assert not Commitment.objects.filter(
                title="sample title",
                description="test description",
                deadline=date.today()
            ).exists()


@pytest.mark.django_db
class TestViewCommitmentView:
    """Tests for ViewCommitmentView"""

    @pytest.fixture(name="viewable_commitment_1")
    def fixture_viewable_commitment_1(self, saved_clinician_profile):
        return Commitment.objects.create(
            title="First commitment",
            description="This is the first description",
            deadline=date.today()+timedelta(days=1),
            owner=saved_clinician_profile,
            status=CommitmentStatus.IN_PROGRESS
        )

    @pytest.fixture(name="viewable_commitment_2")
    def fixture_viewable_commitment_2(self, saved_clinician_profile):
        return Commitment.objects.create(
            title="Second commitment",
            description="This is the second description",
            deadline=date.fromisoformat("2000-01-01"),
            owner=saved_clinician_profile,
            status=CommitmentStatus.EXPIRED
        )


    class TestGet:
        """Tests for ViewCommitmentView.get"""

        def test_missing_commitment_returns_404(self, client, viewable_commitment_1):
            uid = viewable_commitment_1.id
            viewable_commitment_1.delete()
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": uid}
            )
            response = client.get(target_url)
            assert response.status_code == 404

        def test_first_commitment_values_show_in_page(
            self, client, saved_clinician_profile, viewable_commitment_1
        ):
            client.force_login(saved_clinician_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            assert viewable_commitment_1.title in html
            assert viewable_commitment_1.description in html
            deadline_regex = convert_date_to_general_regex(viewable_commitment_1.deadline)
            assert deadline_regex.search(html)

        def test_second_commitment_values_show_in_page(
            self, client, saved_clinician_profile, viewable_commitment_2
        ):
            client.force_login(saved_clinician_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_2.id}
            )
            html = client.get(target_url).content.decode()
            assert viewable_commitment_2.title in html
            assert viewable_commitment_2.description in html
            deadline_regex = convert_date_to_general_regex(viewable_commitment_2.deadline)
            assert deadline_regex.search(html)

        def test_other_clinicians_can_view_commitment(
            self, client, other_clinician_profile, viewable_commitment_1
        ):
            client.force_login(other_clinician_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            assert viewable_commitment_1.title in html
            assert viewable_commitment_1.description in html

        def test_providers_can_view_commitment(
            self, client, saved_provider_profile, viewable_commitment_1
        ):
            client.force_login(saved_provider_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            assert viewable_commitment_1.title in html
            assert viewable_commitment_1.description in html

        def test_anonymous_users_can_view_commitment(
            self, client, viewable_commitment_2
        ):
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_2.id}
            )
            html = client.get(target_url).content.decode()
            assert viewable_commitment_2.title in html
            assert viewable_commitment_2.description in html

        def test_alteration_buttons_show_in_page_for_owner(
            self, client, saved_clinician_profile, viewable_commitment_1
        ):
            client.force_login(saved_clinician_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
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

        def test_alteration_buttons_do_not_show_for_other_clinicians(
            self, client, other_clinician_profile, viewable_commitment_1
        ):
            client.force_login(other_clinician_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            delete_button_regex = re.compile(
                r"\<button[^\>]*\>[^\<]*Delete[^\<]*\<\/button\>",
                flags=re.IGNORECASE
            )
            assert not delete_button_regex.search(html)
            edit_button_regex = re.compile(
                r"\<button[^\>]*\>[^\<]*Edit[^\<]*\<\/button\>",
                flags=re.IGNORECASE
            )
            assert not edit_button_regex.search(html)

        def test_alteration_buttons_do_not_show_for_providers(
            self, client, saved_provider_profile, viewable_commitment_1
        ):
            client.force_login(saved_provider_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            delete_button_regex = re.compile(
                r"\<button[^\>]*\>[^\<]*Delete[^\<]*\<\/button\>",
                flags=re.IGNORECASE
            )
            assert not delete_button_regex.search(html)
            edit_button_regex = re.compile(
                r"\<button[^\>]*\>[^\<]*Edit[^\<]*\<\/button\>",
                flags=re.IGNORECASE
            )
            assert not edit_button_regex.search(html)

        def test_alteration_buttons_do_not_show_for_anonymous_users(
            self, client, viewable_commitment_1
        ):
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            delete_button_regex = re.compile(
                r"\<button[^\>]*\>[^\<]*Delete[^\<]*\<\/button\>",
                flags=re.IGNORECASE
            )
            assert not delete_button_regex.search(html)
            edit_button_regex = re.compile(
                r"\<button[^\>]*\>[^\<]*Edit[^\<]*\<\/button\>",
                flags=re.IGNORECASE
            )
            assert not edit_button_regex.search(html)

        def test_link_to_reminder_email_view_shows_for_owner(
            self, client, saved_clinician_profile, viewable_commitment_1
        ):
            client.force_login(saved_clinician_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            link_url = reverse(
                "view CommitmentReminderEmails",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            assert link_url in html

        def test_link_to_reminder_email_view_does_not_shows_for_providers(
            self, client, saved_provider_profile, viewable_commitment_1
        ):
            client.force_login(saved_provider_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            link_url = reverse(
                "view CommitmentReminderEmails",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            assert link_url not in html

        def test_link_to_reminder_email_view_does_not_shows_for_other_clinicians(
            self, client, other_clinician_profile, viewable_commitment_1
        ):
            client.force_login(other_clinician_profile.user)
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            link_url = reverse(
                "view CommitmentReminderEmails",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            assert link_url not in html

        def test_link_to_reminder_email_view_does_not_shows_for_anonymous_users(
            self, client, viewable_commitment_1
        ):
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            html = client.get(target_url).content.decode()
            link_url = reverse(
                "view CommitmentReminderEmails",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            assert link_url not in html


    class TestPost:
        """Tests for ViewCommitmentView.post"""

        def test_post_rejected_with_405(self, client, viewable_commitment_1):
            target_url = reverse(
                "view Commitment",
                kwargs={"commitment_id": viewable_commitment_1.id}
            )
            response = client.post(target_url)
            assert response.status_code == 405


@pytest.mark.django_db
class TestEditCommitmentView:
    """Tests for EditCommitmentView"""

    @pytest.fixture(name="existing_commitment")
    def fixture_existing_commitment(self, saved_clinician_profile):
        return Commitment.objects.create(
            owner=saved_clinician_profile,
            title="Existing title",
            description="Existing description",
            deadline=date.today(),
            status=CommitmentStatus.IN_PROGRESS
        )


    class TestGet:
        """Tests for EditCommitmentView.get"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_clinician_accounts_with_404(
            self, client, other_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(other_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_no_such_commitment_returns_404(
            self, client, saved_clinician_profile, existing_commitment
        ):
            uid = existing_commitment.id
            existing_commitment.delete()
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": uid}
            )
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
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

        def test_mandatory_commitment_fields_are_filled_and_required(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            title_input_regex = re.compile(
                r"\<input[^\>]*name=\"title\"[^\>]*\>"
            )
            title_input_match = title_input_regex.search(html)
            assert title_input_match
            assert "required" in title_input_match[0]
            assert existing_commitment.title in title_input_match[0]
            description_input_regex = re.compile(
                r"\<textarea[^\>]*name=\"description\"[^\>]*\>[^\>]*\<\/textarea\>"
            )
            description_input_match = description_input_regex.search(html)
            assert description_input_match
            assert "required" in description_input_match[0]
            assert existing_commitment.description in description_input_match[0]
            deadline_input_regex = re.compile(
                r"\<input[^\>]*name=\"deadline\"[^\>]*\>"
            )
            deadline_input_match = deadline_input_regex.search(html)
            assert deadline_input_match
            assert "required" in deadline_input_match[0]
            assert str(existing_commitment.deadline) in deadline_input_match[0]

        def test_associated_course_shows_only_enrolled_courses_and_blank(
            self, client, saved_clinician_profile, enrolled_course, non_enrolled_course,
            existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            associated_course_select_regex = re.compile(
                r"\<select[^\>]*name=\"associated_course\"[^\>]*\>"
            )
            associated_course_select_match = associated_course_select_regex.search(html)
            assert associated_course_select_match
            associated_course_select_contents = \
                html.split(associated_course_select_match.group())[1]\
                .split("</select>")[0]
            assert "value=\"\"" in associated_course_select_contents
            assert str(enrolled_course) in associated_course_select_contents
            assert str(non_enrolled_course) not in associated_course_select_contents


    class TestPost:
        """Tests for EditCommitmentView.post"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_provider_user)
            response = client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.today()
                }
            )
            assert response.status_code == 403

        def test_rejects_other_clinician_accounts_with_404(
            self, client, other_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(other_clinician_profile.user)
            response = client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.today()
                }
            )
            assert response.status_code == 404

        def test_no_such_commitment_returns_404(
            self, client, saved_clinician_profile, existing_commitment
        ):
            uid = existing_commitment.id
            existing_commitment.delete()
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": uid}
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.today()
                }
            )
            assert response.status_code == 404

        def test_bad_request_returns_get_form_with_error_notes(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
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

        def test_good_request_edits_commitment(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            new_deadline = date.today().replace(year=date.today().year+1, day=1)
            client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "new description",
                    "deadline": new_deadline
                }
            )
            reloaded_commitment = Commitment.objects.get(id=existing_commitment.id)
            assert reloaded_commitment.title == "new title"
            assert reloaded_commitment.description == "new description"
            assert reloaded_commitment.deadline == new_deadline

        def test_good_request_redirects_to_view_page(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            new_deadline = date.today().replace(year=date.today().year+1, day=1)
            response = client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "new description",
                    "deadline": new_deadline
                }
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )

        def test_empty_titles_are_rejected(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "description": "new description",
                    "deadline": date.today()
                }
            )
            reloaded_commitment = Commitment.objects.get(id=existing_commitment.id)
            assert reloaded_commitment.description != "new description"

        def test_empty_descriptions_are_rejected(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "new title",
                    "deadline": date.today()
                }
            )
            reloaded_commitment = Commitment.objects.get(id=existing_commitment.id)
            assert reloaded_commitment.title != "new title"

        def test_empty_deadlines_are_rejected(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "test description"
                }
            )
            reloaded_commitment = Commitment.objects.get(id=existing_commitment.id)
            assert reloaded_commitment.title != "new title"

        def test_past_deadlines_are_rejected(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "test description",
                    "deadline": date.fromisoformat("2000-01-01")
                }
            )
            reloaded_commitment = Commitment.objects.get(id=existing_commitment.id)
            assert reloaded_commitment.title != "new title"

        def test_enrolled_courses_are_accepted(
            self, client, saved_clinician_profile, enrolled_course, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "sample title",
                    "description": "test description",
                    "deadline": date.today(),
                    "associated_course": enrolled_course.id
                }
            )
            reloaded_commitment = Commitment.objects.get(id=existing_commitment.id)
            assert reloaded_commitment.associated_course == enrolled_course

        def test_non_enrolled_courses_are_rejected(
            self, client, saved_clinician_profile, non_enrolled_course, existing_commitment
        ):
            target_url = reverse(
                "edit Commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "test description",
                    "deadline": date.today(),
                    "associated_course": non_enrolled_course.id
                }
            )
            reloaded_commitment = Commitment.objects.get(id=existing_commitment.id)
            assert reloaded_commitment.associated_course != non_enrolled_course
            assert reloaded_commitment.title != "new title"


@pytest.mark.django_db
class TestDeleteCommitmentView:
    """Tests for DeleteCommitmentView"""

    @pytest.fixture(name="existing_commitment")
    def fixture_existing_commitment(self, saved_clinician_profile):
        return Commitment.objects.create(
            title="Deletion target",
            description="TBD",
            deadline=date.today(),
            owner=saved_clinician_profile
        )

    class TestGet:
        """Tests for DeleteCommitmentView.get"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_clinicians_with_404(
            self, client, other_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(other_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
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

        def test_hidden_delete_field_is_set(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
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
        """Tests for DeleteCommitmentView.post"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_provider_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_clinicians_with_404(
            self, client, other_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(other_clinician_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            html = client.post(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)
            error_notes_regex = re.compile(
                r"\<ul[^\>]*class=\"[^\"]*errorlist[^\"]*\"[^\>]*>"
            )
            assert error_notes_regex.search(html)

        def test_valid_request_deletes_commitment_template(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"delete": "true"}
            )
            assert not Commitment.objects.filter(id=existing_commitment.id).exists()

        def test_valid_request_redirects_correctly(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "delete Commitment", 
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {"delete": "true"}
            )
            assert response.status_code == 302
            assert response.url == reverse("clinician dashboard")


@pytest.mark.django_db
class TestCreateFromSuggestedCommitmentView:
    """Tests for CreateFromSuggestedCommitmentView"""

    class TestGet:
        """Tests for CreateFromSuggestedCommitmentView.get"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_non_student_clinician_accounts_with_404(
            self, client, other_clinician_profile, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_returns_404_on_missing_course(
            self, client, saved_clinician_user, enrolled_course, commitment_template_1
        ):
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id + 1,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_returns_404_on_missing_commitment_template(
            self, client, saved_clinician_user, enrolled_course, commitment_template_1
        ):
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id + 1
                }
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_returns_404_on_commitment_template_not_a_part_of_course(
            self, client, saved_clinician_user, enrolled_course, commitment_template_1
        ):
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_create_commitment_view(
            self, client,saved_clinician_user, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"\"[^\>]*\>"
            )
            match = form_regex.search(html)
            assert match
            form_tag = match[0]
            post_method_regex = re.compile(r"method=\"(post|POST)\"")
            assert post_method_regex.search(form_tag)

        def test_mandatory_commitment_template_fields_are_filled_by_default(
            self, client,saved_clinician_user, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            title_input_regex = re.compile(
                r"\<input[^\>]*name=\"title\"[^\>]*\>"
            )
            title_input_match = title_input_regex.search(html)
            assert title_input_match
            assert f"value=\"{commitment_template_1.title}\"" in title_input_match[0]
            description_input_regex = re.compile(
                r"\<textarea[^\>]*name=\"description\"[^\>]*\>[^\>]*\<\/textarea\>"
            )
            description_input_match = description_input_regex.search(html)
            assert description_input_match
            assert commitment_template_1.description in description_input_match[0]

        def test_course_field_is_set_by_default(
            self, client,saved_clinician_user, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            course_option_regex = re.compile(
                r"\<option[^\>]*value=\"" + str(enrolled_course.id) + r"\"[^\>]*\>"
            )
            course_option_match = course_option_regex.search(html)
            assert course_option_match
            assert "selected" in course_option_match[0]

        def test_fields_sourced_from_course_or_template_are_disabled(
            self, client,saved_clinician_user, enrolled_course, commitment_template_1
        ):
            """Tests that the fields provided automatically in this view cannot be 
            edited by the user and should visually display as such in the browser."""
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            course_select_regex = re.compile(
                r"\<select[^\>]*name=\"associated_course\"[^\>]*\>"
            )
            assert "disabled" in course_select_regex.search(html)[0]
            title_input_regex = re.compile(
                r"\<input[^\>]*name=\"title\"[^\>]*\>"
            )
            assert "disabled" in title_input_regex.search(html)[0]
            description_input_regex = re.compile(
                r"\<textarea[^\>]*name=\"description\"[^\>]*\>[^\>]*\<\/textarea\>"
            )
            assert "disabled" in description_input_regex.search(html)[0]

        def test_reminder_preset_select_shows_in_page(
            self, client, saved_clinician_profile,
        ):
            target_url = reverse("create Commitment")
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            reminder_schedule_select_regex = re.compile(
                r"\<select[^\>]*name=\"reminder_schedule\"[^\>]*\>"
            )
            assert reminder_schedule_select_regex.search(html)


    class TestPost:
        """Tests for CreateFromSuggestedCommitmentView.post"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_provider_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_non_student_clinician_accounts_with_404(
            self, client, other_clinician_profile, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_returns_404_on_missing_course(
            self, client, saved_clinician_user, enrolled_course, commitment_template_1
        ):
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id + 1,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_returns_404_on_missing_commitment_template(
            self, client, saved_clinician_user, enrolled_course, commitment_template_1
        ):
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id + 1
                }
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_returns_404_on_commitment_template_not_a_part_of_course(
            self, client, saved_clinician_user, enrolled_course, commitment_template_1
        ):
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_bad_request_returns_get_form(
            self, client,saved_clinician_profile, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            html = client.post(
                target_url,
                {}
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"\"[^\>]*\>"
            )
            assert form_regex.search(html)

        def test_valid_request_creates_commitment_with_correct_values(
            self, client, saved_clinician_profile, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {
                    "title": commitment_template_1.title,
                    "description": commitment_template_1.description,
                    "deadline": date.today(),
                    "associated_course": enrolled_course.id
                }
            )
            commitment = Commitment.objects.get(
                title=commitment_template_1.title,
                description=commitment_template_1.description,
                deadline=date.today(),
                associated_course=enrolled_course.id
            )
            assert commitment.status == CommitmentStatus.IN_PROGRESS
            assert commitment.owner == saved_clinician_profile
            assert commitment.source_template == commitment_template_1

        def test_valid_request_redirects_correctly(
            self, client, saved_clinician_profile, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "create Commitment from suggested commitment", 
                kwargs={
                    "course_id": enrolled_course.id,
                    "commitment_template_id": commitment_template_1.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {
                    "title": commitment_template_1.title,
                    "description": commitment_template_1.description,
                    "deadline": date.today(),
                    "associated_course": enrolled_course.id
                }
            )
            assert response.status_code == 302
            commitment = Commitment.objects.get(
                title=commitment_template_1.title,
                description=commitment_template_1.description,
                deadline=date.today(),
                associated_course=enrolled_course.id
            )
            assert response.url == reverse(
                "view Commitment",
                kwargs={"commitment_id": commitment.id}
            )


@pytest.mark.django_db
class TestCompleteCommitmentView:
    """Tests for CompleteCommitmentView"""

    class TestGet:
        """Tests for CompleteCommitmentView.get
        
        get does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_get_returns_405(self, client, saved_clinician_profile):
            target_url = reverse("complete Commitment", kwargs={"commitment_id": 1})
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 405


    class TestPost:
        """Tests for CompleteCommitmentView.post"""

        @pytest.fixture(name="saved_completable_commitment")
        def fixture_saved_completable_commitment(self, saved_clinician_profile):
            return Commitment.objects.create(
                owner=saved_clinician_profile,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=CommitmentStatus.IN_PROGRESS
            )

        def test_good_request_marks_complete(
            self, client, saved_completable_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "complete Commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"complete": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.COMPLETE

        def test_good_request_clears_reminder_emails(
            self, client, saved_completable_commitment, saved_clinician_profile
        ):
            CommitmentReminderEmail.objects.create(
                commitment=saved_completable_commitment,
                date=date.today() + timedelta(days=1)
            )
            CommitmentReminderEmail.objects.create(
                commitment=saved_completable_commitment,
                date=date.today() + timedelta(days=2)
            )
            target_url = reverse(
                "complete Commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"complete": "true"}
            )
            assert not CommitmentReminderEmail.objects.filter(
                commitment=saved_completable_commitment
            ).exists()

        def test_rejects_non_owner_with_no_changes(
            self, client,saved_completable_commitment, other_clinician_profile
        ):
            target_url = reverse(
                "complete Commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(other_clinician_profile.user)
            client.post(
                target_url,
                {"complete": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.IN_PROGRESS

        def test_rejects_non_owner_with_404(
            self, client, saved_completable_commitment, other_clinician_profile
        ):
            target_url = reverse(
                "complete Commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.post(
                target_url,
                {"complete": "true"}
            )
            assert response.status_code == 404

        def test_rejects_bad_request_body_with_no_changes(
            self, client, saved_completable_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "complete Commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.IN_PROGRESS

        def test_rejects_bad_request_body_with_400(
            self, client, saved_completable_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "complete Commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {}
            )
            assert response.status_code == 400


@pytest.mark.django_db
class TestDiscontinueCommitmentView:
    """Tests for DiscontinueCommitmentView"""

    class TestGet:
        """Tests for DiscontinueCommitmentView.get
        
        get does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_get_returns_405(self, client, saved_clinician_profile):
            target_url = reverse("discontinue Commitment", kwargs={"commitment_id": 1})
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 405


    class TestPost:
        """Tests for DiscontinueCommitmentView.post"""

        @pytest.fixture(name="saved_discontinueable_commitment")
        def fixture_saved_discontinueable_commitment(self, saved_clinician_profile):
            return Commitment.objects.create(
                owner=saved_clinician_profile,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=CommitmentStatus.IN_PROGRESS
            )

        def test_good_request_marks_discontinued(
            self, client, saved_discontinueable_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "discontinue Commitment", 
                kwargs={
                    "commitment_id": saved_discontinueable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"discontinue": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_discontinueable_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.DISCONTINUED

        def test_good_request_clears_reminder_emails(
            self, client, saved_discontinueable_commitment, saved_clinician_profile
        ):
            CommitmentReminderEmail.objects.create(
                commitment=saved_discontinueable_commitment,
                date=date.today() + timedelta(days=1)
            )
            CommitmentReminderEmail.objects.create(
                commitment=saved_discontinueable_commitment,
                date=date.today() + timedelta(days=2)
            )
            target_url = reverse(
                "discontinue Commitment", 
                kwargs={
                    "commitment_id": saved_discontinueable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"discontinue": "true"}
            )
            assert not CommitmentReminderEmail.objects.filter(
                commitment=saved_discontinueable_commitment
            ).exists()

        def test_rejects_non_owner_with_no_changes(
            self, client,saved_discontinueable_commitment, other_clinician_profile
        ):
            target_url = reverse(
                "discontinue Commitment", 
                kwargs={
                    "commitment_id": saved_discontinueable_commitment.id
                }
            )
            client.force_login(other_clinician_profile.user)
            client.post(
                target_url,
                {"discontinue": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_discontinueable_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.IN_PROGRESS

        def test_rejects_non_owner_with_404(
            self, client, saved_discontinueable_commitment, other_clinician_profile
        ):
            target_url = reverse(
                "discontinue Commitment", 
                kwargs={
                    "commitment_id": saved_discontinueable_commitment.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.post(
                target_url,
                {"discontinue": "true"}
            )
            assert response.status_code == 404

        def test_rejects_bad_request_body_with_no_changes(
            self, client, saved_discontinueable_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "discontinue Commitment", 
                kwargs={
                    "commitment_id": saved_discontinueable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_discontinueable_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.IN_PROGRESS

        def test_rejects_bad_request_body_with_400(
            self, client, saved_discontinueable_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "discontinue Commitment", 
                kwargs={
                    "commitment_id": saved_discontinueable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {}
            )
            assert response.status_code == 400


@pytest.mark.django_db
class TestReopenCommitmentView:
    """Tests for ReopenCommitmentView"""

    class TestGet:
        """Tests for ReopenCommitmentView.get
        
        get does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_get_returns_405(self, client, saved_clinician_profile):
            target_url = reverse("reopen Commitment", kwargs={"commitment_id": 1})
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 405


    class TestPost:
        """Tests for ReopenCommitmentView.post"""

        @pytest.fixture(name="saved_complete_commitment")
        def fixture_saved_complete_commitment(self, saved_clinician_profile):
            return Commitment.objects.create(
                owner=saved_clinician_profile,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=CommitmentStatus.COMPLETE
            )

        @pytest.fixture(name="saved_discontinued_commitment")
        def fixture_saved_discontinued_commitment(self, saved_clinician_profile):
            return Commitment.objects.create(
                owner=saved_clinician_profile,
                title="Test title",
                description="Test description",
                deadline=date.fromisoformat("2000-01-01"),
                status=CommitmentStatus.DISCONTINUED
            )

        def test_good_request_reopens_non_expired_completed_commitment(
            self, client, saved_complete_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "reopen Commitment", 
                kwargs={
                    "commitment_id": saved_complete_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"reopen": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_complete_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.IN_PROGRESS

        def test_good_request_reopens_exired_discontinued_commitment(
            self, client, saved_discontinued_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "reopen Commitment", 
                kwargs={
                    "commitment_id": saved_discontinued_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"reopen": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_discontinued_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.EXPIRED

        def test_rejects_non_owner_with_no_changes(
            self, client,saved_complete_commitment, other_clinician_profile
        ):
            target_url = reverse(
                "reopen Commitment", 
                kwargs={
                    "commitment_id": saved_complete_commitment.id
                }
            )
            client.force_login(other_clinician_profile.user)
            client.post(
                target_url,
                {"reopen": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_complete_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.COMPLETE

        def test_rejects_non_owner_with_404(
            self, client, saved_complete_commitment, other_clinician_profile
        ):
            target_url = reverse(
                "reopen Commitment", 
                kwargs={
                    "commitment_id": saved_complete_commitment.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.post(
                target_url,
                {"reopen": "true"}
            )
            assert response.status_code == 404

        def test_rejects_bad_request_body_with_no_changes(
            self, client, saved_complete_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "reopen Commitment", 
                kwargs={
                    "commitment_id": saved_complete_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_complete_commitment.id)
            assert reloaded_commitment.status == CommitmentStatus.COMPLETE

        def test_rejects_bad_request_body_with_400(
            self, client, saved_complete_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "reopen Commitment", 
                kwargs={
                    "commitment_id": saved_complete_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {}
            )
            assert response.status_code == 400
