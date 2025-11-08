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
from missions.selectors import location_details, mission_details
from souls.models import Soul, ProgressUpdate
from souls.selectors import get_soul
from users.selectors import user_details


def create_soul(data) -> Soul:

    try:
        location_id = data.get("location")
        user_id = data.get("user")
        mission_id = data.get("mission")
        if location_id is not None:
            location = location_details(location_id)
            data["location"] = location
        if user_id is not None:
            user = user_details(user_id)
            data["user"] = user
        if mission_id is not None:
            mission = mission_details(mission_id)
            data["mission"] = mission
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


def progress_update_handler(user, kwargs):
    print("SOUL ID KWARGS:", kwargs)
    print("USER ID:", user.pk)
    soul_id = kwargs.get("progress_update_in").soul_id if "progress_update_in" in kwargs else kwargs.get("soul_id")
    if not soul_id:
        return None
    soul = get_soul(soul_id)
    if not soul.user or soul.user.pk != user.pk:
        raise CustomValidationError("You can only view/write/edit/delete notes for souls assigned to you.")
    return None


def missioner_soul_operations_handler(user, kwargs):
    """
    Restriction handler for missioners updating souls.
    Ensures missioners can only update souls associated to them.
    """
    print("KWARGS", kwargs)
    soul_id = kwargs.get('soul_id')
    if not soul_id:
        raise CustomValidationError("Soul ID is required.")

    soul = get_soul(soul_id=soul_id)

    if not soul.user or soul.user.pk != user.id:
        raise CustomValidationError("You can only view/update souls assigned to you.")
