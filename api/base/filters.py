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
