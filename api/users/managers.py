import re

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for creating users with roles and additional fields"""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password"""
        if not email:
            raise ValueError('Email is required')

        # Normalize email
        email = self.normalize_email(email)

        # Validate email format
        if not self._is_valid_email(email):
            raise ValidationError('Invalid email format')

        # Set default username if not provided
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = self._generate_username_from_email(email)

        # Set default preferred_username if not provided
        if 'preferred_username' not in extra_fields:
            extra_fields['preferred_username'] = extra_fields['username']

        # Ensure required fields have defaults
        extra_fields.setdefault('first_name', '')
        extra_fields.setdefault('last_name', '')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create a regular user"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, **extra_fields)

    @transaction.atomic
    def create_user_with_role(self, email, role_name, password=None, **extra_fields):
        """Create a user and assign a role"""
        from .models import Role

        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            raise ValidationError(f"Role '{role_name}' does not exist")

        extra_fields['role'] = role
        return self.create_user(email, password, **extra_fields)

    @transaction.atomic
    def create_oauth_user(self, email, provider, provider_user_id, **extra_fields):
        """Create user from OAuth authentication (Google/Apple)"""
        # OAuth users don't need passwords
        user = self.create_user(email, **extra_fields)

        # Create OAuth provider link
        from .models import UserAuthProvider, AuthProvider

        try:
            auth_provider = AuthProvider.objects.get(name=provider)
            UserAuthProvider.objects.create(
                user=user,
                provider=auth_provider,
                provider_user_id=provider_user_id
            )
        except AuthProvider.DoesNotExist:
            # Provider not configured, but user is still created
            pass

        return user

    def authenticate_user(self, login_identifier, password):
        """
        Authenticate user using login methods:
        - Email
        - Username
        Note: preferred_username is NOT used for authentication, only for display
        """
        from django.contrib.auth import authenticate

        # Try different authentication methods
        user = None

        # Method 1: Direct email authentication
        if self._is_valid_email(login_identifier):
            user = authenticate(username=login_identifier, password=password)

        # Method 2: Try username authentication
        if not user:
            try:
                user_by_username = self.get(username=login_identifier, is_active=True)
                user = authenticate(username=user_by_username.email, password=password)
            except self.model.DoesNotExist:
                pass

        return user

    def find_user_by_login(self, login_identifier):
        """Find user by login identifiers (email or username only)"""
        # Try email first
        if self._is_valid_email(login_identifier):
            try:
                return self.get(email=login_identifier, is_active=True)
            except self.model.DoesNotExist:
                pass

        # Try username
        try:
            return self.get(username=login_identifier, is_active=True)
        except self.model.DoesNotExist:
            pass

        return None

    def get_active_users(self):
        """Get all active users"""
        return self.filter(is_active=True)

    def get_users_by_role(self, role_name):
        """Get all users with specific role"""
        return self.filter(role__name=role_name, is_active=True)

    def get_users_with_permission(self, permission):
        """Get all users who have a specific permission"""
        return self.filter(role__permissions__contains=[permission], is_active=True)

    def update_last_login(self, user):
        """Update user's last login timestamp"""
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

    def deactivate_user(self, user_id):
        """Deactivate a user"""
        try:
            user = self.get(id=user_id)
            user.is_active= False
            user.save(update_fields=['is_active'])
            return user
        except self.model.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} does not exist")

    def activate_user(self, user_id):
        """Activate a user"""
        try:
            user = self.get(id=user_id)
            user.is_active = True
            user.save(update_fields=['is_active'])
            return user
        except self.model.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} does not exist")

    def _is_valid_email(self, email):
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def _generate_username_from_email(self, email):
        """Generate username from email"""
        base_username = email.split('@')[0]

        # Clean the username
        username = re.sub(r'[^a-zA-Z0-9_]', '_', base_username)

        # Ensure uniqueness
        counter = 1
        original_username = username

        while self.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1

        return username

    def bulk_create_users(self, user_data_list):
        """Bulk create users from a list of user data"""
        created_users = []

        with transaction.atomic():
            for user_data in user_data_list:
                try:
                    user = self.create_user(**user_data)
                    created_users.append(user)
                except Exception as e:
                    # Log error but continue with other users
                    print(f"Failed to create user {user_data.get('email', 'unknown')}: {e}")

        return created_users