"""Settings specifically for local testing. Generally sets memory backends."""

from Commitment_to_Change_App.settings import * #pylint: disable=W0401, W0614

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
