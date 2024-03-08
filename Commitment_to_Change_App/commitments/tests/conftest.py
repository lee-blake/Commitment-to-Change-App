import datetime

import pytest

from cme_accounts.models import User
from commitments.models import ClinicianProfile, ProviderProfile, Commitment, Course, \
    CommitmentTemplate


@pytest.fixture(name="minimal_clinician")
def fixture_minimal_clinician():
    return ClinicianProfile.objects.create(
        user=User.objects.create(
            username="minimal_clinician",
            email="a@localhost",
            password="password"
        )
    )

@pytest.fixture(name="minimal_provider")
def fixture_minimal_provider():
    return ProviderProfile.objects.create(
        user=User.objects.create(
            username="minimal_provider",
            email="a@localhost",
            password="password"
        ),
        institution="Ball State University"
    )

@pytest.fixture(name="minimal_commitment")
def fixture_minimal_commitment(minimal_clinician):
    return Commitment.objects.create(
        owner=minimal_clinician,
        title="Minimal Commitment title",
        description="Minimal Commitment description",
        deadline=datetime.date.today()
    )

@pytest.fixture(name="minimal_course")
def fixture_minimal_course(minimal_provider):
    return Course.objects.create(
        owner=minimal_provider,
        title="Minimal Course title",
        description="Minimal Course description"
    )

@pytest.fixture(name="minimal_commitment_template")
def fixture_minimal_commitment_template(minimal_provider):
    return CommitmentTemplate.objects.create(
        owner=minimal_provider,
        title="Minimal CommitmentTemplate title",
        description="Minimal CommitmentTemplate description"
    )
