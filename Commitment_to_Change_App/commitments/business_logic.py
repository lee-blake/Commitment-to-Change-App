import csv
import datetime
import random
import string

from commitments.enums import CommitmentStatus


class ClinicianLogic:
    def __init__(self, data_object):
        self._data = data_object


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

    def __str__(self):
        return self._data.title

    @property
    def title(self):
        return self._data.title

    @property
    def description(self):
        return self._data.description

    @property
    def derived_commitments(self):
        return self._data.derived_commitments


class CourseLogic:
    def __init__(self, data_object):
        self._data = data_object
        self._statistics = None

    def __str__(self):
        return self._data.title.__str__()

    def generate_join_code_if_none_exists(self, length):
        if length <= 0:
            raise ValueError("Join codes must have a positive length!")
        if not self._data.join_code:
            self._data.join_code = ''.join(
                random.choice(string.ascii_uppercase) for i in range(0, length)
            )

    def enroll_student_with_join_code(self, student, code):
        if code != self._data.join_code:
            raise ValueError("The join code was incorrect!")
        self._add_student(student)

    def _add_student(self, student):
        if student not in self._data.students:
            self._data.students.append(student)


class CommitmentStatusStatistics:
    def __init__(self, *commitments):
        self._total = 0
        self._status_counts = {}
        self._initialize_status_counts()
        self._count_statuses(*commitments)

    def _initialize_status_counts(self):
        for status in CommitmentStatus.values:
            self._status_counts[status] = 0

    def _count_statuses(self, *commitments):
        for commitment in commitments:
            self._total += 1
            self._status_counts[commitment.status] += 1

    def total(self):
        return self._total

    def count_with_status(self, status):
        return self._status_counts[status]

    def fraction_with_status(self, status):
        return self._status_counts[status]/self._total

    def percentage_with_status(self, status):
        return 100*self.fraction_with_status(status)

    def as_json(self):
        return {
            "total": self._total,
            "counts": self._get_counts_json(),
            "percentages": self._get_percentages_json()
        }

    def _get_counts_json(self):
        return {
            "in_progress": self.count_with_status(CommitmentStatus.IN_PROGRESS),
            "complete": self.count_with_status(CommitmentStatus.COMPLETE),
            "discontinued": self.count_with_status(CommitmentStatus.DISCONTINUED),
            "expired": self.count_with_status(CommitmentStatus.EXPIRED),
        }

    def _get_percentages_json(self):
        if self._total == 0:
            return {
                "in_progress": "N/A",
                "complete": "N/A",
                "discontinued": "N/A",
                "expired": "N/A"
            }
        return {
            "in_progress": self.percentage_with_status(CommitmentStatus.IN_PROGRESS),
            "complete": self.percentage_with_status(CommitmentStatus.COMPLETE),
            "discontinued": self.percentage_with_status(CommitmentStatus.DISCONTINUED),
            "expired": self.percentage_with_status(CommitmentStatus.EXPIRED),
        }


def write_course_commitments_as_csv(course, file_object_to_write_to):
    headers = [
        "Commitment Title", 
        "Commitment Description",
        "Status",
        "Due",
        "Owner First Name",
        "Owner Last Name",
        "Owner Email"
    ]
    writer = csv.DictWriter(file_object_to_write_to, headers)
    writer.writeheader()
    for commitment in course.associated_commitments_list:
        writer.writerow({
            "Commitment Title": commitment.title,
            "Commitment Description": commitment.description,
            # Because it is an enum, CommitmentStatus may be erroneously loaded as an int.
            # Ensure it always converts to a human-friendly string.
            "Status": CommitmentStatus.__str__(commitment.status),
            "Due": commitment.deadline,
            "Owner First Name": commitment.owner.first_name,
            "Owner Last Name": commitment.owner.last_name,
            "Owner Email": commitment.owner.email
        })


def write_aggregate_course_statistics_as_csv(courses, file_object_to_write_to):
    headers = [
        "Course Identifier",
        "Course Title",
        "Start Date",
        "End Date",
        "Total Commitments",
        "Num. In Progress",
        "Num. Past Due",
        "Num. Completed",
        "Num. Discontinued",
        ]
    writer = csv.DictWriter(file_object_to_write_to, headers)
    writer.writeheader()
    for course in courses:
        statistics = CommitmentStatusStatistics(*course.associated_commitments_list).as_json()
        writer.writerow({
            "Course Identifier": course.identifier,
            "Course Title": course.title,
            "Start Date": course.start_date,
            "End Date": course.end_date,
            "Total Commitments": statistics["total"],
            "Num. In Progress": statistics["counts"]["in_progress"],
            "Num. Past Due": statistics["counts"]["expired"],
            "Num. Completed": statistics["counts"]["complete"],
            "Num. Discontinued": statistics["counts"]["discontinued"],
        })
