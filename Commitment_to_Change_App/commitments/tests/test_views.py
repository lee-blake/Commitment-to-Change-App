import pytest

from datetime import date
from django.urls import reverse

from cme_accounts.models import User
from commitments.models import ClinicianProfile, Commitment

@pytest.fixture(name="saved_commitment_owner")
def fixture_saved_commitment_owner():
    user = User.objects.create(
        username="testuser", 
        password="password", 
        email="test@email.me",
        is_clinician=True
    )
    return ClinicianProfile.objects.create(
        user=user
    )

@pytest.fixture(name="other_clinician_account")
def fixture_other_clinician_account():
    user = User.objects.create(
        username="other", 
        password="password", 
        email="test@email.me",
        is_clinician=True
    )
    return ClinicianProfile.objects.create(
        user=user
    )

@pytest.mark.django_db
class TestCompleteCommitmentView:
    """Tests for CompleteCommitmentView"""

    class TestGet:
        """Tests for CompleteCommitmentView.get
        
        get does not exist. The only test here verifies that it returns an appropriate error.
        """

        def test_get_returns_405(self, client, saved_commitment_owner):
            target_url = reverse("complete commitment", kwargs={"commitment_id": 1})
            client.force_login(saved_commitment_owner.user)
            response = client.get(target_url)
            assert response.status_code == 405


    class TestPost:
        """Tests for CompletCommitmentView.post"""

        @pytest.fixture(name="saved_completable_commitment")
        def fixture_saved_completable_commitment(self, saved_commitment_owner):
            return Commitment.objects.create(
                owner=saved_commitment_owner,
                title="Test title",
                description="Test description",
                deadline=date.today(),
                status=Commitment.CommitmentStatus.IN_PROGRESS
            )

        def test_good_request_marks_complete(
            self, 
            client,
            saved_completable_commitment, 
            saved_commitment_owner
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_commitment_owner.user)
            client.post(
                target_url,
                {"complete": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.COMPLETE
        
        def test_rejects_non_owner_with_no_changes(
            self, 
            client,
            saved_completable_commitment, 
            other_clinician_account
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(other_clinician_account.user)
            client.post(
                target_url,
                {"complete": "true"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.IN_PROGRESS

        def test_rejects_non_owner_with_404(
            self, 
            client,
            saved_completable_commitment, 
            other_clinician_account
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(other_clinician_account.user)
            response = client.post(
                target_url,
                {"complete": "true"}
            )
            assert response.status_code == 404

        def test_rejects_bad_request_body_with_no_changes(
            self, 
            client,
            saved_completable_commitment, 
            saved_commitment_owner
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_commitment_owner.user)
            client.post(
                target_url,
                {"complete": "blah blah nonsense"}
            )
            reloaded_commitment = Commitment.objects.get(id=saved_completable_commitment.id)
            assert reloaded_commitment.status == Commitment.CommitmentStatus.IN_PROGRESS

        def test_rejects_bad_request_body_with_400(
            self, 
            client,
            saved_completable_commitment, 
            saved_commitment_owner
        ):
            target_url = reverse(
                "complete commitment", 
                kwargs={
                    "commitment_id": saved_completable_commitment.id
                }
            )
            client.force_login(saved_commitment_owner.user)
            response = client.post(
                target_url,
                {"complete": "blah blah nonsense"}
            )
            assert response.status_code == 400

