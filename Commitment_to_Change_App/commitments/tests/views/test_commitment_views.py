"""Tests for views relating to Commitment objects."""

import re

from datetime import date

import pytest

from django.urls import reverse

from commitments.models import Commitment


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
