"""
1. Create soul
2. Update soul
3. Delete soul
4. Create progress update
5. Update progress update
6. Delete progress update
"""
from django.core.exceptions import ValidationError

from base.utils.exceptions import CustomValidationError, handle_cleaning_error
from missions_backend.api.souls.models import Soul, ProgressUpdate
from souls.selectors import get_soul


def create_soul(data) -> Soul:

    try:
        soul = Soul(**data)
        soul.full_clean()
        soul.save()
    except ValidationError as e:
        error_message = handle_cleaning_error(e)
        raise CustomValidationError(error_message)
    except Exception as e:
        raise CustomValidationError("Error creating soul: {}".format(e))
    return soul


def update_soul(soul_id, data) -> Soul:
    try:
        soul = Soul.objects.get(id=soul_id)
        for key, value in data.items():
            if value is not None:
                setattr(soul, key, value)
        soul.full_clean()
        soul.save()
    except Soul.DoesNotExist:
        raise CustomValidationError(f"Soul with ID {soul_id} does not exist")
    except ValidationError as e:
        error_message = handle_cleaning_error(e)
        raise CustomValidationError(error_message)
    except Exception as e:
        raise CustomValidationError("Error updating soul: {}".format(e))
    return soul


def delete_soul(soul_id) -> Soul:
    soul = get_soul(soul_id)
    try:
        soul.delete()
        return soul
    except Exception as e:
        raise CustomValidationError("Error deleting soul: {}".format(e))


def create_progress_update(data: dict) -> ProgressUpdate:
    soul_id = data.pop("soul_id")
    soul = get_soul(soul_id)
    try:
        progress_update = ProgressUpdate(soul=soul, **data)
        progress_update.full_clean()
        progress_update.save()
    except ValidationError as e:
        error_message = handle_cleaning_error(e)
        raise CustomValidationError(error_message)
    except Exception as e:
        raise CustomValidationError("Error creating progress update: {}".format(e))
    return progress_update


def update_progress_update(progress_update_id: int, data: dict) -> ProgressUpdate:
    try:
        progress_update = ProgressUpdate.objects.get(id=progress_update_id)
        for key, value in data.items():
            if value is not None:
                setattr(progress_update, key, value)
        progress_update.full_clean()
        progress_update.save()
    except ProgressUpdate.DoesNotExist:
        raise CustomValidationError(f"Progress update with ID {progress_update_id} does not exist")
    except ValidationError as e:
        error_message = handle_cleaning_error(e)
        raise CustomValidationError(error_message)
    except Exception as e:
        raise CustomValidationError("Error updating progress update: {}".format(e))
    return progress_update


def delete_progress_update(progress_update_id: int) -> ProgressUpdate:
    try:
        progress_update = ProgressUpdate.objects.get(id=progress_update_id)
        progress_update.delete()
        return progress_update
    except ProgressUpdate.DoesNotExist:
        raise CustomValidationError(f"Progress update with ID {progress_update_id} does not exist")
    except Exception as e:
        raise CustomValidationError("Error deleting progress update: {}".format(e))