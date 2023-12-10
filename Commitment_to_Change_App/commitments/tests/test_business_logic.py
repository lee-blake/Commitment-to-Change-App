import datetime

import pytest

from commitments.business_logic import CommitmentLogic, CommitmentTemplateLogic, CourseLogic
from commitments.enums import CommitmentStatus
from commitments.fake_data_objects import FakeCommitmentData, FakeCommitmentTemplateData, \
    FakeCourseData

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

    
    class TestStatistics:
        """Tests for CourseLogic.statistics"""

        def test_total_correct_0(self):
            course = CourseLogic(
                FakeCourseData(associated_commitments_list=[])
            )
            assert course.statistics["associated_commitments"]["total"] == 0

        def test_total_correct_1(self):
            course = CourseLogic(
                FakeCourseData(associated_commitments_list=[
                    FakeCommitmentData()
                ])
            )
            assert course.statistics["associated_commitments"]["total"] == 1

        def test_associated_commitments_status_counts_correct_all_0(self):
            course = CourseLogic(
                FakeCourseData(associated_commitments_list=[])
            )
            status_stats = course.statistics["associated_commitments"]["statuses"]
            assert status_stats["in_progress"] == 0
            assert status_stats["complete"] == 0
            assert status_stats["past_due"] == 0
            assert status_stats["discontinued"] == 0

        def test_associated_commitments_status_counts_correct_all_1(self):
            course = CourseLogic(
                FakeCourseData(
                    associated_commitments_list=[
                        FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS),
                        FakeCommitmentData(status=CommitmentStatus.COMPLETE),
                        FakeCommitmentData(status=CommitmentStatus.EXPIRED),
                        FakeCommitmentData(status=CommitmentStatus.DISCONTINUED)
                    ]
                )
            )
            status_stats = course.statistics["associated_commitments"]["statuses"]
            assert status_stats["in_progress"] == 1
            assert status_stats["complete"] == 1
            assert status_stats["past_due"] == 1
            assert status_stats["discontinued"] == 1


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
