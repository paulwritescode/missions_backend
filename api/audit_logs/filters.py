from django_filters import rest_framework as filters

from audit_logs.models import AuditLog
from base.filters import BaseFilterSet


class AuditLogFilter(BaseFilterSet):
    user_id = filters.NumberFilter(field_name="user__id")
    ip_address = filters.CharFilter(field_name="ip_address", lookup_expr="iexact")

    class Meta:
        fields = '__all__'
        model = AuditLog
