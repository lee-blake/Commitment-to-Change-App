"""Tests for views relating to Course objects."""

import re

import pytest

from django.urls import reverse

from commitments.models import Course


@pytest.mark.django_db
class TestCreateCourseView:
    """Tests for CreateCourseView"""

    class TestGet:
        """Tests for CreateCourseView.get"""

        def test_rejects_clinician_accounts_with_403(self, client, saved_clinician_user):
            client.force_login(saved_clinician_user)
            response = client.get(
                reverse("create course")
            )
            assert response.status_code == 403

        def test_shows_post_form_pointing_to_this_view(self, client, saved_provider_user):
            target_url = reverse("create course")
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
            target_url = reverse("create course")
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
            target_url = reverse("create course")
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
        """Tests for CreateCourseView.post"""

        def test_rejects_clinician_accounts_with_403(self, client, saved_clinician_user):
            client.force_login(saved_clinician_user)
            response = client.get(
                reverse("create course")
            )
            assert response.status_code == 403

        def test_invalid_request_returns_the_get_page_with_error_notes(
            self, client, saved_provider_user
        ):
            target_url = reverse("create course")
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
            target_url = reverse("create course")
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
            target_url = reverse("create course")
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
                reverse("create course"),
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
                reverse("create course"),
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
                "view course", 
                kwargs={ "course_id": course.id }
            )


@pytest.mark.django_db
class TestEditCourseView:
    """Tests for EditCourseView"""

    class TestGet:
        """Tests for EditCourseView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "edit course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 404

        def test_shows_post_form_pointing_to_this_view(
            self, client,saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit course", 
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
                "edit course", 
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


    class TestPost:
        """Tests for EditCourseView.post"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user, enrolled_course
        ):
            target_url = reverse(
                "edit course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(saved_clinician_user)
            response = client.post(target_url)
            assert response.status_code == 403

        def test_rejects_other_providers_with_404(
            self, client, other_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit course", 
                kwargs={ "course_id": enrolled_course.id }
            )
            client.force_login(other_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 404

        def test_bad_request_returns_get_form(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse(
                "edit course", 
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
                "edit course", 
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
                "edit course", 
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
                "view course",
                kwargs={"course_id": enrolled_course.id}
            )

        def test_valid_request_does_not_alter_enrolled_students(
            self, client, saved_provider_profile, enrolled_course
        ):
            students_before = [ student for student in enrolled_course.students.all() ]
            assert len(students_before) > 0
            target_url = reverse(
                "edit course", 
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


@pytest.mark.django_db
class TestViewCourseView:
    """Tests for ViewCourseView"""

    # TODO Add tests to cover all Iteration 1 functionality
        # The tests I have added here only cover new code and adding those tests would
        # make this feature branch even more cumbersome than it is already. - Lee

    class TestGetUnauthorizedView:
        """Tests for ViewCourseView.get that involve unauthorized viewers."""


    class TestGetOwnerView:
        """Tests for ViewCourseView.get viewing from the perspective of the owner."""

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


    class TestGetStudentView:
        """Tests for ViewCourseView.get viewing from the perspective of a student."""

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


    class TestPost:
        """Tests for ViewCourseView.post"""


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
