"""
Updated Google OAuth authentication backend implementation.
"""
from pprint import pprint
from typing import Dict, Optional, Tuple

import requests
from django.conf import settings
from django.http import HttpRequest
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from authentication.backends.base import AuthBackend
from authentication.backends.registry import register_backend
from authentication.constants import AuthBackendType


@register_backend
class GoogleAuthBackend(AuthBackend):
    """
    Google OAuth authentication backend.

    This backend handles authentication with Google's OAuth 2.0 service.
    Supports both web OAuth flow (with authorization codes) and mobile ID token verification.
    """
    name = AuthBackendType.GOOGLE.value
    display_name = AuthBackendType.GOOGLE.label
    supports_registration = True
    requires_config = True

    # Google OAuth API endpoints
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
    AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'

    def __init__(self, config: Dict = None):
        super().__init__(config)
        # Required config parameters
        self.client_id = self.config.get('client_id', getattr(settings, 'GOOGLE_CLIENT_ID', None))
        self.client_secret = self.config.get('client_secret', getattr(settings, 'GOOGLE_CLIENT_SECRET', None))
        self.redirect_uri = self.config.get('redirect_uri', getattr(settings, 'GOOGLE_REDIRECT_URI', None))
        # Optional config
        self.scope = self.config.get('scope', 'email profile openid')
        self.validate_config()

    def validate_config(self) -> None:
        """Ensure required configuration is present."""
        super().validate_config()
        if not self.client_id:
            raise ValueError("Google OAuth backend requires client_id")
        # client_secret and redirect_uri only needed for web OAuth flow

    def get_auth_url(self) -> str:
        """
        Get the Google OAuth authorization URL.

        Returns:
            The URL to redirect the user to for Google authentication.
        """
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Web OAuth flow requires client_id, client_secret, and redirect_uri")

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scope,
            'access_type': 'offline',
            'include_granted_scopes': 'true',
        }

        query = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    def authenticate(self, request: HttpRequest, **kwargs) -> Tuple[bool, Dict, Optional[str]]:
        """
        Authenticate a user with Google.

        This method supports multiple authentication flows:
        1. ID token verification (for mobile apps)
        2. Access token validation (for web apps with existing tokens)
        3. Authorization code exchange (for web OAuth flow)

        Args:
            request: The HTTP request
            **kwargs: May contain 'code', 'access_token', or 'id_token'

        Returns:
            Tuple of (success, user_data, error_message)
        """
        code = kwargs.get('code')
        access_token = kwargs.get('access_token') or self.extract_auth_token(request)
        id_token_str = kwargs.get('id_token')

        # Priority: ID token (mobile) > Access token > Code (web)
        if id_token_str:
            return self._authenticate_with_id_token(id_token_str)
        elif access_token:
            return self._authenticate_with_access_token(access_token)
        elif code:
            return self._authenticate_with_code(code)
        else:
            return False, {}, "No authentication credentials provided"

    def _authenticate_with_id_token(self, id_token_str: str) -> Tuple[bool, Dict, Optional[str]]:
        """
        Authenticate using Google ID token (preferred for mobile apps).

        Args:
            id_token_str: The ID token from Google Sign-In

        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            # Verify the ID token with Google
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                self.client_id
            )

            # Extract user data from the verified token
            user_data = {
                'provider_user_id': idinfo.get('sub'),
                'email': idinfo.get('email'),
                'provider_data': {
                    'name': idinfo.get('name'),
                    'given_name': idinfo.get('given_name'),
                    'family_name': idinfo.get('family_name'),
                    'picture': idinfo.get('picture'),
                    'email_verified': idinfo.get('email_verified', False),
                    'locale': idinfo.get('locale'),
                    'aud': idinfo.get('aud'),  # Client ID
                    'iss': idinfo.get('iss'),  # Issuer
                }
            }

            if not user_data['provider_user_id'] or not user_data['email']:
                return False, {}, "ID token missing required user data"

            return True, user_data, None

        except ValueError as e:
            return False, {}, f"Invalid ID token: {str(e)}"
        except Exception as e:
            return False, {}, f"ID token verification failed: {str(e)}"

    def _authenticate_with_access_token(self, access_token: str) -> Tuple[bool, Dict, Optional[str]]:
        """
        Authenticate using Google access token.

        Args:
            access_token: The access token from Google OAuth

        Returns:
            Tuple of (success, user_data, error_message)
        """
        user_info = self._get_user_info(access_token)
        if 'error' in user_info:
            return False, {}, f"Failed to get user info: {user_info.get('error_description', user_info.get('error'))}"

        # Extract user data
        user_data = {
            'provider_user_id': user_info.get('sub'),
            'email': user_info.get('email'),
            'provider_data': {
                'name': user_info.get('name'),
                'given_name': user_info.get('given_name'),
                'family_name': user_info.get('family_name'),
                'picture': user_info.get('picture'),
                'email_verified': user_info.get('email_verified', False),
                'locale': user_info.get('locale'),
            }
        }

        if not user_data['provider_user_id'] or not user_data['email']:
            return False, {}, "Could not extract required user data from Google response"

        return True, user_data, None

    def _authenticate_with_code(self, code: str) -> Tuple[bool, Dict, Optional[str]]:
        """
        Authenticate using authorization code (web OAuth flow).

        Args:
            code: The authorization code from Google OAuth

        Returns:
            Tuple of (success, user_data, error_message)
        """
        if not all([self.client_secret, self.redirect_uri]):
            return False, {}, "Authorization code flow requires client_secret and redirect_uri"

        # Exchange code for access token
        token_response = self._exchange_code_for_token(code)
        if 'error' in token_response:
            return False, {}, f"Failed to exchange code: {token_response.get('error_description', token_response.get('error'))}"

        access_token = token_response.get('access_token')
        if not access_token:
            return False, {}, "No access token in response"

        # Use access token to authenticate
        return self._authenticate_with_access_token(access_token)

    def _exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange an authorization code for an access token.

        Args:
            code: The authorization code from Google OAuth

        Returns:
            Dictionary with token information or error details
        """
        payload = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        try:
            response = requests.post(self.TOKEN_URL, data=payload)
            pprint("payload: {}, response: {}".format(payload, response.text))
            return response.json()
        except requests.RequestException as e:
            return {'error': 'request_failed', 'error_description': str(e)}

    def _get_user_info(self, access_token: str) -> Dict:
        """
        Get user info from Google with the provided access token.

        Args:
            access_token: Google OAuth access token

        Returns:
            Dictionary with user information or error details
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(self.USER_INFO_URL, headers=headers)
            return response.json()
        except requests.RequestException as e:
            return {'error': 'request_failed', 'error_description': str(e)}

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract the user ID from a Google token.
        Tries ID token verification first, then access token.

        Args:
            token: Google ID token or access token

        Returns:
            Google user ID or None if token is invalid
        """
        # Try as ID token first
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                self.client_id
            )
            return idinfo.get('sub')
        except ValueError:
            # If ID token verification fails, try as access token
            user_info = self._get_user_info(token)
            if 'sub' in user_info:
                return user_info['sub']

        return None
