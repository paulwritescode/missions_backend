"""
Authentication backend system using plugin architecture.
"""

from authentication.backends.base import AuthBackend
from authentication.backends.registry import registry, register_backend, get_backend

# Import all backend implementations to ensure they're registered
from authentication.backends.jwt import JWTAuthBackend
from authentication.backends.google import GoogleAuthBackend
from authentication.backends.apple import AppleAuthBackend

__all__ = [
    'AuthBackend',
    'registry',
    'register_backend',
    'get_backend',
    'JWTAuthBackend',
    'GoogleAuthBackend',
    'AppleAuthBackend',
]
