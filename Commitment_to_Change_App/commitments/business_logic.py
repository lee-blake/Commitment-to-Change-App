import datetime
import random
import string

from commitments.enums import CommitmentStatus


class CommitmentLogic:
    def __init__(self, data_object):
        self._data = data_object

    @property
    def status_text(self):
        # We must explicitly return this string representation based because when
        # Django loads them from the database, they are primitive integers and will
        # convert to their literal values when str() is called on them
        return CommitmentStatus.__str__(self._data.status)

    def mark_complete(self):
        self._data.status = CommitmentStatus.COMPLETE

    def mark_discontinued(self):
        self._data.status = CommitmentStatus.DISCONTINUED

    def reopen(self):
        if self._data.status in {
            CommitmentStatus.COMPLETE,
            CommitmentStatus.DISCONTINUED
            }:
            today = datetime.date.today()
            if self._data.deadline >= today:
                self._data.status = CommitmentStatus.IN_PROGRESS
            else:
                self._data.status = CommitmentStatus.EXPIRED

    def apply_commitment_template(self, commitment_template):
        self._data.title = commitment_template.title
        self._data.description = commitment_template.description
        self._data.source_template = commitment_template


class CommitmentTemplateLogic:
    def __init__(self, data_object):
        self._data = data_object

    @property
    def title(self):
        return self._data.title

    @property
    def description(self):
        return self._data.description


class CourseLogic:
    def __init__(self, data_object):
        self._data = data_object

    def __str__(self):
        return self._data.title.__str__()

    def generate_join_code_if_none_exists(self, length):
        if length <= 0:
            raise ValueError("Join codes must have a positive length!")
        if not self._data.join_code:
            self._data.join_code = ''.join(
                random.choice(string.ascii_uppercase) for i in range(0, length)
            )
