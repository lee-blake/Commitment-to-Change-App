"""Tests for views relating to CommitmentReminderEmail objects."""

import datetime
import re

import pytest

from django.urls import reverse

from commitments.models import CommitmentReminderEmail
from commitments.tests.helpers import convert_date_to_general_regex

@pytest.fixture(name="existing_commitment")
def fixture_existing_commitment(make_quick_commitment):
    return make_quick_commitment()


@pytest.mark.django_db
class TestCreateCommitmentReminderEmailView:
    """Tests for CreateCommitmentReminderEmailView"""

    class TestGet:
        """Tests for CreateCommitmentReminderEmailView.get"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_commitment
        ):
            client.force_login(saved_provider_user)
            response = client.get(
                reverse(
                    "create CommitmentReminderEmail",
                    kwargs={"commitment_id": existing_commitment.id}
                )
            )
            assert response.status_code == 403

        def test_rejects_other_clinicians_with_404(
            self, client, other_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "create CommitmentReminderEmail", 
                kwargs={ "commitment_id": existing_commitment.id }
            )
            client.force_login(other_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client, saved_clinician_user, existing_commitment
        ):
            target_url = reverse(
                "create CommitmentReminderEmail",
                kwargs={"commitment_id": existing_commitment.id}
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

        def test_shows_required_date_field(
            self, client, saved_clinician_user, existing_commitment
        ):
            target_url = reverse(
                "create CommitmentReminderEmail",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            title_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"date\"[^\>]*\>"
            )
            title_input_tag_match = title_input_tag_regex.search(html)
            assert title_input_tag_match
            title_input_tag = title_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert required_attribute_regex.search(title_input_tag)


    class TestPost:
        """Tests for CreateCommitmentView.post"""

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_clinician_user, existing_commitment
        ):
            target_url = reverse(
                "create CommitmentReminderEmail",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_user)
            html = client.post(
                target_url,
                {"date": ""}
            ).content.decode()
            form_regex = re.compile(
                r"\<form[^\>]*action=\"" + target_url + r"\"[^\>]*\>"
            )
            assert form_regex.search(html)
            error_notes_regex = re.compile(
                r"\<ul[^\>]*class=\"[^\"]*errorlist[^\"]*\"[^\>]*>"
            )
            assert error_notes_regex.search(html)

        def test_valid_request_creates_reminder_email_with_right_commitment(
            self, client, saved_clinician_profile, existing_commitment
        ):
            client.force_login(saved_clinician_profile.user)
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            client.post(
                reverse(
                    "create CommitmentReminderEmail",
                    kwargs={"commitment_id": existing_commitment.id}
                ),
                {
                    "date": f"{tomorrow}"
                }
            )
            reminder_email = CommitmentReminderEmail.objects.get(
                date=tomorrow
            )
            assert reminder_email.commitment == existing_commitment

        def test_valid_request_redirects_to_correct_url(
            self, client, saved_clinician_profile, existing_commitment
        ):
            client.force_login(saved_clinician_profile.user)
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            response = client.post(
                reverse(
                    "create CommitmentReminderEmail",
                    kwargs={"commitment_id": existing_commitment.id}
                ),
                {
                    "date": f"{tomorrow}"
                }
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view CommitmentReminderEmails", 
                kwargs={ "commitment_id": existing_commitment.id }
            )


@pytest.mark.django_db
class TestViewCommitmentReminderEmailView:
    """Tests for ViewCommitmentReminderEmailView"""

    @pytest.fixture(name="saved_commitment_template")
    def fixture_saved_commitment_template(self, saved_provider_profile):
        return CommitmentReminderEmail.objects.create(
            owner=saved_provider_profile,
            title="Should not occur randomly in HTML 123481234",
            description="Also should not occur randomly 12498123hfdwjas"
        )

    def test_rejects_provider_accounts_with_403(
        self, client, saved_provider_user, existing_commitment
    ):
        target_url = reverse(
            "view CommitmentReminderEmails", 
            kwargs={ "commitment_id": existing_commitment.id }
        )
        client.force_login(saved_provider_user)
        response = client.get(target_url)
        assert response.status_code == 403

    def test_rejects_other_clinicians_with_404(
        self, client, other_clinician_profile, existing_commitment
    ):
        target_url = reverse(
            "view CommitmentReminderEmails", 
            kwargs={ "commitment_id": existing_commitment.id }
        )
        client.force_login(other_clinician_profile.user)
        response = client.get(target_url)
        assert response.status_code == 404

    def test_shows_mandatory_fields_somewhere_in_page_for_all_reminder_emails(
        self, client, saved_clinician_profile, existing_commitment
    ):
        future_date_1 = datetime.date.today() + datetime.timedelta(days=99)
        CommitmentReminderEmail.objects.create(
            commitment=existing_commitment,
            date=future_date_1
        )
        future_date_2 = datetime.date.today() + datetime.timedelta(days=199)
        CommitmentReminderEmail.objects.create(
            commitment=existing_commitment,
            date=future_date_2
        )
        target_url = reverse(
            "view CommitmentReminderEmails", 
            kwargs={ "commitment_id": existing_commitment.id }
        )
        client.force_login(saved_clinician_profile.user)
        html = client.get(target_url).content.decode()
        future_date_regex_1 = convert_date_to_general_regex(future_date_1)
        assert future_date_regex_1.search(html)
        future_date_regex_2 = convert_date_to_general_regex(future_date_2)
        assert future_date_regex_2.search(html)

    def test_links_to_create_page(
        self, client, saved_clinician_profile, existing_commitment
    ):
        target_url = reverse(
            "view CommitmentReminderEmails", 
            kwargs={ "commitment_id": existing_commitment.id }
        )
        client.force_login(saved_clinician_profile.user)
        html = client.get(target_url).content.decode()
        link_url = reverse(
            "create CommitmentReminderEmail", 
            kwargs={ "commitment_id": existing_commitment.id }
        )
        assert link_url in html
