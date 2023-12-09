from commitments.enums import CommitmentStatus


class TestCommitmentStatus:
    """Tests for CommitmentStatus"""

    class TestToStr:
        """Tests for CommitmentStatus.__str__"""

        def test_in_progress_gives_correct_string(self):
            assert str(CommitmentStatus.IN_PROGRESS) == "In Progress"

        def test_complete_gives_correct_string(self):
            assert str(CommitmentStatus.COMPLETE) == "Complete"

        def test_expired_gives_correct_string(self):
            """Test that EXPIRED converts to string correctly.
            
            While we may use 'expired' in the code, such language is forceful enough that it may
            discourage users. We should display 'past due' instead."""

            assert str(CommitmentStatus.EXPIRED) == "Past Due"

        def test_discontinued_gives_correct_string(self):
            assert str(CommitmentStatus.DISCONTINUED) == "Discontinued"
