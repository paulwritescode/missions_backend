import datetime
from enum import Enum

from ninja import Schema
from pydantic import Field

from base.schemas import BaseQuery, FilterQuery, BaseOut


class MissionStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class GenderChoices(str, Enum):
    MALE = "male"
    FEMALE = "female"


class LocationsFilterSchema(BaseQuery):
    parent_location_id: int | None = None
    category: str | None = None
    search: str | None = None


class MissionsCategoryFilterSchema(BaseQuery):
    search: str | None = None


class MissionsFilterSchema(BaseQuery):
    category_id: int | None = None
    location_id: int | None = None
    is_individual: bool | None = None
    status: MissionStatus | None = None
    start_date_before: str | None = None
    start_date_after: str | None = None
    end_date_before: str | None = None
    end_date_after: str | None = None
    search: str | None = None


class ReportSortByEnum(str, Enum):
    CREATED_AT = "created_at"
    TITLE = "title"


class ReportsFilterSchema(BaseQuery, FilterQuery):
    mission_id: int | None = None
    created_by_id: int | None = None
    search: str | None = None
    is_desc: bool | None = True
    sort_by: ReportSortByEnum | None = None


class MissionJIASortByEnum(str, Enum):
    CREATED_AT = "created_at"
    FULL_NAME = "full_name"
    PHONE_NUMBER = "phone_number"
    TRAVELLING_FROM = "travelling_from"


class MissionJIAFilterSchema(BaseQuery, FilterQuery):
    user_id: int | None = None
    need_facilitation: bool | None = None
    gender: GenderChoices | None = None
    sort_by: MissionJIASortByEnum | None = None
    is_desc: bool | None = True


class MissionGalleryFilterSchema(BaseQuery, FilterQuery):
    mission_id: int | None = None
    uploaded_by_id: int | None = None


class LocationCreateSchema(Schema):
    name: str
    category: str
    description: str | None = ""
    parent_location_id: int | None = None


class LocationUpdateSchema(Schema):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    parent_location_id: int | None = None


class LocationOutSchema(BaseOut):
    name: str
    category: str
    description: str
    parent_location_id: int | None = None
    parent_location_name: str | None = None


class MissionCategoryCreateSchema(Schema):
    name: str
    description: str | None = None


class MissionCategoryFilterSchema(BaseQuery):
    search: str | None = None


class MissionCategoryUpdateSchema(Schema):
    name: str | None = None
    description: str | None = None


class MissionCategoryOutSchema(BaseOut):
    name: str
    description: str


class MissionCreateSchema(Schema):
    title: str
    description: str
    category_id: int
    location_id: int | None = None
    start_date: datetime.date
    end_date: datetime.date
    partnering_organization: list[str] | None = []
    is_individual: bool | None = False


class MissionUpdateSchema(Schema):
    title: str | None = None
    description: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    location_id: int | None = None
    location_name: str | None = None
    created_by_id: int | None = None
    created_by_name: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: MissionStatus | None = None
    partnering_organization: list[str] | None = None
    is_individual: bool | None = None


class MissionFilterSchema(BaseQuery):
    category_id: int | None = None
    location_id: int | None = None
    is_individual: bool | None = None
    status: MissionStatus | None = None
    start_date_before: str | None = None
    start_date_after: str | None = None
    end_date_before: str | None = None
    end_date_after: str | None = None
    search: str | None = None


class MissionOutSchema(BaseOut):
    title: str
    description: str
    category_id: int | None = None
    category_name: str | None = None
    location_id: int | None = None
    location_name: str | None = None
    start_date: str
    end_date: str
    status: MissionStatus
    partnering_organization: list[str]
    is_individual: bool
    created_by_id: int | None = None
    created_by_name: str | None = None


class AttendanceDay(Schema):
    day: int
    day_date: datetime.date | None = None
    check_in_time: datetime.time | None = None


class AttendanceDayOut(Schema):
    day: int
    day_date: str | None = None
    check_in_time: str | None = None


class MissionJIACreateSchema(Schema):
    mission_id: int
    user_id: int | None = ""
    full_name: str | None = ""
    phone_number: str | None = ""
    travelling_from: str
    days_of_attendance: list[AttendanceDay]
    diet_advisory: str | None = ""
    need_facilitation: bool | None = False
    gender: GenderChoices


class MissionJIAUpdateSchema(Schema):
    mission_id: int | None = None
    user_id: int | None = None
    full_name: str | None = None
    phone_number: str | None = None
    travelling_from: str | None = None
    days_of_attendance: list[AttendanceDay] | None = None
    diet_advisory: str | None = None
    need_facilitation: bool | None


class BulkUpdateMissionJIASchema(Schema):
    participant_ids: list[int]
    need_facilitation: bool | None = None


class MissionJIAOutSchema(BaseOut):
    mission_id: int | None = None
    mission_title: str | None = None
    user_id: int | None = None
    full_name: str
    phone_number: str
    travelling_from: str
    days_of_attendance: list[AttendanceDayOut]
    diet_advisory: str | None = None
    need_facilitation: bool
    gender: str


class ReportCreateSchema(Schema):
    mission_id: int
    title: str
    content: str
    created_by_id: int
    report_file: str | None = None


class ReportUpdateSchema(Schema):
    mission_id: int | None = None
    title: str | None = None
    content: str | None = None
    report_file: str | None = None


class ReportOutSchema(BaseOut):
    mission_id: int | None = None
    mission_title: str | None = None
    title: str
    content: str
    report_file: str | None = None
    created_by_id: int | None = None
    created_by_name: str | None = None


class MissionGalleryCreateSchema(Schema):
    mission_id: int = Field(..., description="Mission ID")
    uploaded_by_id: int = Field(..., description="User ID uploading the images")
    images_data: str = Field(
        ...,
        description="JSON-encoded array of GalleryImageMetadata objects"
    )


class MissionGalleryDeleteSchema(Schema):
    mission_id: int
    image_ids: list[int]


class MissionGalleryOutSchema(BaseOut):
    mission_id: int | None = None
    title: str | None = None
    description: str | None = None
    image: str
    uploaded_by_id: int | None = None
    uploaded_by_name: str | None = None