from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    # TODO Create a validator to prevent the username from being an email and register here
    email = models.EmailField(max_length=254, unique=True)
