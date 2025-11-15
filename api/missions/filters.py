from django_filters import rest_framework as filters

from base.filters import BaseFilterSet
from missions.constants import MissionStatusType
from missions.models import Location, Mission, MissionJIAParticipant, Report, MissionGallery



class LocationFilter(BaseFilterSet):
    parent_location_id = filters.NumberFilter(field_name='parent_location__id')
    category = filters.CharFilter(field_name='category', lookup_expr='iexact')
    search_fields = ['name',]

    class Meta:
        model = Location
        fields = ['category', 'parent_location_id']


class MissionFilter(BaseFilterSet):
    category_id = filters.NumberFilter(field_name='category__id')
    location_id = filters.NumberFilter(field_name='location__id')
    start_date_before = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    start_date_after = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    end_date_before = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    end_date_after = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    status = filters.CharFilter(field_name="status", lookup_expr="exact")
    registration_close_date_before = filters.DateFilter(field_name='registration_close_date', lookup_expr='lte')
    registration_close_date_after = filters.DateFilter(field_name='registration_close_date', lookup_expr='gte')
    search_fields = ['title',]

    class Meta:
        model = Mission
        fields = [
            'category_id', 'location_id', 'status', 'start_date_before', 'start_date_after',
            'end_date_before', 'end_date_after', 'registration_close_date_before',
            'registration_close_date_after', 'registration_fee_required'
        ]


class MissionJIAFilter(BaseFilterSet):
    mission_id = filters.NumberFilter(field_name='mission__id')
    user_id = filters.NumberFilter(field_name='user__id')
    search_fields = ['mission__title', 'full_name', 'phone_number',]
    gender = filters.CharFilter(field_name='gender', lookup_expr="iexact")

    class Meta:
        model = MissionJIAParticipant
        fields = ['mission_id', 'user_id', 'need_facilitation', 'gender']


class ReportsFilter(BaseFilterSet):
    mission_id = filters.NumberFilter(field_name='mission__id')
    created_by_id = filters.NumberFilter(field_name='created_by__id')
    search_fields = ['mission__title', 'created_by__first_name', 'created_by__last_name',]

    class Meta:
        model = Report
        fields = ['mission_id', 'created_by_id']


class MissionGalleryFilter(BaseFilterSet):
    mission_id = filters.NumberFilter(field_name='mission__id')
    uploaded_by_id = filters.NumberFilter(field_name='uploaded_by__id')

    class Meta:
        model = MissionGallery
        fields = ['mission_id', 'uploaded_by_id']
