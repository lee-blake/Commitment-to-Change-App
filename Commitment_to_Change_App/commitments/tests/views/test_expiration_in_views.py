"""Tests to ensure that Commitment views that show a Commitment object's status automatically
expire the respective Commitments before showing them. This functionality will become redundant
when we have a commitment expiration daemon and we should remove these tests then."""

import datetime

import pytest

from django.urls import reverse

from commitments.enums import CommitmentStatus
from commitments.models import Commitment


@pytest.fixture(name="commitment_to_expire")
def fixture_commitment_to_expire(saved_clinician_profile):
    return Commitment.objects.create(
        owner=saved_clinician_profile,
        title="Auto-expiration test",
        description="Tests that auto-expiration works on certain views",
        deadline=datetime.date.fromisoformat("2000-01-01"),
        status=CommitmentStatus.IN_PROGRESS
    )


@pytest.mark.django_db
class TestViewCommitmentViewExpiration:
    """Tests for expiration relating to ViewCommitmentView"""

    def test_view_saves_commitment_as_expired(
        self, client, saved_clinician_profile, commitment_to_expire
    ):
        client.force_login(saved_clinician_profile.user)
        client.get(
            reverse(
                "view commitment",
                kwargs={"commitment_id": commitment_to_expire.id}
            )
        )
        reloaded_commitment = Commitment.objects.get(id=commitment_to_expire.id)
        assert reloaded_commitment.status == CommitmentStatus.EXPIRED

    def test_view_shows_commitment_as_expired(
        self, client, saved_clinician_profile, commitment_to_expire
    ):
        client.force_login(saved_clinician_profile.user)
        html = client.get(
            reverse(
                "view commitment",
                kwargs={"commitment_id": commitment_to_expire.id}
            )
        ).content.decode()
        assert str(CommitmentStatus.EXPIRED) in html


@pytest.mark.django_db
class TestClinicianDashboardViewExpiration:
    """Tests for expiration relating to ClinicianDashboardView"""

    def test_view_saves_commitment_as_expired(
        self, client, saved_clinician_profile, commitment_to_expire
    ):
        client.force_login(saved_clinician_profile.user)
        client.get(reverse("clinician dashboard"))
        reloaded_commitment = Commitment.objects.get(id=commitment_to_expire.id)
        assert reloaded_commitment.status == CommitmentStatus.EXPIRED
