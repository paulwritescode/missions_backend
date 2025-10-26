"""
1. Get soul by id
2. List souls with filters
3. Get progress updates by id
4. List progress updates with filters
"""
from base.utils.exceptions import CustomValidationError
from souls.models import Soul


def get_soul(soul_id: int):
    """Retrieve a soul by its ID."""

    try:
        return Soul.objects.get(id=soul_id)
    except Soul.DoesNotExist:
        raise CustomValidationError("Soul with ID {} does not exist".format(soul_id))
