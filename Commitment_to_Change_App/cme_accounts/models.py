from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_slug, RegexValidator, EmailValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, validators=[
        validate_slug,
        RegexValidator(
            regex="^[a-zA-Z]",
            code="invalid_username",
            message="Username must start with a letter."
        )
    ])
    email = models.EmailField(max_length=254, validators=[
        EmailValidator()
    ])
    # Django should use one model for user authentication and one model only. Inheritance is
    # greatly discouraged as it can cause issues. As such, we split the different account
    # types into this User class and a profile class. These booleans are here to allow fast
    # authentication decisions about where on the site a user is generally not allowed.
    # Marking account type with booleans is also the standard practice in Django - this user model
    # inherits an is_staff boolean marking admin accounts.
    is_clinician = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
