"""This script will populate the database with a reasonable number of courses, as well
as supporting clinician accounts to make commitments in those courses.

Variants of this script should be created by copying this file rather than modifying it.

To run this script, pass it to the Django manage.py shell:
https://docs.djangoproject.com/en/5.0/ref/django-admin/#shell"""

import datetime
import random

from django.core.exceptions import ObjectDoesNotExist

from cme_accounts.models import User
from commitments.enums import CommitmentStatus
from commitments.models import ClinicianProfile, ProviderProfile, Commitment, Course, \
    CommitmentTemplate


LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod " \
    + "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis " \
    + "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. " \
    + "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu " \
    + "fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in " \
    + "culpa qui officia deserunt mollit anim id est laborum."


ONE_YEAR_AGO = datetime.date.today() - datetime.timedelta(days=365)
ONE_YEAR_FROM_NOW = datetime.date.today() + datetime.timedelta(days=365)

def random_date_within(start_date, end_date):
    days_between = (end_date-start_date).days
    random_days_from_start = random.randint(0, days_between)
    return start_date + datetime.timedelta(days=random_days_from_start)

class ClinicianBuilder:
    # Taken from the 2010 census and SSA:
    # https://www.census.gov/topics/population/genealogy/data/2010_surnames.html
    # https://www.ssa.gov/oact/babynames/decades/names2010s.html
    FIRST_NAMES = ["James", "Robert", "John", "Michael", "David", "William", "Richard", \
        "Joseph", "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", \
        "Mark", "Donald", "Steven", "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", \
        "Brian", "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", \
        "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", \
        "Scott", "Brandon", "Benjamin", "Samuel", "Gregory", "Alexander", "Patrick", \
        "Frank", "Raymond", "Jack", "Dennis", "Jerry", "Mary", "Patricia", "Jennifer", \
        "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa", \
        "Nancy", "Betty", "Sandra", "Margaret", "Ashley", "Kimberly", "Emily", "Donna", \
        "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Dorothy", \
        "Rebecca", "Sharon", "Laura", "Cynthia", "Amy", "Kathleen", "Angela", "Shirley", \
        "Brenda", "Emma", "Anna", "Pamela", "Nicole", "Samantha", "Katherine", \
        "Christine", "Helen", "Debra", "Rachel", "Carolyn", "Janet", "Maria", \
        "Catherine", "Heather"
    ]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", \
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", \
        "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", \
        "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", \
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", \
        "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", \
        "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", \
        "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", \
        "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", \
        "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", \
        "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", \
        "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", \
        "Long", "Ross", "Foster", "Jimenez"
    ]

    def build_clinician(self):
        random_first_name = random.choice(self.FIRST_NAMES)
        random_last_name = random.choice(self.LAST_NAMES)
        username_count = None
        while username_count != 0:
            random_number = random.randint(1,9999)
            username = f"{random_first_name.lower()}_{random_last_name.lower()}{random_number}"
            username_count = User.objects.filter(username=username).count()
        user = User.objects.create(
            username=username,
            email=f"{username}@localhost",
            password="password",
            is_clinician=True
        )
        user.set_password("password")
        user.save()
        return ClinicianProfile.objects.create(
            user=user,
            first_name=random_first_name,
            last_name=random_last_name
        )

    def build_clinician_list(self, length):
        return [self.build_clinician() for i in range(0, length)]


class CommitmentTemplateBuilder:
    # These are deliberately generic because they are randomly assigned to courses.
    COMMITMENT_TEMPLATE_TITLES = [
        "Wash hands before surgery",
        "Proofread records after appointments",
        "Use new scoring system for risk factors",
        "Review diagnosis criteria",
        "Apply goals of care communication techniques",
        "Reexamine personal biases each week",
        "Consider substance abuse risks for patient medications",
        "Verify AI assistant is not hallucinating",
        "Avoid fallacies in statistical reasoning",
        "Apply best practices for virtual visits"
    ]
    def __init__(self, owner):
        self._owner = owner

    def build_commitment_template(self, title):
        return CommitmentTemplate.objects.create(
            title=title,
            description=LOREM_IPSUM,
            owner=self._owner
        )

    def build_commitment_template_list(self):
        return [
            self.build_commitment_template(title) for title in self.COMMITMENT_TEMPLATE_TITLES
        ]


class CourseBuilder:
    # Use actual course titles to see how they will render
    COURSE_TITLES = [
        "CAR T-Cell Translation: The State of the Art",
        "Mastering Presence in Virtual Visits through Relationship-Centered Communication (ACES 2.0)",
        "Preventing Heart Disease",
        "Cue-Centered Therapy: Advanced Theory and Practice of Cue-Centered Therapy",
        "Master Clinician Series 2024 March: Treating Persecutory Delusions: an Introduction to the Feeling Safe Programme",

        "Compassion Cultivation Training For Physicians and Psychologists",
        "Pediatric Orthopedics and Sports Medicine Lecture Series: At Home Remedies",
        "Stanford Maintenance of Certification in Anesthesiology (MOCA) Course",
        "Coding Evaluation and Management Guidelines: Level of Service 3 vs. 4",
        "AI + Health 2023 On-Demand",

        "Innovation Insights: Gamification in Pediatric Pain Management",
        "Hypertension in Primary Care - Improving Control and Reducing Risk",
        "SafetyQuest: Level One - QI Basics",
        "Medicine for a Changing Planet: Emerging Zoonoses",
        "Essential Emergency and Critical Care",

        "Symptom Management in Palliative Care",
        "Septris 2.0 | Simulated Education to Teach Providers to Recognize and Treat Sepsis",
        "AI Series: Evaluations of AI Applications in Healthcare",
        "Targeting the Metabolic Processes of Nonalcoholic Steatohepatitis in Treatment Decisions",
        "Telehealth: Strategy, Implementation, and Optimization"
    ]
    MIN_SUGGESTED_COMMITMENTS = 2
    MAX_SUGGESTED_COMMITMENTS = 5
    MIN_CLINICIANS = 10
    MAX_CLINICIANS = 30

    def __init__(self, owner, commitment_templates, clinicians):
        self._owner = owner
        self._commitment_templates = commitment_templates
        self._clinicians = clinicians

    def build_course(self):
        course = self._create_course_object()
        self._attach_suggested_commitments(course)
        self._attach_clinicians(course)
        self._make_commitments(course)
        course.save()
        return course

    def _create_course_object(self):
        title = random.choice(self.COURSE_TITLES)
        start_date = datetime.date.today() + datetime.timedelta(
            days=random.randint(-365, 365)
        )
        end_date = start_date + datetime.timedelta(days=random.randint(0,180))
        identifier = str(random.randint(0,100000))
        course = Course.objects.create(
            owner=self._owner,
            title=title,
            description=LOREM_IPSUM,
            identifier=identifier,
            start_date=start_date,
            end_date=end_date
        )
        course.generate_join_code_if_none_exists(8)
        course.save()
        return course

    def _attach_suggested_commitments(self, course):
        num_suggested_commitments = random.randint(
            self.MIN_SUGGESTED_COMMITMENTS, self.MAX_SUGGESTED_COMMITMENTS
        )
        random_suggested_commitments = random.sample(
            self._commitment_templates, num_suggested_commitments
        )
        course.suggested_commitments.add(*random_suggested_commitments)

    def _attach_clinicians(self, course):
        num_clinicians = random.randint(self.MIN_CLINICIANS, self.MAX_CLINICIANS)
        random_students = random.sample(self._clinicians, num_clinicians)
        course.students.add(*random_students)

    def _make_commitments(self, course):
        commitment_maker = CommitmentMaker(course)
        commitment_maker.make_commitments()

    def build_course_list(self, length):
        return [self.build_course() for i in range(0, length)]


class CommitmentMaker:
    # These are deliberately more generic to distinguish from suggested commitments.
    GENERIC_COMMITMENT_TITLES = [
        "Follow standard operating procedure in the operating room",
        "Practice seeing patients in the new practice",
        "Review pull requests for medical software updates",
        "Test medical intern on lessons learned",
        "Recommend best hospital dishes for patient comfort",
        "Clear accessible parking spots during winter",
        "Inspect medical equipment for safety issues",
        "Optimize room allocation to improve response times",
        "Participate in team-building exercises by watching Colts games",
        "Add more posters to exam rooms"
    ]
    MIN_CLINICIAN_MAKES_ANY_COMMITMENT_PROBABILITY = 0.7
    MAX_CLINICIAN_MAKES_ANY_COMMITMENT_PROBABILITY = 1
    MIN_SUGGESTED_COMMITMENT_PROBABILITY = 0.4
    MAX_SUGGESTED_COMMITMENT_PROBABILITY = 0.8
    MIN_COMMITMENT_DURATION = 30
    MAX_COMMITMENT_DURATION = 180

    def __init__(self, course):
        self._course = course
        self._setup_unique_probabilities_for_course()
        self._commitment_statuses = list(CommitmentStatus.values)

    def _setup_unique_probabilities_for_course(self):
        # Vary the behavior of clinicians among courses
        self._clinician_makes_any_commitment_probability = random.uniform(
            self.MIN_CLINICIAN_MAKES_ANY_COMMITMENT_PROBABILITY,
            self.MAX_CLINICIAN_MAKES_ANY_COMMITMENT_PROBABILITY
        )
        self._clinician_makes_suggested_commitment = random.uniform(
            self.MIN_SUGGESTED_COMMITMENT_PROBABILITY,
            self.MAX_SUGGESTED_COMMITMENT_PROBABILITY
        )
        self._status_weights = [random.random() for status in CommitmentStatus.values]

    def make_commitments(self):
        for student in self._course.students.all():
            self._take_actions_for_student(student)

    def _take_actions_for_student(self, student):
        if random.random() > self._clinician_makes_any_commitment_probability:
            return
        commitment = self._make_commitment_for_student(student)
        if random.random() < self._clinician_makes_suggested_commitment:
            self._convert_to_suggested_commitment(commitment)

    def _make_commitment_for_student(self, student):
        commitment_length = random.randint(
            self.MIN_COMMITMENT_DURATION, self.MAX_COMMITMENT_DURATION
        )
        deadline = self._course.end_date + datetime.timedelta(days=commitment_length)
        status = random.choices(self._commitment_statuses, self._status_weights)[0]
        return Commitment.objects.create(
            owner=student,
            title=random.choice(self.GENERIC_COMMITMENT_TITLES),
            description=LOREM_IPSUM,
            deadline=deadline,
            status=status,
            associated_course=self._course
        )

    def _convert_to_suggested_commitment(self, commitment):
        random_suggested_commitment = random.choice(
            self._course.suggested_commitments.all()
        )
        commitment.apply_commitment_template(random_suggested_commitment)
        commitment.save()


class DatabasePopulator:
    PROVIDER_USERNAME = "testdata-provider"
    CLINICIAN_COUNT = 50
    COURSE_COUNT = 30

    def get_or_create_provider_profile(self):
        try:
            user = User.objects.get(username=self.PROVIDER_USERNAME)
            return ProviderProfile.objects.get(user=user)
        except ObjectDoesNotExist:
            user = User.objects.create(
                username=self.PROVIDER_USERNAME,
                email=f"{self.PROVIDER_USERNAME}@localhost",
                password="password",
                is_provider=True
            )
            user.set_password("password")
            user.save()
            return ProviderProfile.objects.create(
                user=user,
                institution="BSU"
            )

    def populate_database(self):
        provider_profile = self.get_or_create_provider_profile()
        clinicians = ClinicianBuilder().build_clinician_list(self.CLINICIAN_COUNT)
        commitment_templates = CommitmentTemplateBuilder(
            provider_profile
        ).build_commitment_template_list()
        CourseBuilder(
            provider_profile, commitment_templates, clinicians
        ).build_course_list(self.COURSE_COUNT)


if __name__ == "__main__" or __name__ == "django.core.management.commands.shell":
    DatabasePopulator().populate_database()
