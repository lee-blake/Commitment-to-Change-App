from commitments.enums import CommitmentStatus


class CommitmentStatusStatistics:
    @staticmethod
    def aggregate(*commitment_status_statistics_objects):
        status_counts = {}
        for status in CommitmentStatus.values:
            status_counts[status] = 0
        for stats_object in commitment_status_statistics_objects:
            for status in CommitmentStatus.values:
                status_counts[status] += stats_object.count_with_status(status)
        return CommitmentStatusStatistics(status_counts)

    @staticmethod
    def from_commitment_list(*commitments):
        return CommitmentStatusStatistics(
            CommitmentStatusStatistics._count_statuses(*commitments)
        )

    @staticmethod
    def _count_statuses(*commitments):
        status_counts = {}
        for status in CommitmentStatus.values:
            status_counts[status] = 0
        for commitment in commitments:
            status_counts[commitment.status] += 1
        return status_counts

    def __init__(self, status_counts):
        self._status_counts = status_counts
        self._total = self._get_total()
        self._internal_dict_representation = self._as_dict()

    def __getitem__(self, key):
        return self._internal_dict_representation[key]

    def _get_total(self):
        total = 0
        for status in CommitmentStatus.values:
            total += self._status_counts[status]
        return total

    def total(self):
        return self._total

    def count_with_status(self, status):
        return self._status_counts[status]

    def fraction_with_status(self, status):
        return self._status_counts[status]/self._total

    def percentage_with_status(self, status):
        return 100*self.fraction_with_status(status)

    def _as_dict(self):
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
