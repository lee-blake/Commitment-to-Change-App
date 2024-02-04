"""This file contains defaults for custom settings that are unique to your Django
instance. If you want to override anything in settings.py specific to your instance
only, you should do it by adding the respective variable in this file. You should
not do so in settings.py because that file is committed to the repo.

These defaults are for the deployment instructions."""

# The TODOs in this file are intentional for the replicating user and are not a problem.
#pylint: disable=fixme

# TODO You must generate a secret key for your server. Run the following code
# in your terminal to do so and then copy it between the quotes:
# python -c "import secrets; print(secrets.token_urlsafe())"
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# TODO Turn this off once you have set up the server and verified it works!
DEBUG = True

# TODO Add the domain name/static IP that you will be accessing the server at.
# If you are using AWS and do not have a static IP, you will need to change this
# every time you start/reboot the server, unless you give it a value of ["*"].
# Outside of that situation, it is preferable to use the domain and static IPs only.
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',     # TODO set this to the database created when setting up PostgreSQL.
        'USER': '',     # TODO set this to the user created when setting up PostgreSQL.
        'PASSWORD': '', # TODO set this to the password you set when setting up PostgreSQL.
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# You can change this to "django.core.mail.backends.console.EmailBackend" to test the
# Django standalone server, but it won't be useful with Apache/mod_wsgi.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# TODO Configure your SMTP service details here
# Host & port for your SMTP service
EMAIL_HOST = ""
EMAIL_PORT = ""
# Set only one of these to true depending on your service
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
# Credentials for your SMTP service
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
# This will be the "from" email for every email sent by the server
DEFAULT_FROM_EMAIL = ""
