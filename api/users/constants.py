
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


class AgeGroupCategory(TextChoices):
    """Age group categories aligned with common social and developmental stages."""
    CHILD = "0-12", _("Child (0–12 years)")
    YOUNG_TEEN = "13-17", _("Young Teen (13–17 years)")
    YOUNG_ADULT = "18-24", _("Young Adult (18–24 years)")
    ADULT = "25-39", _("Adult (25–39 years)")
    MATURE_ADULT = "40-59", _("Mature Adult (40–59 years)")
    SENIOR = "60+", _("Senior (60 years and above)")
