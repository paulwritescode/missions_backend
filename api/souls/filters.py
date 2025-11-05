from django_filters import rest_framework as filters
from base.filters import BaseFilterSet
from souls.models import Soul


class SoulFilter(BaseFilterSet):
    location_id = filters.NumberFilter(field_name='location__id')
    mission_id = filters.NumberFilter(field_name='mission__id')
    user_id = filters.NumberFilter(field_name='user__id')
    search_fields = ["first_name", "last_name", "phone_number"]
    created_before = filters.DateTimeFilter(field_name="uploaded_at", lookup_expr="lte")
    created_after = filters.DateTimeFilter(field_name="uploaded_at", lookup_expr="gte")

    class Meta:
        model = Soul
        fields = "__all__"
