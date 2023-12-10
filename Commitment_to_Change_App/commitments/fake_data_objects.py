"""This file contains fake DTO representations of our Django models. It can be used for
testing both our business logic and our template logic."""

import datetime

from commitments.enums import CommitmentStatus


class FakeClinicianData:
    first_name = "Fake first name"
    last_name = "Fake last name"
    insitution = "Fake institution"

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeProviderData:
    institution = "Fake insitution"

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeCourseData:
    created = datetime.datetime.now()
    last_updated = datetime.datetime.now()
    owner = FakeProviderData()
    title = "Fake Course title"
    description = "Fake Course description"
    identifier = "FAKE-001"
    start_date = datetime.date.today()
    end_date = datetime.date.today()
    suggested_commitments = []
    join_code = ""
    students = []
    associated_commitments_list = []

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeCommitmentData:
    created = datetime.datetime.now()
    last_updated = datetime.datetime.now()
    source_template = None
    owner = FakeClinicianData()
    title = "Fake Commitment Title"
    description = "Fake Commitment description"
    status = CommitmentStatus.IN_PROGRESS
    deadline = datetime.date.today()
    associated_course = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeCommitmentTemplateData:
    title = "Fake CommitmentTemplate Title"
    description = "Fake CommitmentTemplate Description"
    owner = FakeProviderData()

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
