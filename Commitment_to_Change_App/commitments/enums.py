from django.db.models import IntegerChoices

class CommitmentStatus(IntegerChoices):
    # While this may seem to depend on Django, IntegerChoices is mostly just enum.Enum with some
    # nice helper methods for getting names and choices for the database. If we move frameworks
    # we can switch this to enum.Enum without damaging the business logic.
    IN_PROGRESS = 0
    COMPLETE = 1
    EXPIRED = 2
    DISCONTINUED = 3

    def __str__(self):
        match self:
            case 0:
                return "In Progress"
            case 1:
                return "Complete"
            case 2:
                return "Past Due"
            case 3:
                return "Discontinued"
