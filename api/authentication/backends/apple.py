"""
Apple OAuth authentication backend implementation.
"""
import base64
import json
import time
from typing import Dict, Optional, Tuple

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings
from django.http import HttpRequest

from authentication.backends.base import AuthBackend
from authentication.constants import AuthBackendType
from authentication.backends.registry import register_backend


@register_backend
class AppleAuthBackend(AuthBackend):
    """
    Apple OAuth authentication backend.

    This backend handles authentication with Apple's Sign in with Apple service.
    """
    name = AuthBackendType.APPLE.value
    display_name = AuthBackendType.APPLE.label
    supports_registration = True
    requires_config = True

    # Apple API endpoints and constants
    AUTH_URL = 'https://appleid.apple.com/auth/authorize'
    TOKEN_URL = 'https://appleid.apple.com/auth/token'
    KEYS_URL = 'https://appleid.apple.com/auth/keys'

    def __init__(self, config: Dict = None):
        super().__init__(config)
        # Required config parameters
        self.client_id = self.config.get('client_id', getattr(settings, 'APPLE_CLIENT_ID', None))
        self.team_id = self.config.get('team_id', getattr(settings, 'APPLE_TEAM_ID', None))
        self.key_id = self.config.get('key_id', getattr(settings, 'APPLE_KEY_ID', None))
        self.private_key = self.config.get('private_key', getattr(settings, 'APPLE_PRIVATE_KEY', None))
        self.redirect_uri = self.config.get('redirect_uri', getattr(settings, 'APPLE_REDIRECT_URI', None))

        # Optional config
        self.scope = self.config.get('scope', 'email name')
        self.validate_config()

    def validate_config(self) -> None:
        """Ensure required configuration is present."""
        super().validate_config()
        required_fields = ['client_id', 'team_id', 'key_id', 'private_key', 'redirect_uri']
        missing = [field for field in required_fields if not getattr(self, field)]
        if missing:
            raise ValueError(f"Apple OAuth backend requires: {', '.join(missing)}")

    def get_auth_url(self) -> str:
        """
        Get the Apple OAuth authorization URL.

        Returns:
            The URL to redirect the user to for Apple authentication.
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code id_token',
            'scope': self.scope,
            'response_mode': 'form_post',
        }

        query = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    def authenticate(self, request: HttpRequest, **kwargs) -> Tuple[bool, Dict, Optional[str]]:
        """
        Authenticate a user with Apple.

        This method can authenticate in two ways:
        1. Using an authorization code
        2. Using an id_token directly

        Args:
            request: The HTTP request
            **kwargs: May contain 'code', 'id_token', or 'user' (Apple user data)

        Returns:
            Tuple of (success, user_data, error_message)
        """
        code = kwargs.get('code')
        id_token = kwargs.get('id_token') or self.extract_auth_token(request)
        user_info = kwargs.get('user', {})

        # No authentication method provided
        if not code and not id_token:
            return False, {}, "No authorization code or ID token provided"

        # If we have a code but no token, exchange code for token
        if code and not id_token:
            token_response = self._exchange_code_for_token(code)
            if 'error' in token_response:
                return False, {}, f"Failed to exchange code: {token_response.get('error_description', token_response.get('error'))}"

            id_token = token_response.get('id_token')
            if not id_token:
                return False, {}, "No ID token in response"

        # Validate and decode the ID token
        try:
            decoded_token = self._verify_apple_id_token(id_token)
        except Exception as e:
            return False, {}, f"Failed to validate Apple ID token: {str(e)}"

        # Extract user data - Apple ID token contains minimal info
        user_data = {
            'provider_user_id': decoded_token.get('sub'),  # Apple user ID
            'email': decoded_token.get('email'),
            'provider_data': {
                'email_verified': decoded_token.get('email_verified', False),
                'is_private_email': decoded_token.get('is_private_email', False),
            }
        }

        # Apple may provide additional user info on first login (name)
        if user_info and isinstance(user_info, dict):
            name_info = user_info.get('name', {})
            if name_info:
                user_data['provider_data'].update({
                    'first_name': name_info.get('firstName'),
                    'last_name': name_info.get('lastName'),
                })

        if not user_data['provider_user_id']:
            return False, {}, "Could not extract user ID from Apple ID token"

        return True, user_data, None

    def _create_client_secret(self) -> str:
        """
        Generate a client secret for Apple API.

        Returns:
            JWT token to use as client_secret
        """
        # Load the private key
        if self.private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            key = serialization.load_pem_private_key(
                self.private_key.encode(),
                password=None,
                backend=default_backend()
            )
        else:
            # If it's a path to a file
            try:
                with open(self.private_key, 'rb') as key_file:
                    key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )
            except FileNotFoundError:
                raise ValueError(f"Apple private key file not found: {self.private_key}")

        # Create the JWT payload
        now = int(time.time())
        payload = {
            'iss': self.team_id,
            'iat': now,
            'exp': now + 3600,  # 1 hour expiration
            'aud': 'https://appleid.apple.com',
            'sub': self.client_id,
        }

        # Create the headers
        headers = {
            'kid': self.key_id,
            'alg': 'ES256'
        }

        # Sign and encode the JWT
        client_secret = jwt.encode(
            payload,
            key,
            algorithm='ES256',
            headers=headers
        )

        return client_secret

    def _exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange an authorization code for tokens.

        Args:
            code: The authorization code from Apple OAuth

        Returns:
            Dictionary with token information or error details
        """
        try:
            client_secret = self._create_client_secret()
        except Exception as e:
            return {'error': 'client_secret_creation_failed', 'error_description': str(e)}

        payload = {
            'client_id': self.client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

        try:
            response = requests.post(self.TOKEN_URL, data=payload)
            return response.json()
        except requests.RequestException as e:
            return {'error': 'request_failed', 'error_description': str(e)}

    def _get_apple_public_keys(self) -> Dict:
        """
        Fetch Apple's public keys for JWT verification.

        Returns:
            Dictionary of Apple's public keys
        """
        try:
            response = requests.get(self.KEYS_URL)
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch Apple public keys: {str(e)}")

    def _verify_apple_id_token(self, id_token: str) -> Dict:
        """
        Verify and decode an Apple ID token.

        Args:
            id_token: The Apple ID token to verify

        Returns:
            Decoded token payload if valid

        Raises:
            ValueError: If token verification fails
        """
        # Get the key ID from the token header
        try:
            header = id_token.split('.')[0]
            padded_header = header + '=' * (4 - len(header) % 4)
            decoded_header = json.loads(base64.b64decode(padded_header).decode('utf-8'))
            key_id = decoded_header.get('kid')
        except Exception as e:
            raise ValueError(f"Failed to parse token header: {str(e)}")

        if not key_id:
            raise ValueError("No key ID in token header")

        # Get Apple's public keys
        keys_data = self._get_apple_public_keys()
        public_keys = {key['kid']: key for key in keys_data.get('keys', [])}

        if key_id not in public_keys:
            raise ValueError(f"Key ID {key_id} not found in Apple public keys")

        # Get the public key for verification
        key_data = public_keys[key_id]

        try:
            # Decode and verify the token
            return jwt.decode(
                id_token,
                jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data)),
                algorithms=['RS256'],
                audience=self.client_id,
                options={"verify_exp": True}
            )
        except jwt.PyJWTError as e:
            raise ValueError(f"ID token validation failed: {str(e)}")

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract the user ID from an Apple ID token.

        Args:
            token: Apple ID token

        Returns:
            Apple user ID or None if token is invalid
        """
        try:
            decoded_token = self._verify_apple_id_token(token)
            return decoded_token.get('sub')
        except Exception:
            return None
