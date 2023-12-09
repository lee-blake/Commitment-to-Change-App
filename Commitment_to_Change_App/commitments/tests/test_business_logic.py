import datetime

from commitments.business_logic import CommitmentLogic
from commitments.enums import CommitmentStatus
from commitments.fake_data_objects import FakeCommitmentData

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
