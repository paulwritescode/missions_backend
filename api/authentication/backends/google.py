"""
Google OAuth authentication backend implementation.
"""
from typing import Dict, Optional, Tuple

import requests
from django.conf import settings
from django.http import HttpRequest

from authentication.backends.base import AuthBackend
from authentication.backends.registry import register_backend


@register_backend
class GoogleAuthBackend(AuthBackend):
    """
    Google OAuth authentication backend.

    This backend handles authentication with Google's OAuth 2.0 service.
    """
    name = 'google'
    display_name = 'Google'
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

    def validate_config(self) -> None:
        """Ensure required configuration is present."""
        super().validate_config()
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Google OAuth backend requires client_id, client_secret, and redirect_uri")

    def get_auth_url(self) -> str:
        """
        Get the Google OAuth authorization URL.

        Returns:
            The URL to redirect the user to for Google authentication.
        """
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

        This method expects an authorization code or access token.
        If code is provided, it will exchange it for an access token.

        Args:
            request: The HTTP request
            **kwargs: May contain 'code' (auth code) or 'access_token'

        Returns:
            Tuple of (success, user_data, error_message)
        """
        code = kwargs.get('code')
        access_token = kwargs.get('access_token') or self.extract_auth_token(request)

        # No credentials provided
        if not code and not access_token:
            return False, {}, "No authorization code or access token provided"

        # If we have a code but no token, exchange code for token
        if code and not access_token:
            token_response = self._exchange_code_for_token(code)
            if 'error' in token_response:
                return False, {}, f"Failed to exchange code: {token_response.get('error_description', token_response.get('error'))}"

            access_token = token_response.get('access_token')
            if not access_token:
                return False, {}, "No access token in response"

        # Use token to get user info
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
        Extract the user ID from a Google access token.

        Args:
            token: Google access token

        Returns:
            Google user ID or None if token is invalid
        """
        user_info = self._get_user_info(token)
        if 'sub' in user_info:
            return user_info['sub']
        return None
