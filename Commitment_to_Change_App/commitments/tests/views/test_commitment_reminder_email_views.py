"""Tests for views relating to CommitmentReminderEmail objects."""

import datetime
import re

import pytest

from django.urls import reverse

from commitments.models import CommitmentReminderEmail, RecurringReminderEmail
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

    def test_includes_delete_url_somewhere_in_page_for_all_reminder_emails(
        self, client, saved_clinician_profile, existing_commitment
    ):
        reminder_email_1 = CommitmentReminderEmail.objects.create(
            commitment=existing_commitment,
            date=datetime.date.today() + datetime.timedelta(days=99)
        )
        reminder_email_2 = CommitmentReminderEmail.objects.create(
            commitment=existing_commitment,
            date=datetime.date.today() + datetime.timedelta(days=199)
        )
        target_url = reverse(
            "view CommitmentReminderEmails", 
            kwargs={ "commitment_id": existing_commitment.id }
        )
        client.force_login(saved_clinician_profile.user)
        html = client.get(target_url).content.decode()
        reminder_email_url_1 = reverse(
            "delete CommitmentReminderEmail", 
            kwargs={
                "commitment_id": existing_commitment.id,
                "reminder_email_id": reminder_email_1.id
            }
        )
        assert reminder_email_url_1 in html
        reminder_email_url_2 = reverse(
            "delete CommitmentReminderEmail", 
            kwargs={
                "commitment_id": existing_commitment.id,
                "reminder_email_id": reminder_email_2.id
            }
        )
        assert reminder_email_url_2 in html

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

    def test_links_to_delete_all_page(
        self, client, saved_clinician_profile, existing_commitment
    ):
        target_url = reverse(
            "view CommitmentReminderEmails", 
            kwargs={ "commitment_id": existing_commitment.id }
        )
        client.force_login(saved_clinician_profile.user)
        html = client.get(target_url).content.decode()
        link_url = reverse(
            "clear CommitmentReminderEmails", 
            kwargs={ "commitment_id": existing_commitment.id }
        )
        assert link_url in html


@pytest.mark.django_db
class TestDeleteCommitmentReminderEmailView:
    """Tests for DeleteCommitmentReminderEmailView"""

    @pytest.fixture(name="existing_reminder_email")
    def fixture_existing_reminder_email(self, make_quick_commitment):
        return CommitmentReminderEmail.objects.create(
            commitment=make_quick_commitment(),
            date=datetime.date.today()
        )

    class TestGet:
        """Tests for DeleteCommitmentReminderEmailView.get"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
            )
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_clinicians_with_404(
            self, client, other_clinician_profile, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_clinician_profile, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
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
            self, client, saved_clinician_profile, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
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
        """Tests for DeleteCommitmentReminderEmailView.post"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
            )
            client.force_login(saved_provider_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_clinicians_with_404(
            self, client, other_clinician_profile, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_clinician_profile, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
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

        def test_valid_request_deletes_reminder_email(
            self, client, saved_clinician_profile, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"delete": "true"}
            )
            assert not CommitmentReminderEmail.objects.filter(
                id=existing_reminder_email.id
            ).exists()

        def test_valid_request_redirects_correctly(
            self, client, saved_clinician_profile, existing_reminder_email
        ):
            target_url = reverse(
                "delete CommitmentReminderEmail", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id,
                    "reminder_email_id": existing_reminder_email.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {"delete": "true"}
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_email.commitment.id
                }
            )


@pytest.mark.django_db
class TestClearCommitmentReminderEmailsView:
    """Tests for ClearCommitmentReminderEmailsView"""

    @pytest.fixture(name="existing_reminder_emails")
    def fixture_existing_reminder_emails(self, make_quick_commitment):
        commitment = make_quick_commitment()
        return [
            CommitmentReminderEmail.objects.create(
                commitment=commitment,
                date=datetime.date.today() + datetime.timedelta(days=1)
            ),
            CommitmentReminderEmail.objects.create(
                commitment=commitment,
                date=datetime.date.today() + datetime.timedelta(days=2)
            ),
        ]

    class TestGet:
        """Tests for ClearCommitmentReminderEmailsView.get"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
            )
            client.force_login(saved_provider_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_clinicians_with_404(
            self, client, other_clinician_profile, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_clinician_profile, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
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

        def test_hidden_clear_field_is_set(
            self, client, saved_clinician_profile, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            html = client.get(target_url).content.decode()
            delete_input_regex = re.compile(
                r"\<input[^\>]*name=\"clear\"[^\>]*\>"
            )
            delete_input_match = delete_input_regex.search(html)
            assert delete_input_match
            assert "type=\"hidden\"" in delete_input_match[0]
            nonempty_value_regex = re.compile(
                r"value=\"[^\"]+\""
            )
            assert nonempty_value_regex.search(delete_input_match[0])

    class TestPost:
        """Tests for ClearCommitmentReminderEmailsView.post"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
            )
            client.force_login(saved_provider_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_clinicians_with_404(
            self, client, other_clinician_profile, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
            )
            client.force_login(other_clinician_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_clinician_profile, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
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

        def test_invalid_request_deletes_no_reminder_emails_for_commitment(
            self, client, saved_clinician_profile, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {}
            )
            assert CommitmentReminderEmail.objects.filter(
                commitment=existing_reminder_emails[0].commitment
            ).count() == 2

        def test_valid_request_deletes_all_reminder_emails_for_commitment(
            self, client, saved_clinician_profile, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
            )
            client.force_login(saved_clinician_profile.user)
            client.post(
                target_url,
                {"clear": "true"}
            )
            assert not CommitmentReminderEmail.objects.filter(
                commitment=existing_reminder_emails[0].commitment
            ).exists()

        def test_valid_request_redirects_correctly(
            self, client, saved_clinician_profile, existing_reminder_emails
        ):
            target_url = reverse(
                "clear CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id,
                }
            )
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                target_url,
                {"clear": "true"}
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view CommitmentReminderEmails", 
                kwargs={
                    "commitment_id": existing_reminder_emails[0].commitment.id
                }
            )


@pytest.mark.django_db
class TestCreateRecurringReminderEmailView:
    """Tests for CreateRecurringReminderEmailView"""

    class TestGet:
        """Tests for CreateRecurringReminderEmailView.get"""

        def test_rejects_provider_accounts_with_403(
            self, client, saved_provider_user, existing_commitment
        ):
            client.force_login(saved_provider_user)
            response = client.get(
                reverse(
                    "create RecurringReminderEmail",
                    kwargs={"commitment_id": existing_commitment.id}
                )
            )
            assert response.status_code == 403

        def test_rejects_other_clinicians_with_404(
            self, client, other_clinician_profile, existing_commitment
        ):
            target_url = reverse(
                "create RecurringReminderEmail",
                kwargs={ "commitment_id": existing_commitment.id }
            )
            client.force_login(other_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client, saved_clinician_user, existing_commitment
        ):
            target_url = reverse(
                "create RecurringReminderEmail",
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

        def test_shows_required_interval_field(
            self, client, saved_clinician_user, existing_commitment
        ):
            target_url = reverse(
                "create RecurringReminderEmail",
                kwargs={"commitment_id": existing_commitment.id}
            )
            client.force_login(saved_clinician_user)
            html = client.get(target_url).content.decode()
            interval_input_tag_regex = re.compile(
                r"\<input[^\>]*name=\"interval\"[^\>]*\>"
            )
            interval_input_tag_match = interval_input_tag_regex.search(html)
            assert interval_input_tag_match
            interval_input_tag = interval_input_tag_match[0]
            required_attribute_regex = re.compile(r"\srequired(=\"\")?[\s\>]")
            assert required_attribute_regex.search(interval_input_tag)


    class TestPost:
        """Tests for CreateRecurringReminderEmailView.post"""

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_clinician_user, existing_commitment
        ):
            target_url = reverse(
                "create RecurringReminderEmail",
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

        def test_valid_request_creates_recurring_reminder_email_with_right_commitment(
            self, client, saved_clinician_profile, existing_commitment
        ):
            client.force_login(saved_clinician_profile.user)
            client.post(
                reverse(
                    "create RecurringReminderEmail",
                    kwargs={"commitment_id": existing_commitment.id}
                ),
                {
                    "interval": "30"
                }
            )
            recurring_reminder_email = RecurringReminderEmail.objects.get(
                interval=30
            )
            assert recurring_reminder_email.commitment == existing_commitment

        def test_valid_request_redirects_to_correct_url(
            self, client, saved_clinician_profile, existing_commitment
        ):
            client.force_login(saved_clinician_profile.user)
            response = client.post(
                reverse(
                    "create RecurringReminderEmail",
                    kwargs={"commitment_id": existing_commitment.id}
                ),
                {
                    "interval": "30"
                }
            )
            assert response.status_code == 302
            assert response.url == reverse(
                "view CommitmentReminderEmails",
                kwargs={ "commitment_id": existing_commitment.id }
            )
