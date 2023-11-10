from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_slug, RegexValidator, EmailValidator
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not email:
            raise ValueError("Users must register with an email address")
        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


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
