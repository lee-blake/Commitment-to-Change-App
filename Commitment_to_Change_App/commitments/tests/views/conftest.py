"""Common fixtures for testing views"""

import datetime

import pytest

from cme_accounts.models import User
from commitments.models import ClinicianProfile, ProviderProfile, CommitmentTemplate, Course

@pytest.fixture(name="saved_clinician_user")
def fixture_saved_clinician_user():
    return User.objects.create(
        username="testuser",
        password="password",
        email="test@email.me",
        is_clinician=True
    )

@pytest.fixture(name="saved_clinician_profile")
def fixture_saved_clinician_profile(saved_clinician_user):
    return ClinicianProfile.objects.create(
        user=saved_clinician_user
    )

@pytest.fixture(name="other_clinician_profile")
def fixture_other_clinician_profile():
    user = User.objects.create(
        username="other",
        password="password",
        email="test@email.me",
        is_clinician=True
    )
    return ClinicianProfile.objects.create(
        user=user
    )

@pytest.fixture(name="saved_provider_user")
def fixture_saved_provider_user():
    return User.objects.create(
        username="provider",
        password="password",
        email="test@email.me",
        is_provider=True
    )

@pytest.fixture(name="saved_provider_profile")
def fixture_saved_provider_profile(saved_provider_user):
    return ProviderProfile.objects.create(
        user=saved_provider_user
    )

@pytest.fixture(name="other_provider_profile")
def fixture_other_provider_profile():
    user = User.objects.create(
        username="other-provider",
        password="password",
        email="test@email.me",
        is_provider=True
    )
    return ProviderProfile.objects.create(
        user=user
    )

@pytest.fixture(name="enrolled_course")
def fixture_enrolled_course(saved_provider_profile, saved_clinician_profile):
    course = Course.objects.create(
        title="Enrolled Course Title",
        description="Enrolled Course Description",
        owner=saved_provider_profile,
        join_code="JOINCODE",
        unique_identifier="ENROLLED",
        start_date=datetime.date.fromisoformat("2001-01-01"),
        end_date=datetime.date.fromisoformat("2001-12-31")
    )
    course.students.add(saved_clinician_profile)
    return course

@pytest.fixture(name="commitment_template_1")
def fixture_commitment_template_1(saved_provider_profile):
    return CommitmentTemplate.objects.create(
        owner=saved_provider_profile,
        title="First Suggested Title",
        description="First Suggested Description"
    )

@pytest.fixture(name="commitment_template_2")
def fixture_commitment_template_2(saved_provider_profile):
    return CommitmentTemplate.objects.create(
        owner=saved_provider_profile,
        title="Second Suggested Title",
        description="Second Suggested Description"
    )
