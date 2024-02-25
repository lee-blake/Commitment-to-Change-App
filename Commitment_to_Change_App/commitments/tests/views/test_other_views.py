import csv
import io

import pytest

from django.urls import reverse

from commitments.models import Course, CommitmentTemplate


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

        def test_one_course_gives_correct_csv(
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
