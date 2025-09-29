"""
JWT authentication backend implementation.
"""
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Dict, Optional, Tuple

import jwt
import pytz
from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone

from authentication.backends.base import AuthBackend
from authentication.backends.registry import register_backend
from users.models import User


@register_backend
class JWTAuthBackend(AuthBackend):
    """
    JSON Web Token authentication backend.

    This backend handles JWT token generation, validation and user authentication.
    """
    name = 'jwt'
    display_name = 'JWT Authentication'
    supports_registration = False
    requires_config = False

    # Default JWT settings (can be overridden in settings.py)
    DEFAULT_JWT_SECRET = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
    DEFAULT_JWT_ALGORITHM = getattr(settings, 'JWT_ALGORITHM', 'HS256')
    DEFAULT_JWT_EXPIRATION = getattr(settings, 'JWT_EXPIRATION_DELTA',
                                    timedelta(days=7))

    def __init__(self, config: Dict = None):
        super().__init__(config)
        # Use settings from config or fall back to defaults
        self.jwt_secret = self.config.get('secret_key', self.DEFAULT_JWT_SECRET)
        self.algorithm = self.config.get('algorithm', self.DEFAULT_JWT_ALGORITHM)
        self.token_expiration = self.config.get('expiration_delta', self.DEFAULT_JWT_EXPIRATION)

    def generate_token(self, user: User) -> Dict:
        """
        Generate a JWT token for the given user.

        Args:
            user: The user to generate a token for.

        Returns:
            Dictionary containing the token and expiration time.
        """
        # Calculate token expiry time
        now = timezone.now()
        expiry = now + self.token_expiration

        # Create the payload
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'is_superuser': user.is_superuser,
            'exp': expiry.timestamp(),
            'iat': now.timestamp(),
        }

        # Add roles if available
        roles = list(user.roles.values_list('name', flat=True))
        if roles:
            payload['roles'] = roles

        # Generate the token
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)

        return {
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': self.token_expiration.total_seconds(),
        }

    def authenticate(self, request: HttpRequest, **kwargs) -> Tuple[bool, Dict, Optional[str]]:
        """
        Authenticate a user with a JWT token.

        For JWT backend, we expect the token to be passed in Authorization header,
        or in the 'token' kwarg.

        Args:
            request: The HTTP request.
            **kwargs: May contain 'token' if passed directly.

        Returns:
            Tuple of (success, user_data, error_message)
        """
        token = kwargs.get('token') or self.extract_auth_token(request)

        if not token:
            return False, {}, "No JWT token provided"

        try:
            # Decode and validate token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])
            nairobi_tz = pytz.timezone("Africa/Nairobi")
            # Check expiration
            if 'exp' in payload:
                # ✅ Use datetime.timezone.utc instead of timezone.utc
                exp_dt = datetime.fromtimestamp(payload['exp'], tz=dt_timezone.utc).astimezone(nairobi_tz)

                # Get current time in Nairobi
                now_nairobi = timezone.now().astimezone(nairobi_tz)

                if exp_dt < now_nairobi:
                    return False, {}, "Token has expired"

            # Return user data
            user_data = {
                'provider_user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'is_superuser': payload.get('is_superuser', False),
                'roles': payload.get('roles', []),
            }

            return True, user_data, None

        except jwt.ExpiredSignatureError:
            return False, {}, "Token has expired"
        except jwt.InvalidTokenError as e:
            return False, {}, f"Invalid token: {str(e)}"

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract the user ID from a JWT token.

        Args:
            token: JWT token string

        Returns:
            User ID from the token or None if invalid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])
            return payload.get('user_id')
        except jwt.PyJWTError:
            return None

    def decode_token(self, token: str) -> dict:
        """
        Decode a JWT token and return its payload.

        Raises jwt.PyJWTError if token is invalid or expired.
        """
        return jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])