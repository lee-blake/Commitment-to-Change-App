"""Tests for views relating to CommitmentTemplate objects."""

import re

import pytest

from django.urls import reverse

from commitments.models import CommitmentTemplate


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


@pytest.mark.django_db
class TestEditCommitmentTemplateView:
    """Tests for EditCommitmentTemplateView"""

    class TestGet:
        """Tests for EditCommitmentTemplateView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, commitment_template_1
        ):
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
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

        def test_mandatory_commitment_template_fields_are_filled_by_default(
            self, client, saved_provider_profile, enrolled_course, commitment_template_1
        ):
            enrolled_course.suggested_commitments.add(commitment_template_1)
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
            )
            client.force_login(saved_provider_profile.user)
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


    class TestPost:
        """Tests for EditCommitmentTemplateView.post"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, commitment_template_1
        ):
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_bad_request_returns_get_form(
            self, client, saved_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
            )
            client.force_login(saved_provider_profile.user)
            html = client.post(
                target_url,
                {"title":""}
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)

        def test_valid_request_alters_commitment_template(
            self, client, saved_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
            )
            client.force_login(saved_provider_profile.user)
            client.post(
                target_url,
                {
                    "title": "new title",
                    "description": "new description"
                }
            )
            reloaded_commitment_template = CommitmentTemplate.objects.get(
                id=commitment_template_1.id
            )
            assert reloaded_commitment_template.title == "new title"
            assert reloaded_commitment_template.description == "new description"

        def test_valid_request_redirects_correctly(
            self, client, saved_provider_profile, commitment_template_1
        ):
            target_url = reverse(
                "edit CommitmentTemplate", 
                kwargs={ "commitment_template_id": commitment_template_1.id }
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
                "view CommitmentTemplate",
                kwargs={"commitment_template_id": commitment_template_1.id}
            )
