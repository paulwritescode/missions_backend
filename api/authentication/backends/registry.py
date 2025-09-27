"""
Authentication backend registry system.
"""
from typing import Dict, Optional, Type

from authentication.backends.base import AuthBackend
from authentication.constants import AuthBackendType, config_dict

# Global registry of authentication backends
registry: Dict[str, Type[AuthBackend]] = {}


def register_backend(backend_class: Type[AuthBackend]) -> Type[AuthBackend]:
    """
    Register an authentication backend with the system.

    This is designed to be used as a decorator:
        @register_backend
        class MyAuthBackend(AuthBackend):
            ...

    Args:
        backend_class: The backend class to register.

    Returns:
        The registered backend class (for decorator use).

    Raises:
        ValueError: If a backend with the same name is already registered.
    """
    if not backend_class.name:
        raise ValueError(f"Backend class {backend_class.__name__} must define a 'name' attribute")

    if backend_class.name in registry:
        raise ValueError(f"Authentication backend '{backend_class.name}' is already registered")

    registry[backend_class.name] = backend_class
    return backend_class


def get_backend(name: str) -> Optional[AuthBackend]:
    """
    Get an instance of an authentication backend by name.

    Args:
        name: The unique name of the backend.

    Returns:
        An instance of the requested backend, or None if not found.
    """
    config = config_dict.get(name, {})
    backend_class = registry.get(name)
    if not backend_class:
        return None
    return backend_class(config)
