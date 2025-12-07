from typing import Dict, Any

from django.db import models
from django.http import HttpRequest

from audit_logs.constants import ActionType
from base.models import BaseModel


class AuditLog(BaseModel):
    user = models.ForeignKey("users.User", on_delete=models.PROTECT)
    action_type = models.CharField(choices=ActionType.choices, max_length=50)
    action_category = models.CharField(max_length=100)
    action_description = models.CharField(max_length=300)
    is_successful = models.BooleanField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    flag_suspicious = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['action_category']),
            models.Index(fields=['is_successful']),
            models.Index(fields=['flag_suspicious']),
            models.Index(fields=['ip_address'])
        ]
        db_table = 'audit_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"AuditLog {self.pk} - {self.action_category} by User {self.user.pk}"

    def to_dict(self, request: HttpRequest = None) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "user_id": self.user.id if self.user else None,
            "ip_address": str(self.ip_address) if self.ip_address else None,
        })
        return data