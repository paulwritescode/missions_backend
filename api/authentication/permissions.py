# Custom authentication for Django Ninja
from ninja.security import HttpBearer

from users.models import User
from django.http import HttpRequest
from typing import Optional
from django.http import HttpRequest
from authentication.backends.jwt import JWTAuthBackend


def get_user(request: HttpRequest) -> User:
    """
    Authentication function for Django Ninja.

    This can be used with NinjaAPI's authentication parameter.
    """
    user = request.user
    if user and user.is_authenticated:
        return user
    return None


class JWTCustomAuth(HttpBearer):
    def authenticate(self, request, token):
        success, user_data, error = JWTAuthBackend().authenticate(request)
        if not success:
            return None
        try:
            user = User.objects.get(id=user_data["provider_user_id"])
        except User.DoesNotExist:
            return None
        request.user = user
        return user


jwt_auth = JWTCustomAuth()

def has_role_type(role_type: str, roles=None, user=None) -> bool:
    if roles is None and user is None:
        return False
    if roles is None and user is not None:
        roles = user.roles.values_list('name', flat=True)
    role_names = list(roles)
    return any(role_type.lower() in role_name.lower() for role_name in role_names)
