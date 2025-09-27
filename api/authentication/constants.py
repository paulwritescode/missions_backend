from django.conf import settings
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class AuthBackendType(TextChoices):
    """Authentication backend choices"""
    APPLE = "apple", _("Apple")
    GOOGLE = "google", _("Google")
    JWT = "jwt", _("JWT")

SUPPORTED_AUTH_BACKENDS = {AuthBackendType.APPLE, AuthBackendType.GOOGLE, AuthBackendType.JWT}

config_dict = {
    AuthBackendType.APPLE.value: {},
    AuthBackendType.GOOGLE.value: {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    },
    AuthBackendType.JWT.value: {},
}