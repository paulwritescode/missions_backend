"""
Base authentication backend classes and interfaces.
"""
from abc import ABC, abstractmethod
from pprint import pprint
from typing import Any, Dict, Optional, Tuple

from django.http import HttpRequest


class AuthBackend(ABC):
    """
    Base class for all authentication backends.

    All authentication backends must implement this interface to be used in the system.
    The backend system uses a plugin architecture where backends register themselves
    and can be retrieved by name.
    """

    # Unique identifier for the auth backend type
    name: str = None

    # Human-readable display name
    display_name: str = None

    # Whether this backend can be used for user registration
    supports_registration: bool = False

    # Whether this backend requires additional configuration
    requires_config: bool = False

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the auth backend with optional configuration.

        Args:
            config: A dictionary of configuration parameters for this backend.
        """
        self.config = config or {}

    def validate_config(self) -> None:
        """
        Validate the backend configuration.

        Raises:
            ValueError: If configuration is invalid.
        """
        if self.requires_config and not self.config:
            raise ValueError(f"{self.display_name} backend requires configuration")

    @abstractmethod
    def authenticate(self, request: HttpRequest, **kwargs) -> Tuple[bool, dict, Optional[str]]:
        """
        Authenticate a user with this backend.

        Args:
            request: The current HTTP request.
            **kwargs: Additional authentication parameters specific to this backend.

        Returns:
            Tuple containing:
            - Success flag (True if authentication successful)
            - User data dictionary (contains provider_user_id, email, and optionally other profile data)
            - Error message (None if successful, error description if failed)
        """
        pass

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract the user identifier from a token.

        Args:
            token: The auth token specific to this backend.

        Returns:
            The unique provider user ID extracted from the token, or None if invalid.
        """
        pass

    def get_auth_url(self) -> str:
        """
        Get the authorization URL for OAuth-based flows.

        Returns:
            The URL to redirect to for starting the OAuth flow.
        """
        raise NotImplementedError(f"{self.name} backend does not support authorization URLs")

    def extract_auth_token(self, request: HttpRequest) -> Optional[str]:
        """
        Extract authentication token from request.

        Args:
            request: The HTTP request.

        Returns:
            The extracted token or None if not found.
        """
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def __str__(self) -> str:
        return self.display_name or self.name

    def decode_token(self, access_token):
        pass
