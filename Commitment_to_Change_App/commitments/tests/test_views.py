import re

from datetime import date

import pytest

from django.urls import reverse

from cme_accounts.models import User
from commitments.models import ClinicianProfile, ProviderProfile, Commitment, CommitmentTemplate, \
    Course

@pytest.fixture(name="saved_clinician_user")
def fixture_saved_clinician_user():
    return User.objects.create(
        username="testuser",
        password="password",
        email="test@email.me",
        is_clinician=True
    )

@pytest.fixture(name="saved_clinician_profile")
def fixture_saved_clinician_profile(saved_clinician_user):
    return ClinicianProfile.objects.create(
        user=saved_clinician_user
    )

@pytest.fixture(name="other_clinician_profile")
def fixture_other_clinician_profile():
    user = User.objects.create(
        username="other",
        password="password",
        email="test@email.me",
        is_clinician=True
    )
    return ClinicianProfile.objects.create(
        user=user
    )

@pytest.fixture(name="saved_provider_user")
def fixture_saved_provider_user():
    return User.objects.create(
        username="provider",
        password="password",
        email="test@email.me",
        is_provider=True
    )

@pytest.fixture(name="saved_provider_profile")
def fixture_saved_provider_profile(saved_provider_user):
    return ProviderProfile.objects.create(
        user=saved_provider_user
    )

@pytest.fixture(name="other_provider_profile")
def fixture_other_provider_profile():
    user = User.objects.create(
        username="other-provider",
        password="password",
        email="test@email.me",
        is_provider=True
    )
    return ProviderProfile.objects.create(
        user=user
    )

@pytest.fixture(name="enrolled_course")
def fixture_enrolled_course(saved_provider_profile, saved_clinician_profile):
    course = Course.objects.create(
        title="Enrolled Course Title",
        description="Enrolled Course Description",
        owner=saved_provider_profile,
        join_code="JOINCODE"
    )
    course.students.add(saved_clinician_profile)
    return course

@pytest.fixture(name="commitment_template_1")
def fixture_commitment_template_1(saved_provider_profile):
    return CommitmentTemplate.objects.create(
        owner=saved_provider_profile,
        title="First Suggested Title",
        description="First Suggested Description"
    )

@pytest.fixture(name="commitment_template_2")
def fixture_commitment_template_2(saved_provider_profile):
    return CommitmentTemplate.objects.create(
        owner=saved_provider_profile,
        title="Second Suggested Title",
        description="Second Suggested Description"
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


@pytest.mark.django_db
class TestCreateCommitmentTemplateView:
    """Tests for CreateCommitmentTemplateView"""

    class TestGet:
        """Tests for CreateCommitmentView.get"""

        def test_rejects_clinician_accounts_with_403(self, client, saved_clinician_user):
            client.force_login(saved_clinician_user)
            response = client.get(
                reverse("create CommitmentTemplate")
            )
            assert response.status_code == 403

        def test_shows_post_form_pointing_to_this_view(self, client, saved_provider_user):
            target_url = reverse("create CommitmentTemplate")
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
            target_url = reverse("create CommitmentTemplate")
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
            target_url = reverse("create CommitmentTemplate")
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


    class TestPost:
        """Tests for CreateCommitmentView.post"""

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_provider_user
        ):
            target_url = reverse("create CommitmentTemplate")
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

        def test_valid_request_creates_template_with_right_owner(
            self, client, saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            client.post(
                reverse("create CommitmentTemplate"),
                {
                    "title": "only used in class TestCommitmentTemplate", 
                    "description": "only used in method test_valid_request_creates_template"
                }
            )
            template = CommitmentTemplate.objects.get(
                title="only used in class TestCommitmentTemplate",
                description="only used in method test_valid_request_creates_template"
            )
            assert template.owner == saved_provider_profile

        def test_valid_request_redirects_to_correct_url(
            self, client, saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            response = client.post(
                reverse("create CommitmentTemplate"),
                {
                    "title": "only used in class TestCommitmentTemplate", 
                    "description": "only used in method test_valid_request_redirects_to_correct_url"
                }
            )
            template = CommitmentTemplate.objects.get(
                title="only used in class TestCommitmentTemplate",
                description="only used in method test_valid_request_redirects_to_correct_url"
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view CommitmentTemplate", 
                kwargs={ "commitment_template_id": template.id }
            )


@pytest.mark.django_db
class TestViewCommitmentTemplateView:
    """Tests for ViewCommitmentTemplateView"""

    @pytest.fixture(name="saved_commitment_template")
    def fixture_saved_commitment_template(self, saved_provider_profile):
        return CommitmentTemplate.objects.create(
            owner=saved_provider_profile,
            title="Should not occur randomly in HTML 123481234",
            description="Also should not occur randomly 12498123hfdwjas"
        )

    def test_rejects_clinician_accounts_with_403(
        self, client, saved_clinician_user, saved_commitment_template
    ):
        target_url = reverse(
            "view CommitmentTemplate", 
            kwargs={ "commitment_template_id": saved_commitment_template.id }
        )
        client.force_login(saved_clinician_user)
        response = client.get(target_url)
        assert response.status_code == 403

    def test_rejects_other_providers_with_404(
        self, client, other_provider_profile, saved_commitment_template
    ):
        target_url = reverse(
            "view CommitmentTemplate", 
            kwargs={ "commitment_template_id": saved_commitment_template.id }
        )
        client.force_login(other_provider_profile.user)
        response = client.get(target_url)
        assert response.status_code == 404

    def test_shows_mandatory_fields_somewhere_in_page(
        self, client, saved_provider_profile, saved_commitment_template
    ):
        target_url = reverse(
            "view CommitmentTemplate", 
            kwargs={ "commitment_template_id": saved_commitment_template.id }
        )
        client.force_login(saved_provider_profile.user)
        html = client.get(target_url).content.decode()
        assert saved_commitment_template.title in html
        assert saved_commitment_template.description in html


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
                "view course", kwargs={ "course_id": enrolled_course.id }
            )

@pytest.mark.django_db
class TestViewCourseView:
    """Tests for ViewCourseView"""

    class TestGet:
        """Tests for ViewCourseView.get"""

        # TODO Add tests to cover all Iteration 1 functionality
        # The tests I have added here only cover new code and adding those tests would
        # make this feature branch even more cumbersome than it is already. - Lee

        def test_suggested_commitments_show_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            enrolled_course.suggested_commitments.add(
                commitment_template_1, commitment_template_2
            )
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert commitment_template_1.title in html
            assert commitment_template_2.title in html

        def test_suggested_commitments_show_in_page_for_clinician(
            self, client, saved_clinician_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            enrolled_course.suggested_commitments.add(
                commitment_template_1, commitment_template_2
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            assert commitment_template_1.title in html
            assert commitment_template_2.title in html

        def test_select_suggested_commitments_button_shows_in_page_for_provider(
            self, client, saved_provider_profile, enrolled_course
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(
                reverse("view course", kwargs={ "course_id": enrolled_course.id })
            ).content.decode()
            select_suggested_commitments_link_url = reverse(
                "change Course suggested commitments",
                kwargs={"course_id": enrolled_course.id}
            )
            select_suggested_commitments_link_regex = re.compile(
                r"\<a\s[^\>]*href=\"" + select_suggested_commitments_link_url + r"\"[^\>]*\>"
            )
            assert select_suggested_commitments_link_regex.search(html)

        def test_create_from_suggested_commitment_button_shows_in_page_for_clinician(
            self, client, saved_clinician_profile, enrolled_course,
            commitment_template_1, commitment_template_2
        ):
            enrolled_course.suggested_commitments.add(
                commitment_template_1, commitment_template_2
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(
                reverse("view course", kwargs={ "course_id": enrolled_course.id })
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
class TestProviderDashboardView:
    """Tests for ProviderDashboardView"""

    class TestGet:
        """Tests for ProviderDashboardView.get"""

        # TODO Add tests to cover all Iteration 1 functionality
        # The tests I have added here only cover new code and adding those tests would
        # make this feature branch even more cumbersome than it is already. - Lee

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


@pytest.mark.django_db
class TestDeleteCommitmentTemplateView:
    """Tests for DeleteCommitmentTemplateView"""

    class TestGet:
        """Tests for DeleteCommitmentTemplateView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, commitment_template_1
        ):
            target_url = reverse(
                "delete CommitmentTemplate", 
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "delete CommitmentTemplate", 
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "delete CommitmentTemplate", 
                kwargs={"commitment_template_id": commitment_template_1.id}
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


    class TestPost:
        """Tests for DeleteCommitmentTemplateView.post"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, commitment_template_1
        ):
            target_url = reverse(
                "delete CommitmentTemplate", 
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "delete CommitmentTemplate", 
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
            client.force_login(other_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_rejects_bad_request_with_400(
            self, client, saved_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "delete CommitmentTemplate", 
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
            client.force_login(saved_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 400

        def test_valid_request_deletes_commitment_template(
            self, client, saved_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "delete CommitmentTemplate", 
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {"delete": "true"}
            )
            assert not CommitmentTemplate.objects.filter(id=commitment_template_1.id).exists()

        def test_valid_request_redirects_correctly(
            self, client, saved_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "delete CommitmentTemplate", 
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
            client.force_login(saved_provider_profile.user)
            response = client.post(
                target_url,
                {"delete": "true"}
            )
            assert response.status_code == 302
            assert response.url == reverse("provider dashboard")
        