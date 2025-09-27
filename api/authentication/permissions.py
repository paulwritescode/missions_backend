# Custom authentication for Django Ninja
from django.contrib.auth.models import User
from django.http import HttpRequest


def get_user(request: HttpRequest) -> User:
    """
    Authentication function for Django Ninja.

    This can be used with NinjaAPI's authentication parameter.
    """
    user = request.user
    if user and user.is_authenticated:
        return user
    return None