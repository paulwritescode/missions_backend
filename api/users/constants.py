
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class AuthProviderType(TextChoices):
    """Authentication provider choices"""
    GOOGLE = "google", _("Google")
    APPLE = "apple", _("Apple")
    JWT = "jwt", _("JWT")


class GenderType(TextChoices):
    """Gender choices"""
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
