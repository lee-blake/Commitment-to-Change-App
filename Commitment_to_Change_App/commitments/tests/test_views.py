import re

import pytest

from datetime import date
from django.urls import reverse

from cme_accounts.models import User
from commitments.models import ClinicianProfile, ProviderProfile, Commitment, CommitmentTemplate

@pytest.fixture(name="saved_clinician_account")
def fixture_saved_clinician_account():
    return User.objects.create(
        username="testuser",
        password="password",
        email="test@email.me",
        is_clinician=True
    )

@pytest.fixture(name="saved_commitment_owner")
def fixture_saved_commitment_owner(saved_clinician_account):
    return ClinicianProfile.objects.create(
        user=saved_clinician_account
    )

@pytest.fixture(name="other_clinician_account")
def fixture_other_clinician_account():
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

@pytest.fixture(name="other_provider_user")
def fixture_other_provider_user():
    return User.objects.create(
        username="other-provider",
        password="password",
        email="test@email.me",
        is_provider=True
    )

@pytest.fixture(name="other_provider_profile")
def fixture_other_provider_profile(other_provider_user):
    return ProviderProfile.objects.create(
        user=other_provider_user
    )

@pytest.mark.django_db
class TestCompleteCommitmentView:
    """Tests for CompleteCommitmentView"""

    class TestGet:
        """Tests for CompleteCommitmentView.get
        
        get does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_get_returns_405(self, client, saved_commitment_owner):
            target_url = reverse("complete commitment", kwargs={"commitment_id": 1})
            client.force_login(saved_commitment_owner.user)
            response = client.get(target_url)
            assert response.status_code == 405


    class TestPost:
        """Tests for CompletCommitmentView.post"""

        @pytest.fixture(name="saved_completable_commitment")
        def fixture_saved_completable_commitment(self, saved_commitment_owner):
            return Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=Commitment.CommitmentStatus.IN_PROGRESS
            )

        def test_good_request_marks_complete(
            self, 
            client,
            saved_completable_commitment, 
            saved_commitment_owner
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_commitment_owner.user)
            client.post(
                target_url,
                {"complete": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.COMPLETE
        
        def test_rejects_non_owner_with_no_changes(
            self, 
            client,
            saved_completable_commitment, 
            other_clinician_account
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(other_clinician_account.user)
            client.post(
                target_url,
                {"complete": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.IN_PROGRESS

        def test_rejects_non_owner_with_404(
            self, 
            client,
            saved_completable_commitment, 
            other_clinician_account
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(other_clinician_account.user)
            response = client.post(
                target_url,
                {"complete": "true"}
            )
            assert response.status_code == 404

        def test_rejects_bad_request_body_with_no_changes(
            self, 
            client,
            saved_completable_commitment, 
            saved_commitment_owner
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_commitment_owner.user)
            client.post(
                target_url,
                {"complete": "blah blah nonsense"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.IN_PROGRESS

        def test_rejects_bad_request_body_with_400(
            self, 
            client,
            saved_completable_commitment, 
            saved_commitment_owner
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_commitment_owner.user)
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

        def test_rejects_clinician_accounts_with_403(self, client, saved_clinician_account):
            client.force_login(saved_clinician_account)
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

        def test_shows_required_title_field(
            self,
            client,
            saved_provider_user
        ):
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

        def test_shows_required_description_field(
            self,
            client,
            saved_provider_user
        ):
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
            self,
            client,
            saved_provider_user
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
            self,
            client,
            saved_provider_profile
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
            self,
            client,
            saved_provider_profile
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
        self,
        client,
        saved_clinician_account,
        saved_commitment_template
    ):
        target_url = reverse(
            "view CommitmentTemplate", 
            kwargs={ "commitment_template_id": saved_commitment_template.id }
        )
        client.force_login(saved_clinician_account)
        response = client.get(target_url)
        assert response.status_code == 403

    def test_rejects_other_providers_with_404(
        self,
        client,
        other_provider_profile,
        saved_commitment_template
    ):
        target_url = reverse(
            "view CommitmentTemplate", 
            kwargs={ "commitment_template_id": saved_commitment_template.id }
        )
        client.force_login(other_provider_profile.user)
        response = client.get(target_url)
        assert response.status_code == 404

    def test_shows_mandatory_fields_somewhere_in_page(
        self,
        client,
        saved_provider_profile,
        saved_commitment_template
    ):
        target_url = reverse(
            "view CommitmentTemplate", 
            kwargs={ "commitment_template_id": saved_commitment_template.id }
        )
        client.force_login(saved_provider_profile.user)
        html = client.get(target_url).content.decode()
        assert saved_commitment_template.title in html
        assert saved_commitment_template.description in html
