"""
Main authentication module for handling user authentication across the system.
"""

from authentication.backends import (
    registry, get_backend, register_backend,
    JWTAuthBackend, GoogleAuthBackend, AppleAuthBackend
)
from authentication.middleware import authenticate_with_token
from authentication.utils import get_auth_for_user, create_auth_token


__all__ = [
    'registry', 
    'get_backend', 
    'register_backend',
    'JWTAuthBackend', 
    'GoogleAuthBackend', 
    'AppleAuthBackend',
    'authenticate_with_token',
    'get_auth_for_user',
    'create_auth_token',
]