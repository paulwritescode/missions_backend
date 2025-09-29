from typing import Optional

from django.db.models import Q

from authentication import permissions_list
from base.utils.exceptions import CustomValidationError
from users.filters import UserFilter, RoleFilter
from users.models import User, Role


def role_details(role_id: int) -> Optional[Role]:
    """Get role details by ID"""
    try:
        return Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        raise CustomValidationError("Role with the given ID does not exist")


def user_details(user_id: Optional[int] = None, email: Optional[str] = None) -> Optional[User]:
    """Get user details by ID or email"""

    try:
        if user_id is not None:
            return User.objects.get(id=user_id)
        elif email is not None:
            return User.objects.get(email=email.lower())
        else:
            raise CustomValidationError("Either user_id or email must be provided")
    except User.DoesNotExist:
        raise CustomValidationError("User with the given identifier does not exist")


def users_list(filters: dict = None):
    """Get list of users with optional filters"""
    if filters is None:
        filters = {}
    queryset = User.objects.all().order_by('id')
    search = filters.pop('search', None)
    if search:
        queryset = queryset.filter(
            (Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))
        )
    user_filter = UserFilter(filters, queryset=queryset)
    return user_filter.qs


def roles_list(filters: dict = None):
    """Get list of roles with optional filters"""
    queryset = Role.objects.all().order_by('id')
    if filters:
        roles_filter = RoleFilter(filters, queryset=queryset)
        return roles_filter.qs
    return queryset


def list_permissions(user_type: Optional[str] = None) -> list[str]:
    """Get list of permissions for a given user type"""
    role_map = {
        'missioner': permissions_list.MISSIONER_PERMISSIONS,
        'admin': permissions_list.ADMIN_PERMISSIONS,
        'exec': permissions_list.EXEC_PERMISSIONS,
        'staff': permissions_list.STAFF_PERMISSIONS,
    }
    if not user_type:
        return list(permissions_list.ALL_PERMISSIONS)
    return list(role_map.get(user_type.lower(), []))
