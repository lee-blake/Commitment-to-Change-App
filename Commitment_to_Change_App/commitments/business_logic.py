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

    @property
    def statistics(self):
        derived_status_counts = self._compute_derived_commitment_status_counts()
        derived_status_percentages = self._compute_derived_commitment_status_percentages(
            derived_status_counts
        )
        return {
            "derived_commitments": {
                "statuses": {
                    "counts": derived_status_counts,
                    "percentages": derived_status_percentages
                }
            }
        }

    def _compute_derived_commitment_status_counts(self):
        status_counts = {
            CommitmentStatus.IN_PROGRESS: 0,
            CommitmentStatus.COMPLETE: 0,
            CommitmentStatus.DISCONTINUED: 0,
            CommitmentStatus.EXPIRED: 0,
            }
        for commitment in self.derived_commitments:
            status_counts[commitment.status] += 1
        return {
            "in_progress": status_counts[CommitmentStatus.IN_PROGRESS],
            "complete": status_counts[CommitmentStatus.COMPLETE],
            "discontinued": status_counts[CommitmentStatus.DISCONTINUED],
            "expired": status_counts[CommitmentStatus.EXPIRED],
            "total": len(self.derived_commitments)
        }

    def _compute_derived_commitment_status_percentages(self, status_counts):
        status_names = ["in_progress", "complete", "discontinued", "expired"]
        status_percentages = {}
        total_commitments = status_counts["total"]
        for status_name in status_names:
            if total_commitments == 0:
                status_percentages[status_name] = "N/A"
            else:
                status_percentages[status_name] = \
                    100 * status_counts[status_name] / total_commitments
        return status_percentages


class CourseLogic:
    def __init__(self, data_object):
        self._data = data_object
        self._statistics = None

    def __str__(self):
        return self._data.title.__str__()

    @property
    def statistics(self):
        if not self._statistics:
            self._statistics =  {
                "associated_commitments": {
                    "total": len(self._data.associated_commitments_list),
                    "statuses": self._compute_associated_commitment_statuses()
                }
            }
        return self._statistics

    def _compute_associated_commitment_statuses(self):
        stats_object = {
            "in_progress": 0,
            "complete": 0,
            "past_due": 0,
            "discontinued": 0
        }
        for commitment in self._data.associated_commitments_list:
            match commitment.status:
                case CommitmentStatus.IN_PROGRESS:
                    stats_object["in_progress"] += 1
                case CommitmentStatus.COMPLETE:
                    stats_object["complete"] += 1
                case CommitmentStatus.EXPIRED:
                    stats_object["past_due"] += 1
                case CommitmentStatus.DISCONTINUED:
                    stats_object["discontinued"] += 1
        return stats_object

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
        # This course logic is a wrapper to make testing work without adding extra properties
        # to CourseLogic. It is questionable code and should be removed by moving the statistics
        # logic to another class.
        course_logic = CourseLogic(course)
        writer.writerow({
            "Course Identifier": course.identifier,
            "Course Title": course.title,
            "Start Date": course.start_date,
            "End Date": course.end_date,
            "Total Commitments": course_logic.statistics["associated_commitments"]["total"],
            "Num. In Progress": \
                course_logic.statistics["associated_commitments"]["statuses"]["in_progress"],
            "Num. Past Due": \
                course_logic.statistics["associated_commitments"]["statuses"]["past_due"],
            "Num. Completed": \
                course_logic.statistics["associated_commitments"]["statuses"]["complete"],
            "Num. Discontinued": \
                course_logic.statistics["associated_commitments"]["statuses"]["discontinued"],
        })
