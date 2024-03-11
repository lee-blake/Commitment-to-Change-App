import csv
import datetime
import io

import pytest

from commitments.business_logic import CommitmentLogic, CommitmentTemplateLogic, CourseLogic, \
    ClinicianLogic, write_course_commitments_as_csv, write_aggregate_course_statistics_as_csv, \
    write_aggregate_commitment_template_statistics_as_csv
from commitments.enums import CommitmentStatus
from commitments.fake_data_objects import FakeCommitmentData, FakeCommitmentTemplateData, \
    FakeCourseData, FakeClinicianData

#pylint: disable=protected-access
# Because Django fields are generally public, we make the DTO reference field on our business
# object classes _data protected. While we could add a property on each to return the data
# object, that would be needless code for testing. We could also always create a variable
# for the data object in each test, but that would make the code less readable. It is not so
# bad for tests to use protected access if it improves readability.


class TestCommitmentLogic:
    """Tests for CommitmentLogic"""

    class TestStatusText:
        """Tests for CommitmentLogic.status_text"""

        def test_displays_in_progress_correctly(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
            )
            assert commitment.status_text == "In Progress"

        def test_displays_complete_correctly(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(status=CommitmentStatus.COMPLETE)
            )
            assert commitment.status_text == "Complete"

        def test_displays_expired_correctly(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(status=CommitmentStatus.EXPIRED)
            )
            assert commitment.status_text == "Past Due"

        def test_displays_discontinued_correctly(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(status=CommitmentStatus.DISCONTINUED)
            )
            assert commitment.status_text == "Discontinued"


    class TestMarkComplete:
        """Tests for CommitmentLogic.mark_complete"""

        def test_marks_complete(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
            )
            commitment.mark_complete()
            assert commitment._data.status == CommitmentStatus.COMPLETE


    class TestMarkDiscontinued:
        """Tests for CommitmentLogic.mark_discontinued"""

        def test_marks_discontinued(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
            )
            commitment.mark_discontinued()
            assert commitment._data.status == CommitmentStatus.DISCONTINUED


    class TestReopen:
        """Tests for CommitmentLogic.reopen"""

        def test_reopen_complete_before_deadline_sets_in_progress(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(
                    deadline=datetime.date.today(),
                    status=CommitmentStatus.COMPLETE
                )
            )
            commitment.reopen()
            assert commitment._data.status == CommitmentStatus.IN_PROGRESS

        def test_reopen_complete_after_deadline_sets_expired(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(
                    deadline=datetime.date.fromisoformat("2000-01-01"),
                    status=CommitmentStatus.COMPLETE
                )
            )
            commitment.reopen()
            assert commitment._data.status == CommitmentStatus.EXPIRED

        def test_reopen_discontinued_before_deadline_sets_in_progress(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(
                    deadline=datetime.date.today(),
                    status=CommitmentStatus.DISCONTINUED
                )
            )
            commitment.reopen()
            assert commitment._data.status == CommitmentStatus.IN_PROGRESS

        def test_reopen_in_progress_does_not_alter_status_even_if_after_deadline(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(
                    deadline=datetime.date.fromisoformat("2000-01-01"),
                    status=CommitmentStatus.IN_PROGRESS
                )
            )
            commitment.reopen()
            assert commitment._data.status == CommitmentStatus.IN_PROGRESS

        def test_reopen_expired_does_not_alter_status_even_if_before_deadline(self):
            commitment = CommitmentLogic(
                FakeCommitmentData(
                    deadline=datetime.date.today(),
                    status=CommitmentStatus.EXPIRED
                )
            )
            commitment.reopen()
            assert commitment._data.status == CommitmentStatus.EXPIRED


    class TestApplyCommitmentTemplate:
        """Tests for CommitmentLogic.apply_commitment_template"""

        @pytest.fixture(name="application_target")
        def fixture_application_target(self):
            return CommitmentLogic(
                FakeCommitmentData(
                    title="Original title",
                    description="Original description",
                    source_template=None
                )
            )

        @pytest.fixture(name="template_to_apply")
        def fixture_template_to_apply(self):
            return CommitmentTemplateLogic(
                FakeCommitmentTemplateData(
                    title="Overwritten title",
                    description="Non-overwritten title"
                )
            )

        def test_overwrites_title_field(self, application_target, template_to_apply):
            application_target.apply_commitment_template(template_to_apply)
            assert application_target._data.title == template_to_apply._data.title

        def test_overwrites_description_field(self, application_target, template_to_apply):
            application_target.apply_commitment_template(template_to_apply)
            assert application_target._data.description == template_to_apply._data.description

        def test_retains_reference_back_to_commitment_template(
            self, application_target, template_to_apply
        ):
            application_target.apply_commitment_template(template_to_apply)
            assert application_target._data.source_template == template_to_apply


class TestCommitmentTemplateLogic:
    """Tests for CommitmentTemplateLogic"""

    class TestStr:
        """Tests for CommitmentTemplateLogic.__str__"""

        @pytest.mark.parametrize("title", ["First title", "Second title"])
        def test_returns_title(self, title):
            course = CommitmentTemplateLogic(
                FakeCommitmentTemplateData(
                    title=title
                )
            )
            assert str(course) == title


    class TestTitle:
        """Tests for CommitmentTemplateLogic.title"""

        @pytest.mark.parametrize("passed_title", ["First title", "Second title"])
        def test_returns_title_from_data(self, passed_title):
            commitment_template = CommitmentTemplateLogic(
                FakeCommitmentTemplateData(title=passed_title)
            )
            assert commitment_template.title == passed_title


    class TestDescription:
        """Tests for CommitmentTemplateLogic.description"""

        @pytest.mark.parametrize("passed_description", ["First description", "Second description"])
        def test_returns_description_from_data(self, passed_description):
            commitment_template = CommitmentTemplateLogic(
                FakeCommitmentTemplateData(description=passed_description)
            )
            assert commitment_template.description == passed_description


    class TestDerivedCommitments:
        """Tests for CommitmentTemplateLogic.derived_commitments"""

        @pytest.mark.parametrize("commitment_title", ["a", "b"])
        def test_returns_derived_commitments_from_data(self, commitment_title):
            commitment_template = CommitmentTemplateLogic(
                FakeCommitmentTemplateData(
                    derived_commitments=[FakeCommitmentData(title=commitment_title)]
                )
            )
            assert commitment_template.derived_commitments[0].title == commitment_title


    class TestEnrichWithStatistics:
        """Tests for CommitmentTemplateLogic.enrich_with_statistics"""

        def test_sets_stats_correctly_on_empty_list(self):
            commitment_template = CommitmentTemplateLogic(
                FakeCommitmentTemplateData(
                    derived_commitments=[]
                )
            )
            commitment_template.enrich_with_statistics()
            assert commitment_template._data.commitment_statistics["total"] == 0

        def test_sets_stats_correctly_on_single_derived_commitment(self):
            commitment_template = CommitmentTemplateLogic(
                FakeCommitmentTemplateData(
                    derived_commitments=[FakeCommitmentData()]
                )
            )
            commitment_template.enrich_with_statistics()
            assert commitment_template._data.commitment_statistics["total"] == 1

    class TestEnrichWithCourseSpecificStatistics:
        """Tests for CommitmentTemplateLogic.enrich_with_course_specific_statistics"""

        def test_method_raises_error_when_template_is_not_a_suggested_commitment(self):
            commitment_template = CommitmentTemplateLogic(
                FakeCommitmentTemplateData()
            )
            course = FakeCourseData(
                sugggested_commitments_list=[]
            )
            with pytest.raises(ValueError):
                commitment_template.enrich_with_course_specific_statistics(course)

        def test_non_course_commitments_are_not_counted(self):
            commitment_template = CommitmentTemplateLogic(
                FakeCommitmentTemplateData(
                    derived_commitments=[
                        FakeCommitmentData(
                            associated_course=None
                        )
                    ]
                )
            )
            course = FakeCourseData(
                suggested_commitments_list=[commitment_template]
            )
            commitment_template.enrich_with_course_specific_statistics(course)
            stats = commitment_template._data.commitment_statistics_within_course
            assert stats["total"] == 0


        def test_course_commitments_are_counted(self):
            course = FakeCourseData()
            commitment_template = CommitmentTemplateLogic(
                FakeCommitmentTemplateData(
                    derived_commitments=[
                        FakeCommitmentData(
                            associated_course=course
                        )
                    ]
                )
            )
            course.suggested_commitments_list=[commitment_template]
            commitment_template.enrich_with_course_specific_statistics(course)
            stats = commitment_template._data.commitment_statistics_within_course
            assert stats["total"] == 1


class TestCourseLogic:
    """Tests for CourseLogic"""

    class TestStr:
        """Tests for CourseLogic.__str__"""

        @pytest.mark.parametrize("title", ["First title", "Second title"])
        def test_returns_title(self, title):
            course = CourseLogic(
                FakeCourseData(
                    title=title
                )
            )
            assert str(course) == title


    class TestGenerateJoinCodeIfNoneExists:
        """Tests for CourseLogic.generate_join_code_if_none_exists"""

        @pytest.mark.parametrize("nonpositive_length", [-1, 0])
        def test_nonpositive_values_throw_value_error(self, nonpositive_length):
            course = CourseLogic(FakeCourseData())
            with pytest.raises(ValueError):
                course.generate_join_code_if_none_exists(nonpositive_length)

        def test_does_not_overwrite_existing_code(self):
            course = CourseLogic(
                FakeCourseData(
                    join_code="exists!"
                )
            )
            course.generate_join_code_if_none_exists(1)
            assert course._data.join_code == "exists!"

        def test_replaces_none_code(self):
            course = CourseLogic(
                FakeCourseData(
                    join_code=None
                )
            )
            course.generate_join_code_if_none_exists(1)
            assert course._data.join_code

        @pytest.mark.parametrize("length", [5, 11])
        def test_generates_with_right_lengths(self, length):
            course = CourseLogic(
                FakeCourseData(
                    join_code=None
                )
            )
            course.generate_join_code_if_none_exists(length)
            assert len(course._data.join_code) == length


    class TestEnrollStudentWithJoinCode:
        """Tests for CourseLogic.enroll_student_with_join_code"""

        def test_invalid_code_throws_error(self):
            course = CourseLogic(
                FakeCourseData(join_code="JOINCODE")
            )
            student = ClinicianLogic(
                FakeClinicianData()
            )
            with pytest.raises(ValueError):
                course.enroll_student_with_join_code(student, "WRONG")

        def test_correct_code_enrolls_student(self):
            course = CourseLogic(
                FakeCourseData(join_code="JOINCODE")
            )
            student = ClinicianLogic(
                FakeClinicianData()
            )
            course.enroll_student_with_join_code(student, "JOINCODE")
            assert student in course._data.students

        def test_student_already_present_is_not_enrolled_twice(self):
            student = ClinicianLogic(
                FakeClinicianData()
            )
            course = CourseLogic(
                FakeCourseData(
                    join_code="JOINCODE",
                    students=[student]
                )
            )
            assert student in course._data.students
            assert len(course._data.students) == 1


    class TestEnrichWithStatistics:
        """Tests for CourseLogic.enrich_with_statistics"""

        def test_sets_stats_correctly_on_empty_list(self):
            course = CourseLogic(
                FakeCourseData(
                    associated_commitments_list=[]
                )
            )
            course.enrich_with_statistics()
            assert course._data.commitment_statistics["total"] == 0

        def test_sets_stats_correctly_on_single_associated_commitment(self):
            course = CourseLogic(
                FakeCourseData(
                    associated_commitments_list=[FakeCommitmentData()]
                )
            )
            course.enrich_with_statistics()
            assert course._data.commitment_statistics["total"] == 1


class TestWriteCourseCommitmentsAsCSV:
    """Tests for write_course_commitments_as_csv"""

    def test_empty_course_commitments_list_only_prints_headers(self):
        course = FakeCourseData(associated_commitments_list=[])
        with io.StringIO() as fake_file:
            write_course_commitments_as_csv(course, fake_file)
            fake_file.seek(0)
            csv_reader = csv.reader(fake_file)
            rows= list(csv_reader)
            assert len(rows) == 1
            expected_headers = [
                "Commitment Title", 
                "Commitment Description",
                "Status",
                "Due",
                "Owner First Name",
                "Owner Last Name",
                "Owner Email"
            ]
            assert rows[0] == expected_headers

    def test_single_course_commitment_prints_csv_correctly(self):
        owner = FakeClinicianData()
        commitment = FakeCommitmentData(owner=owner)
        course = FakeCourseData(
            associated_commitments_list=[
                commitment
            ]
        )
        with io.StringIO() as fake_file:
            write_course_commitments_as_csv(course, fake_file)
            fake_file.seek(0)
            csv_reader = csv.DictReader(fake_file)
            rows = list(csv_reader)
            expected_values = {
                "Commitment Title": commitment.title, 
                "Commitment Description": commitment.description,
                # Make sure it is definitely a string and not an int
                "Status": CommitmentStatus.__str__(commitment.status),
                "Due": str(commitment.deadline),
                "Owner First Name": owner.first_name,
                "Owner Last Name": owner.last_name,
                "Owner Email": owner.email
            }
            assert rows[0] == expected_values

    def test_enum_passed_as_int_still_prints_human_friendly_text(self):
        owner = FakeClinicianData()
        commitment = FakeCommitmentData(owner=owner)
        commitment.status = int(CommitmentStatus.COMPLETE)
        course = FakeCourseData(
            associated_commitments_list=[
                commitment
            ]
        )
        with io.StringIO() as fake_file:
            write_course_commitments_as_csv(course, fake_file)
            fake_file.seek(0)
            csv_reader = csv.DictReader(fake_file)
            rows = list(csv_reader)
            assert rows[0]["Status"] == str(CommitmentStatus.COMPLETE)


class TestWriteAggregateCourseStatisticsAsCSV:
    """Tests for write_aggregate_course_statistics_as_csv"""

    def test_empty_course_list_only_prints_headers(self):
        courses = []
        with io.StringIO() as fake_file:
            write_aggregate_course_statistics_as_csv(courses, fake_file)
            fake_file.seek(0)
            csv_reader = csv.reader(fake_file)
            rows = list(csv_reader)
            assert len(rows) == 1
            expected_headers = [
                "Course Identifier",
                "Course Title",
                "Start Date",
                "End Date",
                "Total Commitments",
                "Num. In Progress",
                "Num. Past Due",
                "Num. Completed",
                "Num. Discontinued",
                "Perc. In Progress",
                "Perc. Past Due",
                "Perc. Completed",
                "Perc. Discontinued",
            ]
            assert rows[0] == expected_headers

    def test_empty_course_prints_csv_correctly(self):
        empty_course = FakeCourseData(
            identifier=None,
            title="Empty Course",
            start_date=None,
            end_date=None,
            associated_commitments_list=[]
        )
        courses = [empty_course]
        with io.StringIO() as fake_file:
            write_aggregate_course_statistics_as_csv(courses, fake_file)
            fake_file.seek(0)
            csv_reader = csv.DictReader(fake_file)
            rows = list(csv_reader)
            expected_values = {
                "Course Identifier": "",
                "Course Title": "Empty Course",
                "Start Date": "",
                "End Date": "",
                "Total Commitments": "0",
                "Num. In Progress": "0",
                "Num. Past Due": "0",
                "Num. Completed": "0",
                "Num. Discontinued": "0",
                "Perc. In Progress": "N/A",
                "Perc. Past Due": "N/A",
                "Perc. Completed": "N/A",
                "Perc. Discontinued": "N/A",
            }
            assert rows[0] == expected_values

    def test_one_of_each_status_course_prints_csv_correctly(self):
        one_of_each_commitment_status = []
        owner = FakeClinicianData()
        for status in CommitmentStatus.values:
            commitment = FakeCommitmentData(owner=owner, status=status)
            one_of_each_commitment_status.append(commitment)
        one_of_each_status_course = FakeCourseData(
            title="One of each status",
            associated_commitments_list=one_of_each_commitment_status
        )
        courses = [one_of_each_status_course]
        with io.StringIO() as fake_file:
            write_aggregate_course_statistics_as_csv(courses, fake_file)
            fake_file.seek(0)
            csv_reader = csv.DictReader(fake_file)
            rows = list(csv_reader)
            expected_values = {
                "Course Identifier": "FAKE-001",
                "Course Title": "One of each status",
                "Start Date": str(datetime.date.today()),
                "End Date": str(datetime.date.today()),
                "Total Commitments": "4",
                "Num. In Progress": "1",
                "Num. Past Due": "1",
                "Num. Completed": "1",
                "Num. Discontinued": "1",
                "Perc. In Progress": "25.0",
                "Perc. Past Due": "25.0",
                "Perc. Completed": "25.0",
                "Perc. Discontinued": "25.0",
            }
            assert rows[0] == expected_values


class TestWriteAggregateCommitmentTemplateStatisticsAsCSV:
    """Tests for write_aggregate_commitment_template_statistics_as_csv"""

    def test_empty_commitment_template_list_only_prints_headers(self):
        commitment_templates = []
        with io.StringIO() as fake_file:
            write_aggregate_commitment_template_statistics_as_csv(
                commitment_templates, fake_file
            )
            fake_file.seek(0)
            csv_reader = csv.reader(fake_file)
            rows = list(csv_reader)
            assert len(rows) == 1
            expected_headers = [
                "Commitment Title",
                "Commitment Description",
                "Total Commitments",
                "Num. In Progress",
                "Num. Past Due",
                "Num. Completed",
                "Num. Discontinued",
                "Perc. In Progress",
                "Perc. Past Due",
                "Perc. Completed",
                "Perc. Discontinued",
            ]
            assert rows[0] == expected_headers

    def test_empty_commitment_template_prints_csv_correctly(self):
        empty_commitment_template = FakeCommitmentTemplateData(
            title="Empty Commitment Template",
            description="No derived commitments",
            derived_commitments=[]
        )
        commitment_templates = [empty_commitment_template]
        with io.StringIO() as fake_file:
            write_aggregate_commitment_template_statistics_as_csv(
                commitment_templates, fake_file
            )
            fake_file.seek(0)
            csv_reader = csv.DictReader(fake_file)
            rows = list(csv_reader)
            expected_values = {
                "Commitment Title": "Empty Commitment Template",
                "Commitment Description": "No derived commitments",
                "Total Commitments": "0",
                "Num. In Progress": "0",
                "Num. Past Due": "0",
                "Num. Completed": "0",
                "Num. Discontinued": "0",
                "Perc. In Progress": "N/A",
                "Perc. Past Due": "N/A",
                "Perc. Completed": "N/A",
                "Perc. Discontinued": "N/A",
            }
            print(rows[0])
            print(expected_values)
            assert rows[0] == expected_values

    def test_one_of_each_status_commitment_template_prints_csv_correctly(self):
        one_of_each_commitment_status = []
        owner = FakeClinicianData()
        for status in CommitmentStatus.values:
            commitment = FakeCommitmentData(owner=owner, status=status)
            one_of_each_commitment_status.append(commitment)
        one_of_each_status_commitment_template = FakeCommitmentTemplateData(
            title="One of each status",
            description="Test counts and percentages",
            derived_commitments=one_of_each_commitment_status
        )
        commitment_templates = [one_of_each_status_commitment_template]
        with io.StringIO() as fake_file:
            write_aggregate_commitment_template_statistics_as_csv(
                commitment_templates, fake_file
            )
            fake_file.seek(0)
            csv_reader = csv.DictReader(fake_file)
            rows = list(csv_reader)
            expected_values = {
                "Commitment Title": "One of each status",
                "Commitment Description": "Test counts and percentages",
                "Total Commitments": "4",
                "Num. In Progress": "1",
                "Num. Past Due": "1",
                "Num. Completed": "1",
                "Num. Discontinued": "1",
                "Perc. In Progress": "25.0",
                "Perc. Past Due": "25.0",
                "Perc. Completed": "25.0",
                "Perc. Discontinued": "25.0",
            }
            assert rows[0] == expected_values
