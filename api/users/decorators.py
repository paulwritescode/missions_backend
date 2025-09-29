from functools import wraps
from django.http import JsonResponse


def require_permission(permission_tag):
    """
    Decorator to check permissions based on user role.
    Missioners automatically get access only to their own resources.

    Args:
        permission_tag: The permission required (e.g., "users:read")
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            # Authentication check
            if user is None:
                return JsonResponse(
                    {"detail": "Authentication credentials were not provided."},
                    status=401
                )
            if not user.is_active:
                return JsonResponse({"detail": "Your account is disabled."}, status=403)

            # Gather user roles and permissions
            user_roles = user.roles.all()
            role_names = [role.name.lower() for role in user_roles]
            user_permissions = set()
            for role in user_roles:
                if role.permissions:
                    user_permissions.update(role.permissions)

            # Helper function to check role type
            def has_role_type(role_type):
                return any(role_type in role_name for role_name in role_names)

            requested_user_id = kwargs.get('user_id')
            has_permission = permission_tag in user_permissions

            # Priority 1: Superuser/Admin - bypass all checks
            if user.is_superuser or has_role_type('superuser') or has_role_type('admin'):
                return func(request, *args, **kwargs)

            # Priority 2: Missioner - automatic self-access only
            if has_role_type('missioner'):
                if not has_permission:
                    return JsonResponse({"detail": "Permission denied"}, status=403)

                # Missioners can only access their own resources
                if requested_user_id and requested_user_id != user.id:
                    return JsonResponse(
                        {"detail": "You can only access your own details"},
                        status=403
                    )

                return func(request, *args, **kwargs)

            # Priority 3: Other roles - check permission only
            if has_permission:
                return func(request, *args, **kwargs)

            # No access granted
            return JsonResponse({"detail": "Permission denied"}, status=403)

        return wrapper

    return decorator