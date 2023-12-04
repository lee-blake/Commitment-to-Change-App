import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from cme_accounts.models import User


class TestUser:
    """Tests for User"""

    @pytest.fixture(name="required_field_names")
    def fixture_required_field_names(self):
        return ["username", "password", "email"]


    class TestInit:
        """Tests for User.__init__"""

        def test_is_clinician_field_defaults_correctly(self):
            user = User(username="username", email="a@b.c", password="password")
            assert not user.is_clinician

        def test_is_provider_field_defaults_correctly(self):
            user = User(username="username", email="a@b.c", password="password")
            assert not user.is_provider


    class TestUsernameValidation:
        """Tests for validation of User.username"""

        @pytest.fixture(name="ignore_non_username_fields")
        def fixture_ignore_non_username_fields(self, required_field_names):
            required_field_names.remove("username")
            return required_field_names


        def test_empty_username_is_not_valid(self, ignore_non_username_fields):
            user = User(username="")
            with pytest.raises(ValidationError):
                user.clean_fields(ignore_non_username_fields)

        def test_non_slug_username_is_not_valid(self, ignore_non_username_fields):
            user = User(username="A*")
            with pytest.raises(ValidationError):
                user.clean_fields(ignore_non_username_fields)

        def test_non_letter_starting_username_is_not_valid(self, ignore_non_username_fields):
            user = User(username="-A", )
            with pytest.raises(ValidationError):
                user.clean_fields(ignore_non_username_fields)
        
        def test_letter_starting_slug_username_is_valid(self, ignore_non_username_fields):
            user = User(username="slug-test_name007")
            user.clean_fields(ignore_non_username_fields)

        @pytest.mark.django_db
        def test_username_enforces_uniqueness(self):
            User.objects.create(username="a", email="a@localhost", password="password")
            user = User(username="a", email="root@localhost", password="password")
            with pytest.raises(IntegrityError):
                user.save()


    class TestEmailValidation:
        """Tests for validation of User.email"""

        @pytest.fixture(name="ignore_non_email_fields")
        def fixture_ignore_non_email_fields(self, required_field_names):
            required_field_names.remove("email")
            return required_field_names

        
        def test_empty_email_is_not_valid(self, ignore_non_email_fields):
            user = User(email="")
            with pytest.raises(ValidationError):
                user.clean_fields(ignore_non_email_fields)

        def test_no_at_sign_email_is_not_valid(self, ignore_non_email_fields):
            user = User(email="HA")
            with pytest.raises(ValidationError):
                user.clean_fields(ignore_non_email_fields)

        def test_bad_domain_email_is_not_valid(self, ignore_non_email_fields):
            user = User(email="a@")
            with pytest.raises(ValidationError):
                user.clean_fields(ignore_non_email_fields)

        def test_too_long_email_is_not_valid(self, ignore_non_email_fields):
            too_long_255_characters = "a"*249 + "@b.com"
            assert len(too_long_255_characters) == 255
            user = User(email=too_long_255_characters)
            with pytest.raises(ValidationError):
                user.clean_fields(ignore_non_email_fields)

        def test_local_email_is_valid(self, ignore_non_email_fields):
            user = User(email="root@localhost")
            user.clean_fields(ignore_non_email_fields)

    class TestPasswordValidation:
        """Tests for validation of User.password
        
        Note that we only test that empty passwords are disallowed because Django
        handles password policies at the form and CLI level. Duplicating the code
        is a recipe for bugs. It is also not desirable to enforce the same policies at 
        this level because policy changes generally make passwords more complicated. 
        This means that sample passwords in unit tests would need changing every time 
        the password policy changes."""

        @pytest.fixture(name="ignore_non_password_fields")
        def fixture_ignore_non_password_fields(self, required_field_names):
            required_field_names.remove("password")
            return required_field_names


        def test_empty_password_is_not_valid(self, ignore_non_password_fields):
            user = User(password="")
            with pytest.raises(ValidationError):
                user.clean_fields(ignore_non_password_fields)
