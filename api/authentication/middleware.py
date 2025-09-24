"""
Authentication middleware and utilities.
"""
from typing import Optional

from django.conf import settings
from django.http import JsonResponse
from django.utils.functional import SimpleLazyObject

from authentication.backends import get_backend, registry


def get_user_from_request(request):
    """
    Get the authenticated user from the request.

    This is a lazy function that will only authenticate the user when needed.
    """
    if hasattr(request, '_cached_user'):
        return request._cached_user

    user = None
    auth_header = request.headers.get('Authorization', '')

    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        user = authenticate_with_token(token)

    request._cached_user = user
    return user


def authenticate_with_token(token: str) -> Optional[object]:
    """
    Authenticate a user with a token using available backends.

    This tries each backend in order of priority until one succeeds.

    Args:
        token: Authentication token

    Returns:
        User object if authentication is successful, None otherwise
    """
    from users.models import User, AuthProvider

    # Try to find a backend that can handle this token
    for provider_name in registry.keys():
        backend = get_backend(provider_name)
        if not backend:
            continue

        user_id = backend.get_user_id_from_token(token)
        if not user_id:
            continue

        # Check if we have a user with this provider ID
        try:
            auth_provider = AuthProvider.objects.get(name=provider_name, is_active=True)
            user_auth = auth_provider.user_auth_providers.get(provider_user_id=user_id)
            user = user_auth.user

            # Update last used timestamp
            user_auth.mark_as_used()

            return user
        except (AuthProvider.DoesNotExist, User.DoesNotExist):
            continue

    return None


class JWTAuthenticationMiddleware:
    """
    Middleware that authenticates users via JWT tokens.

    This middleware adds the authenticated user to the request if a valid
    JWT token is provided in the Authorization header.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add user to request as a lazy object to avoid unnecessary database lookups
        request.user = SimpleLazyObject(lambda: get_user_from_request(request))
        return self.get_response(request)
