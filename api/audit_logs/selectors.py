from typing import Optional

from audit_logs.filters import AuditLogFilter
from audit_logs.models import AuditLog
from base.utils.exceptions import CustomValidationError


def audit_log_details(id: int) -> AuditLog:
    """
    Get details of an audit log entry by ID.

    Args:
        id: ID of the audit log entry.

    Returns:
        AuditLog instance.

    Raises:
        ValueError: If the AuditLog with the given ID does not exist.
    """
    try:
        return AuditLog.objects.get(id=id)
    except AuditLog.DoesNotExist:
        raise CustomValidationError("AuditLog with the the id {} does not exist.".format(id))


def audit_logs_list(filters: Optional[dict] = None):
    """
    List all audit log entries.

    Returns:
        List of AuditLog instances.
    """
    qs = AuditLog.objects.all().order_by('-timestamp')
    return AuditLogFilter(filters, qs).qs if filters else qs