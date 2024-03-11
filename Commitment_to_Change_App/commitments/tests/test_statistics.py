import pytest

from commitments.enums import CommitmentStatus
from commitments.fake_data_objects import FakeCommitmentData
from commitments.statistics import CommitmentStatusStatistics


class TestCommitmentStatusStatistics:
    """Tests for CommitmentStatusStatistics"""

    class TestTotal:
        """Tests for CommitmentStatusStatistics.total"""

        def test_returns_zero_when_empty(self):
            stats = CommitmentStatusStatistics.from_commitment_list()
            assert stats.total() == 0

        def test_returns_one_with_single_commitment(self):
            stats = CommitmentStatusStatistics.from_commitment_list(FakeCommitmentData())
            assert stats.total() == 1


    class TestCountWithStatus:
        """Tests for CommitmentStatusStatistics.count_with_status"""

        def test_returns_zero_when_empty(self):
            stats = CommitmentStatusStatistics.from_commitment_list()
            for status in CommitmentStatus.values:
                assert stats.count_with_status(status) == 0

        @pytest.mark.parametrize("status", CommitmentStatus.values)
        def test_returns_one_with_commitment_of_that_status(self, status):
            stats = CommitmentStatusStatistics.from_commitment_list(
                FakeCommitmentData(status=status)
            )
            assert stats.count_with_status(status) == 1

        def test_returns_zero_if_none_of_that_type(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
            )
            for status in CommitmentStatus.values:
                if status == CommitmentStatus.IN_PROGRESS:
                    continue
                assert stats.count_with_status(status) == 0


    class TestFractionWithStatus:
        """Tests for CommitmentStatusStatistics.fraction_with_status"""

        def test_raises_error_when_empty(self):
            stats = CommitmentStatusStatistics.from_commitment_list()
            with pytest.raises(ArithmeticError):
                stats.fraction_with_status(CommitmentStatus.IN_PROGRESS)

        def test_returns_one_for_only_status_present(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
            )
            assert stats.fraction_with_status(CommitmentStatus.IN_PROGRESS) == 1

        def test_returns_zero_for_not_present(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
            )
            assert stats.fraction_with_status(CommitmentStatus.COMPLETE) == 0

        def test_returns_half_when_one_of_two(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS),
                FakeCommitmentData(status=CommitmentStatus.COMPLETE)
            )
            assert stats.fraction_with_status(CommitmentStatus.IN_PROGRESS) == pytest.approx(0.5)
            assert stats.fraction_with_status(CommitmentStatus.COMPLETE) == pytest.approx(0.5)


    class TestPercentageWithStatus:
        """Tests for CommitmentStatusStatistics.percentage_with_status"""

        def test_raises_error_when_empty(self):
            stats = CommitmentStatusStatistics.from_commitment_list()
            with pytest.raises(ArithmeticError):
                stats.percentage_with_status(CommitmentStatus.IN_PROGRESS)

        def test_returns_one_hundred_for_only_status_present(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
            )
            assert stats.percentage_with_status(CommitmentStatus.IN_PROGRESS) == 100

        def test_returns_zero_for_not_present(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
            )
            assert stats.percentage_with_status(CommitmentStatus.COMPLETE) == 0

        def test_returns_fifty_when_one_of_two(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS),
                FakeCommitmentData(status=CommitmentStatus.COMPLETE)
            )
            assert stats.percentage_with_status(CommitmentStatus.IN_PROGRESS) == pytest.approx(50)
            assert stats.percentage_with_status(CommitmentStatus.COMPLETE) == pytest.approx(50)


    class TestGetItem:
        """Tests for CommitmentStatusStatistics.__getitem__"""

        status_keys = ["in_progress", "complete", "discontinued", "expired"]

        def test_empty_returns_correctly(self):
            stats = CommitmentStatusStatistics.from_commitment_list()
            assert stats["total"] == 0
            for status_key in self.status_keys:
                assert stats["counts"][status_key] == 0
                assert stats["percentages"][status_key] == "N/A"

        def test_one_of_each_returns_correctly(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                *[FakeCommitmentData(status=status) for status in CommitmentStatus.values]
            )
            assert stats["total"] == 4
            for status_key in self.status_keys:
                assert stats["counts"][status_key] == 1
                assert stats["percentages"][status_key] == 25


    class TestDataAsJSON:
        """Tests for CommitmentStatusStatistics._as_dict"""

        def test_empty_returns_correctly(self):
            stats = CommitmentStatusStatistics.from_commitment_list()
            expected_json = {
                "total": 0,
                "counts": {
                    "in_progress": 0,
                    "complete": 0,
                    "discontinued": 0,
                    "expired": 0
                },
                "percentages": {
                    "in_progress": "N/A",
                    "complete": "N/A",
                    "discontinued": "N/A",
                    "expired": "N/A"
                }
            }
            assert stats._as_dict() == expected_json

        def test_one_of_each_returns_correctly(self):
            stats = CommitmentStatusStatistics.from_commitment_list(
                *[FakeCommitmentData(status=status) for status in CommitmentStatus.values]
            )
            expected_json = {
                "total": 4,
                "counts": {
                    "in_progress": 1,
                    "complete": 1,
                    "discontinued": 1,
                    "expired": 1
                },
                "percentages": {
                    "in_progress": 25,
                    "complete": 25,
                    "discontinued": 25,
                    "expired": 25
                }
            }
            assert stats._as_dict() == expected_json

    class TestAggregate:
        """Tests for CommitmentStatusStatistics.aggregate"""

        def test_aggregation_of_empties_is_empty(self):
            stats = CommitmentStatusStatistics.aggregate(
                CommitmentStatusStatistics.from_commitment_list(),
                CommitmentStatusStatistics.from_commitment_list()
            )
            assert stats["total"] == 0

        def test_aggregation_of_differing_statuses_gets_correct_values(self):
            stats = CommitmentStatusStatistics.aggregate(
                CommitmentStatusStatistics.from_commitment_list(
                    FakeCommitmentData(status=CommitmentStatus.IN_PROGRESS)
                ),
                CommitmentStatusStatistics.from_commitment_list(
                    FakeCommitmentData(status=CommitmentStatus.EXPIRED)
                ),
                CommitmentStatusStatistics.from_commitment_list(
                    FakeCommitmentData(status=CommitmentStatus.COMPLETE)
                )
            )
            assert stats["total"] == 3
            assert stats["counts"]["in_progress"] == 1
            assert stats["counts"]["expired"] == 1
            assert stats["counts"]["complete"] == 1
            assert stats["counts"]["discontinued"] == 0
