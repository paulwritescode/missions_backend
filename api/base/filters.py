from django.db.models import Q
from django_filters import rest_framework as filters


class ListFilter(filters.Filter):
    """
    Expects a comma separated list
    filters values in list
    """

    def filter(self, qs, value):
        if value:
            return qs.filter(**{self.field_name + "__in": value.split(",")})
        return qs


class CharFilter(filters.CharFilter):
    """
    Case insensitive contains filter
    """

    def filter(self, qs, value):
        if value:
            return qs.filter(**{self.field_name + "__icontains": value})
        return qs


class BaseFilterSet(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    end_date = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    search = filters.CharFilter(method="filter_search")

    # Define this to be overridden by subclasses
    search_fields: list[str] = []

    def filter_search(self, queryset, name, value):
        if not value or not self.search_fields:
            return queryset

        queries = Q()
        for field in self.search_fields:
            queries |= Q(**{f"{field}__icontains": value})
        return queryset.filter(queries)
