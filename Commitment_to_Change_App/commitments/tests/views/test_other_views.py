import csv
import io
import re

import pytest

from django.urls import reverse

from cme_accounts.models import User
from commitments.enums import CommitmentStatus
from commitments.models import Course, CommitmentTemplate


@pytest.mark.django_db
class TestDashboardRedirectingView:
    """Tests for DashboardRedirectingView"""

    class TestGet:
        """Tests for DashboardRedirectingView.get"""

        def test_clinician_user_gets_clinician_dashboard_redirect(
            self, client, saved_clinician_profile
        ):
            target_url = reverse("dashboard")
            client.force_login(saved_clinician_profile.user)
            response = client.get(target_url)
            assert response.status_code == 302
            assert response.url == reverse("clinician dashboard")

        def test_provider_user_gets_provider_dashboard_redirect(
            self, client, saved_provider_profile
        ):
            target_url = reverse("dashboard")
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            assert response.status_code == 302
            assert response.url == reverse("provider dashboard")

        def test_non_clinician_or_provider_user_gets_server_error(
            self, client
        ):
            target_url = reverse("dashboard")
            neither_type_user = User.objects.create(
                username="neither",
                email="neither@localhost",
                password="p@ssword11"
            )
            # Tell the Django client return 500 instead of reraising the exception
            client.raise_request_exception = False
            client.force_login(neither_type_user)
            response = client.get(target_url)
            assert response.status_code == 500


    class TestPost:
        """Tests for DashboardRedirectingView.post
        
        post is not defined, tests exist to make sure it does not have unexpected functionality."""

        def test_post_returns_405(self, client, saved_provider_profile):
            target_url = reverse("dashboard")
            client.force_login(saved_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 405


@pytest.mark.django_db
class TestAggregateCourseStatisticsCSVDownloadView:
    """Tests for AggregateCourseStatisticsCSVDownloadView"""

    class TestGet:
        """Tests for AggregateCourseStatisticsCSVDownloadView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user
        ):
            target_url = reverse("download aggregate Course statistics as csv")
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_no_courses_gives_one_line_csv(
            self, client, saved_provider_profile
        ):
            target_url = reverse("download aggregate Course statistics as csv")
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            file_content = b"".join(response.streaming_content).decode()
            csv_reader = csv.reader(io.StringIO(file_content))
            rows = list(csv_reader)
            assert len(rows) == 1
            # Check at least one of the column headers to make sure they're getting written.
            # Changing the index/content here is expected if the csv format changes.
            assert rows[0][0] == "Course Identifier"

        def test_one_course_correctly_writes_row(
            self, client, saved_provider_profile
        ):
            Course.objects.create(
                owner=saved_provider_profile,
                title="One Course",
                description="Single course to test csv writing",
            )
            target_url = reverse("download aggregate Course statistics as csv")
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            file_content = b"".join(response.streaming_content).decode()
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)
            expected_values = {
                "Course Title": "One Course",
                "Total Commitments": "0",
                "Num. In Progress": "0",
                "Num. Past Due": "0",
                "Num. Completed": "0",
                "Num. Discontinued": "0",
            }
            # Check only the most essential values are saved via a subset comparison. Here, we
            # are only checking that the view integrates correctly - no need to change this test
            # if we decide more columns are added or some of less essential ones are removed.
            assert expected_values.items() <= rows[0].items()


    class TestPost:
        """Tests for AggregateCourseStatisticsCSVDownloadView.post

        post does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_post_returns_405(self, client, saved_provider_profile):
            target_url = reverse("download aggregate Course statistics as csv")
            client.force_login(saved_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 405




@pytest.mark.django_db
class TestAggregateCommitmentTemplateStatisticsCSVDownloadView:
    """Tests for AggregateCommitmentTemplateStatisticsCSVDownloadView"""

    class TestGet:
        """Tests for AggregateCommitmentTemplateStatisticsCSVDownloadView.get"""

        def test_rejects_clinician_accounts_with_403(
            self, client, saved_clinician_user
        ):
            target_url = reverse("download aggregate CommitmentTemplate statistics as csv")
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_no_commitment_templates_gives_one_line_csv(
            self, client, saved_provider_profile
        ):
            target_url = reverse("download aggregate CommitmentTemplate statistics as csv")
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            file_content = b"".join(response.streaming_content).decode()
            csv_reader = csv.reader(io.StringIO(file_content))
            rows = list(csv_reader)
            assert len(rows) == 1
            # Check at least one of the column headers to make sure they're getting written.
            # Changing the index/content here is expected if the csv format changes.
            assert rows[0][0] == "Commitment Title"

        def test_one_commitment_template_correctly_writes_row(
            self, client, saved_provider_profile
        ):
            CommitmentTemplate.objects.create(
                owner=saved_provider_profile,
                title="One CommitmentTemplate",
                description="Single comitment template to test csv writing",
            )
            target_url = reverse("download aggregate CommitmentTemplate statistics as csv")
            client.force_login(saved_provider_profile.user)
            response = client.get(target_url)
            file_content = b"".join(response.streaming_content).decode()
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)
            expected_values = {
                "Commitment Title": "One CommitmentTemplate",
                "Total Commitments": "0",
                "Num. In Progress": "0",
                "Num. Past Due": "0",
                "Num. Completed": "0",
                "Num. Discontinued": "0",
            }
            # Check only the most essential values are saved via a subset comparison. Here, we
            # are only checking that the view integrates correctly - no need to change this test
            # if we decide more columns are added or some of less essential ones are removed.
            assert expected_values.items() <= rows[0].items()


    class TestPost:
        """Tests for AggregateCommitmentTemplateStatisticsCSVDownloadView.post

        post does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_post_returns_405(self, client, saved_provider_profile):
            target_url = reverse("download aggregate CommitmentTemplate statistics as csv")
            client.force_login(saved_provider_profile.user)
            response = client.post(target_url)
            assert response.status_code == 405


@pytest.mark.django_db
class TestStatisticsOverviewView:
    """Tests for StatisticsOverviewView"""

    class TestGet:
        """Tests for StatisticsOverviewView.get"""

        def test_rejects_clinician_accounts_with_403(self, client, saved_clinician_user):
            target_url = reverse("statistics overview")
            client.force_login(saved_clinician_user)
            response = client.get(target_url)
            assert response.status_code == 403

        def test_individual_and_overall_course_stats_show_correctly(
            self, client, saved_provider_profile, enrolled_course, make_quick_commitment
        ):
            make_quick_commitment(
                associated_course=enrolled_course, status=CommitmentStatus.IN_PROGRESS
            )
            target_url = reverse("statistics overview")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            in_progress_td_matches = re.compile(
                r"\<td[^\>]*\>\s*100.0\s*\%\s*</td>"
            ).findall(html)
            non_in_progress_td_matches = re.compile(
                r"\<td[^\>]*\>\s*0.0\s*\%\s*</td>"
            ).findall(html)
            total_commitment_count_matches = re.compile(
                r"\<td[^\>]*\>\s*1\s*</td>"
            ).findall(html)
            # Because this scenario has only one course, the overall counts are the same
            # and therefore we double the expected number of matching elements.
            assert len(in_progress_td_matches) == 2
            assert len(non_in_progress_td_matches) == 6
            assert len(total_commitment_count_matches) == 2

        def test_overall_course_stats_are_correct_with_multiple_courses(
            self, client, saved_provider_profile, enrolled_course, non_enrolled_course,
            make_quick_commitment
        ):
            make_quick_commitment(
                associated_course=non_enrolled_course, status=CommitmentStatus.IN_PROGRESS
            )
            make_quick_commitment(
                associated_course=enrolled_course, status=CommitmentStatus.EXPIRED
            )
            make_quick_commitment(
                associated_course=enrolled_course, status=CommitmentStatus.COMPLETE
            )
            make_quick_commitment(
                associated_course=enrolled_course, status=CommitmentStatus.DISCONTINUED
            )
            target_url = reverse("statistics overview")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            overall_status_td_matches = re.compile(
                r"\<td[^\>]*\>\s*25.0\s*\%\s*</td>"
            ).findall(html)
            assert len(overall_status_td_matches) == 4
            total_commitment_count_matches = re.compile(
                r"\<td[^\>]*\>\s*4\s*</td>"
            ).findall(html)
            assert len(total_commitment_count_matches) == 1

        def test_individual_course_stats_are_correct_with_multiple_courses(
            self, client, saved_provider_profile, enrolled_course, non_enrolled_course,
            make_quick_commitment
        ):
            make_quick_commitment(
                associated_course=non_enrolled_course, status=CommitmentStatus.IN_PROGRESS
            )
            make_quick_commitment(
                associated_course=enrolled_course, status=CommitmentStatus.EXPIRED
            )
            make_quick_commitment(
                associated_course=enrolled_course, status=CommitmentStatus.COMPLETE
            )
            make_quick_commitment(
                associated_course=enrolled_course, status=CommitmentStatus.DISCONTINUED
            )
            target_url = reverse("statistics overview")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            enrolled_course_nonzero_td_matches = re.compile(
                r"\<td[^\>]*\>\s*33.3\s*\%\s*</td>"
            ).findall(html)
            assert len(enrolled_course_nonzero_td_matches) == 3
            non_enrolled_course_nonzero_td_matches = re.compile(
                r"\<td[^\>]*\>\s*100.0\s*\%\s*</td>"
            ).findall(html)
            assert len(non_enrolled_course_nonzero_td_matches) == 1
            zero_td_matches = re.compile(
                r"\<td[^\>]*\>\s*0.0\s*\%\s*</td>"
            ).findall(html)
            assert len(zero_td_matches) == 4
            total_for_non_enrolled_course_matches = re.compile(
                r"\<td[^\>]*\>\s*3\s*</td>"
            ).findall(html)
            assert len(total_for_non_enrolled_course_matches) == 1

        def test_course_titles_show_in_page(
            self, client, saved_provider_profile, enrolled_course
        ):
            target_url = reverse("statistics overview")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            assert enrolled_course.title in html

        def test_individual_and_overall_commitment_template_stats_show_correctly(
            self, client, saved_provider_profile, commitment_template_1,
            make_quick_commitment
        ):
            make_quick_commitment(
                source_template=commitment_template_1, status=CommitmentStatus.IN_PROGRESS
            )
            target_url = reverse("statistics overview")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            in_progress_td_matches = re.compile(
                r"\<td[^\>]*\>\s*100.0\s*\%\s*</td>"
            ).findall(html)
            non_in_progress_td_matches = re.compile(
                r"\<td[^\>]*\>\s*0.0\s*\%\s*</td>"
            ).findall(html)
            total_commitment_count_matches = re.compile(
                r"\<td[^\>]*\>\s*1\s*</td>"
            ).findall(html)
            # Because this scenario has only one course, the overall counts are the same
            # and therefore we double the expected number of matching elements.
            assert len(in_progress_td_matches) == 2
            assert len(non_in_progress_td_matches) == 6
            assert len(total_commitment_count_matches) == 2

        def test_overall_commitment_template_stats_are_correct_with_multiple_templates(
            self, client, saved_provider_profile, commitment_template_1, commitment_template_2,
            make_quick_commitment
        ):
            make_quick_commitment(
                source_template=commitment_template_2, status=CommitmentStatus.IN_PROGRESS
            )
            make_quick_commitment(
                source_template=commitment_template_1, status=CommitmentStatus.EXPIRED
            )
            make_quick_commitment(
                source_template=commitment_template_1, status=CommitmentStatus.COMPLETE
            )
            make_quick_commitment(
                source_template=commitment_template_1, status=CommitmentStatus.DISCONTINUED
            )
            target_url = reverse("statistics overview")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            overall_status_td_matches = re.compile(
                r"\<td[^\>]*\>\s*25.0\s*\%\s*</td>"
            ).findall(html)
            assert len(overall_status_td_matches) == 4
            total_commitment_count_matches = re.compile(
                r"\<td[^\>]*\>\s*4\s*</td>"
            ).findall(html)
            assert len(total_commitment_count_matches) == 1

        def test_individual_commitment_template_stats_are_correct_with_multiple_templates(
            self, client, saved_provider_profile, commitment_template_1, commitment_template_2,
            make_quick_commitment
        ):
            make_quick_commitment(
                source_template=commitment_template_2, status=CommitmentStatus.IN_PROGRESS
            )
            make_quick_commitment(
                source_template=commitment_template_1, status=CommitmentStatus.EXPIRED
            )
            make_quick_commitment(
                source_template=commitment_template_1, status=CommitmentStatus.COMPLETE
            )
            make_quick_commitment(
                source_template=commitment_template_1, status=CommitmentStatus.DISCONTINUED
            )
            target_url = reverse("statistics overview")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            enrolled_course_nonzero_td_matches = re.compile(
                r"\<td[^\>]*\>\s*33.3\s*\%\s*</td>"
            ).findall(html)
            assert len(enrolled_course_nonzero_td_matches) == 3
            non_enrolled_course_nonzero_td_matches = re.compile(
                r"\<td[^\>]*\>\s*100.0\s*\%\s*</td>"
            ).findall(html)
            assert len(non_enrolled_course_nonzero_td_matches) == 1
            zero_td_matches = re.compile(
                r"\<td[^\>]*\>\s*0.0\s*\%\s*</td>"
            ).findall(html)
            assert len(zero_td_matches) == 4
            total_for_non_enrolled_course_matches = re.compile(
                r"\<td[^\>]*\>\s*3\s*</td>"
            ).findall(html)
            assert len(total_for_non_enrolled_course_matches) == 1

        def test_commitment_template_titles_show_in_page(
            self, client, saved_provider_profile, commitment_template_1
        ):
            target_url = reverse("statistics overview")
            client.force_login(saved_provider_profile.user)
            html = client.get(target_url).content.decode()
            assert commitment_template_1.title in html

        def test_statistics_overview_links_to_aggregate_course_stats_csv_downlaod(
            self, client, saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("statistics overview")).content.decode()
            download_course_stats_csv_link = reverse("download aggregate Course statistics as csv")
            create_course_link_regex = re.compile(
                r"\<a\s[^\>]*href=\"" + download_course_stats_csv_link + r"\"[^\>]*\>"
            )
            assert create_course_link_regex.search(html)

        def test_statistics_overview_links_to_aggregate_commitment_template_stats_csv_downlaod(
            self, client, saved_provider_profile
        ):
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("statistics overview")).content.decode()
            download_course_stats_csv_link = reverse(
                "download aggregate CommitmentTemplate statistics as csv"
            )
            create_course_link_regex = re.compile(
                r"\<a\s[^\>]*href=\"" + download_course_stats_csv_link + r"\"[^\>]*\>"
            )
            assert create_course_link_regex.search(html)

        def test_does_not_show_cells_with_percentage_when_percentages_are_undefined(
            self, client, saved_provider_profile, enrolled_course, commitment_template_1
        ):  # pylint: disable=unused-argument
            # enrolled_course and commitment_template_1 are *implicitly* used to create
            # course and commitment template tables to ensure the test applies to them too.
            client.force_login(saved_provider_profile.user)
            html = client.get(reverse("statistics overview")).content.decode()
            percentage_in_cell_regex = re.compile(
                r"<td(\>|\s+[^\>]\>)\s*[\d\.]*\s*\%\s*</td>"
            )
            assert not percentage_in_cell_regex.search(html)


    class TestPost:
        """Tests for StatisticsOverviewView.post"""

        def test_post_rejected_with_405(self, client, saved_provider_profile):
            client.force_login(saved_provider_profile.user)
            response = client.post(
                reverse("statistics overview"),
                {}
            )
            assert response.status_code == 405
