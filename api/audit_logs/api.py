from typing import List

from ninja import Router

from audit_logs import schemas
from audit_logs.selectors import audit_log_details, audit_logs_list
from audit_logs.services import flag_suspicious_log, unflag_suspicious_log
from authentication.decorators import require_permission
from authentication.permissions import jwt_auth
from base.api import paginate_response
from base.schemas import DetailOut

router = Router(tags=["audit_logs"])


@router.get(
    "/{id}/",
    auth=jwt_auth,
    response={200: schemas.AuditLogSchema, 400: DetailOut},
)
@require_permission("view_auditlog")
def get_audit_log(request, id: int):
    """
    Retrieve details of a specific audit log entry by its ID.
    """
    audit_log = audit_log_details(id)
    return audit_log


@router.get(
    "/",
    auth=jwt_auth,
    response={200: List[schemas.AuditLogSchema], 400: DetailOut},
)
@require_permission("list_auditlogs")
def list_audit_logs(request, filters: schemas.AuditLogQueryIn = None):
    """
    List all audit log entries with optional filters.
    """
    audit_logs = audit_logs_list(filters)
    return paginate_response(
        request=request,
        queryset=audit_logs,
        schema=schemas.AuditLogSchema,
        page_size=filters.page_size,
        page=filters.page,
    )


@router.post(
    "/{id}/flag_suspicious/",
    auth=jwt_auth,
    response={200: schemas.AuditLogSchema, 400: DetailOut},
)
@require_permission("flag_suspicious_auditlog")
def flag_suspicious_audit_log_api(request, id: int):
    """
    Flag an audit log entry as suspicious.
    """
    audit_log = flag_suspicious_log(id)
    return audit_log


@router.post(
    "/{id}/unflag_suspicious/",
    auth=jwt_auth,
    response={200: schemas.AuditLogSchema, 400: DetailOut},
)
@require_permission("unflag_suspicious_auditlog")
def unflag_suspicious_audit_log_api(request, id: int):
    """
    Unflag an audit log entry as suspicious.
    """
    audit_log = unflag_suspicious_log(id)
    return audit_log
