"""Tests for views relating to Course objects."""

import re

import pytest

from django.urls import reverse


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
