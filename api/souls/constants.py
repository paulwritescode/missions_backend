from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class SoulStatus(TextChoices):
    ACTIVE = "active", _("Active")
    NEW_CONVERT = "new_convert", _("New convert")
    FOLLOW_UP = "follow_up", _("Follow up")
