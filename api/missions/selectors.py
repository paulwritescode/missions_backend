from typing import Optional, Dict, Any

from django.db import models

from base.utils.exceptions import CustomValidationError
from base.utils.helpers import apply_sorting
from missions.filters import LocationFilter, MissionFilter, MissionJIAFilter, ReportsFilter, MissionGalleryFilter
from missions.models import MissionCategory, Location, Mission, MissionJIAParticipant, Report, MissionGallery


def location_details(location_id: int) -> Location:
    """
    Get details of a location by ID.

    Args:
        location_id: ID of the location.

    Returns:
        Location instance or None if not found.
    """
    try:
        return Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        raise CustomValidationError("Location with the given ID does not exist.")


def locations_list(filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
    """
    List locations with optional filters.

    Args:
        filters: Optional dictionary of filters.

    Returns:
        QuerySet of Location instances.
    """
    qs = Location.objects.all().select_related('parent_location').order_by('name')
    return LocationFilter(filters, qs).qs if filters else qs


def mission_category_details(category_id: int) -> Optional[MissionCategory]:
    """
    Get details of a mission category by ID.

    Args:
        category_id: ID of the category.

    Returns:
        MissionCategory instance or None if not found.
    """
    try:
        return MissionCategory.objects.get(id=category_id)
    except MissionCategory.DoesNotExist:
        raise CustomValidationError("MissionCategory with the given ID does not exist.")


def mission_categories_list(search: Optional[str] = None) -> models.QuerySet:
    """
    List mission categories with optional filters.

    Args:
        search: Optional dictionary.

    Returns:
        QuerySet of MissionCategory instances.
    """
    qs = MissionCategory.objects.all().order_by('name')
    if search:
        qs.filter(name__icontains=search)
    return qs


def mission_details(mission_id: int) -> Mission:
    """
    Get details of a mission by ID.

    Args:
        mission_id: ID of the mission.

    Returns:
        Mission instance or None if not found.
    """
    from missions.models import Mission

    try:
        return Mission.objects.get(id=mission_id)
    except Mission.DoesNotExist:
        raise CustomValidationError("Mission with the given ID does not exist.")


def missions_list(filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
    """
    List missions with optional filters.

    Args:
        filters: Optional dictionary of filters.

    Returns:
        QuerySet of Mission instances.
    """
    qs = Mission.objects.all().select_related('category', 'location').order_by('-start_date')
    if filters:
        if 'status' in filters and filters['status'] is not None:
            filters['status'] = filters['status'].value

    status_value = filters.get('status', None)
    print("Mission Status Filters:", )
    print("Mission Filters:", filters)
    print(status_value, type(status_value))
    return MissionFilter(filters, qs).qs if filters else qs


def mission_jia_participant_details(participant_id: int) -> MissionJIAParticipant:
    """
    Get details of a mission JIA participant by ID.

    Args:
        participant_id: ID of the participant.

    Returns:
        MissionJIAParticipant instance or None if not found.
    """
    from missions.models import MissionJIAParticipant

    try:
        return MissionJIAParticipant.objects.get(id=participant_id)
    except MissionJIAParticipant.DoesNotExist:
        raise CustomValidationError("MissionJIAParticipant with the given ID does not exist.")


def mission_jia_participants_list(
    mission_id: int,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: str = 'created_at',
    is_desc: bool = True
) -> models.QuerySet:
    """
    List mission JIA participants with optional filters.

    Args:
        mission_id: ID of the mission to filter by.
        filters: Optional dictionary of filters.
        sort_by: Optional field to sort by. Defaults to 'created_at'.
        is_desc: Optional boolean to indicate descending order. Defaults to True.

    Returns:
        QuerySet of MissionJIAParticipant instances.
    """
    qs = MissionJIAParticipant.objects.filter(mission__id=mission_id).select_related('mission', 'user')
    qs = apply_sorting(
        qs,
        sort_by=sort_by,
        is_desc=is_desc,
        allowed_fields=['created_at', 'full_name', 'phone_number', 'travelling_from']
    )
    print("JIA Filters:", filters)

    if filters:
        # Convert enum to its string value
        if 'gender' in filters and filters['gender'] is not None:
            filters['gender'] = filters['gender'].value

    return MissionJIAFilter(filters, qs).qs if filters else qs


def report_details(report_id: int) -> Report:
    """
    Get details of a report by ID.

    Args:
        report_id: ID of the report.

    Returns:
        Report instance or None if not found.
    """
    try:
        return Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        raise CustomValidationError("Report with the given ID does not exist.")


def reports_list(
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = 'created_at',
        is_desc: bool = True
) -> models.QuerySet:
    """
    List reports with optional filters.

    Args:
        filters: Optional dictionary of filters.
        sort_by: Optional field to sort by. Defaults to 'created_at'.
        is_desc: Optional boolean to indicate descending order. Defaults to True.

    Returns:
        QuerySet of Report instances.
    """
    qs = Report.objects.all().select_related('mission', 'created_by')
    qs = apply_sorting(
        qs,
        sort_by=sort_by,
        is_desc=is_desc,
        allowed_fields=['created_at', 'title']
    )
    return ReportsFilter(filters, qs).qs if filters else qs


def gallery_image_details(image_id: int) -> MissionGallery:
    """
    Get details of a gallery image by ID.

    Args:
        image_id: ID of the gallery image.

    Returns:
        MissionGallery instance or None if not found.
    """
    try:
        return MissionGallery.objects.get(id=image_id)
    except MissionGallery.DoesNotExist:
        raise CustomValidationError("MissionGallery with the given ID does not exist.")


def gallery_images_list(
    filters: Optional[Dict[str, Any]] = None,
    sort_by: str = 'created_at',
    is_desc: bool = True
) -> models.QuerySet:
    """
    List gallery images with optional mission filter.

    Args:
        mission_id: Optional ID of the mission to filter by.
        sort_by: Optional field to sort by. Defaults to 'created_at'.
        is_desc: Optional boolean to indicate descending order. Defaults to True.

    Returns:
        QuerySet of MissionGallery instances.
    """
    qs = MissionGallery.objects.all().select_related('mission', 'uploaded_by')
    qs = apply_sorting(
        qs,
        sort_by=sort_by,
        is_desc=is_desc,
        allowed_fields=['created_at', 'title']
    )
    return MissionGalleryFilter(filters, qs).qs if filters else qs
