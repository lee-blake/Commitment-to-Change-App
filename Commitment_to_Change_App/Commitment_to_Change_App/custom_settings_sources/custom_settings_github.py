"""This file contains defaults for custom settings that are unique to your Django
instance. If you want to override anything in settings.py specific to your instance
only, you should do it by adding the respective variable in this file. You should
not do so in settings.py because that file is committed to the repo.

These defaults are for the GitHub CI workflow."""

# You must generate a secret key for your server. Run the following code
# in your terminal to do so and then copy it between the quotes:
# python -c "import secrets; print(secrets.token_urlsafe())"
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Memory-only since console printing is not needed for the CI
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
