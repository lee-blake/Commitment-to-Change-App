"""Tests for views relating to Commitment objects."""

import re

from datetime import date

import pytest

from django.urls import reverse

from commitments.models import Commitment


@pytest.mark.django_db
class TestMakeCommitmentView:
    """Tests for MakeCommitmentView"""

    class TestGet:
        """Tests for MakeCommitmentView.get"""

        def test_rejects_provider_accounts_with_403(self, client, saved_provider_user):
            target_url = reverse("make commitment")
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_shows_post_form_pointing_to_this_view(self, client, saved_clinician_profile):
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
        """Tests for MakeCommitmentView.post"""

        def test_rejects_provider_accounts_with_403(self, client, saved_provider_user):
            target_url = reverse("make commitment")
            client.force_login(saved_provider_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_bad_request_returns_get_form_with_error_notes(
            self, client, saved_clinician_profile
        ):
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
                "view commitment",
                kwargs={"commitment_id": commitment.id}
            )

        def test_empty_titles_are_rejected(self, client, saved_clinician_profile):
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
            target_url = reverse("make commitment")
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
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
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
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
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
            assert commitment.status == Commitment.CommitmentStatus.IN_PROGRESS
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
                "view commitment",
                kwargs={"commitment_id": commitment.id}
            )


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
            status=Commitment.CommitmentStatus.IN_PROGRESS
        )


    class TestGet:
        """Tests for EditCommitmentView.get"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_commitment
        ):
            target_url = reverse(
                "edit commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_clinician_accounts_with_404(
            self, client, other_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit commitment",
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
                "edit commitment",
                kwargs={"commitment_id": uid}
            )
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            new_deadline = date.today().replace(year=date.today().year+1)
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
                "edit commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_profile.user)
            new_deadline = date.today().replace(year=date.today().year+1)
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
                "view commitment",
                kwargs={"commitment_id": existing_commitment.id}
            )

        def test_empty_titles_are_rejected(
            self, client, saved_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
                "edit commitment",
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
class TestCompleteCommitmentView:
    """Tests for CompleteCommitmentView"""

    class TestGet:
        """Tests for CompleteCommitmentView.get
        
        get does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_get_returns_405(self, client, saved_clinician_profile):
            target_url = reverse("complete commitment", kwargs={"commitment_id": 1})
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 405


    class TestPost:
        """Tests for CompletCommitmentView.post"""

        @pytest.fixture(name="saved_completable_commitment")
        def fixture_saved_completable_commitment(self, saved_clinician_profile):
            return Commitment.objects.create(
                owner=saved_clinician_profile,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=Commitment.CommitmentStatus.IN_PROGRESS
            )

        def test_good_request_marks_complete(
            self, client, saved_completable_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "complete commitment", 
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
            assert reloaded_commitment.status == Commitment.CommitmentStatus.COMPLETE

        def test_rejects_non_owner_with_no_changes(
            self, client,saved_completable_commitment, other_clinician_profile
        ):
            target_url = reverse(
                "complete commitment", 
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
            assert reloaded_commitment.status == Commitment.CommitmentStatus.IN_PROGRESS

        def test_rejects_non_owner_with_404(
            self, client, saved_completable_commitment, other_clinician_profile
        ):
            target_url = reverse(
                "complete commitment", 
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
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"complete": "blah blah nonsense"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.IN_PROGRESS

        def test_rejects_bad_request_body_with_400(
            self, client, saved_completable_commitment, saved_clinician_profile
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {"complete": "blah blah nonsense"}
            )
            assert response.status_code == 400