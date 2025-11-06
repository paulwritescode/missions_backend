"""
1. Get soul by id
2. List souls with filters
3. Get progress updates by id
4. List progress updates with filters
"""
from enum import Enum
from typing import Optional, Dict, Any

from base.utils.exceptions import CustomValidationError
from base.utils.helpers import apply_sorting
from souls.filters import SoulFilter
from souls.models import Soul, ProgressUpdate


def get_soul(soul_id: int):
    """Retrieve a soul by its ID."""

    try:
        return Soul.objects.get(id=soul_id)
    except Soul.DoesNotExist:
        raise CustomValidationError("Soul with ID {} does not exist".format(soul_id))


def list_souls(
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None,
    is_desc: bool = True
):
    """List souls with optional filters."""
    print(sort_by, type(sort_by))
    if sort_by is None:
        sort_by = 'uploaded_at'
    if isinstance(sort_by, Enum):
        sort_by = sort_by.value
    qs = Soul.objects.all()
    qs = apply_sorting(
        qs,
        sort_by=sort_by,
        is_desc=is_desc,
        allowed_fields=['uploaded_at', 'first_name', 'phone_number', 'date_added']
    )
    if filters:
        qs = SoulFilter(filters, queryset=qs).qs
    return qs


def souls_stats(filters: Optional[Dict[str, Any]] = None):
    """Get statistics about souls with optional filters."""
    qs = Soul.objects.all()
    if filters:
        qs = SoulFilter(filters, queryset=qs).qs
    total_souls = qs.count()
    # Add more statistics as needed
    return {
        "total_souls": total_souls,
    }

def get_progress_update(id: int):
    """Retrieve a progress update by its ID."""
    try:
        return ProgressUpdate.objects.get(id=id)
    except ProgressUpdate.DoesNotExist:
        raise CustomValidationError("ProgressUpdate with ID {} does not exist".format(id))


def list_progress_updates(
    soul_id: Optional[int] = None,
    is_desc: bool = True
):
    """List progress updates with optional soul filter."""
    qs = ProgressUpdate.objects.all()
    qs = apply_sorting(
        qs,
        sort_by='update_date',
        is_desc=is_desc,
        allowed_fields=['update_date']
    )
    if soul_id is not None:
        qs = qs.filter(soul=soul_id)
    return qs
