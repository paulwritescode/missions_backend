from django_filters import rest_framework as filters
from users.models import Role, User


class UserFilter(filters.FilterSet):
    roles = filters.ModelMultipleChoiceFilter(field_name='roles__name', to_field_name='name', queryset=Role.objects.all())
    is_active = filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = User
        fields = ['email', 'roles', 'is_active']


class RoleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Role
        fields = ['name']