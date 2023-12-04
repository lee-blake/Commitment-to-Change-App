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
    is_clinician = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
