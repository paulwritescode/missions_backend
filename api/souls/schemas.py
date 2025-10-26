import datetime
from typing import Optional

from ninja import Schema

from base.schemas import BaseQuery, FilterQuery, BaseOut
from souls.constants import SoulStatus
from users.constants import GenderType, AgeGroupCategory


class SoulsQuery(BaseQuery, FilterQuery):
    """Schema for querying souls with pagination."""
    is_personal: Optional[bool] = None
    mission: Optional[int] = None
    gender: Optional[GenderType] = None
    age_group: Optional[AgeGroupCategory] = None
    location: Optional[int] = None
    status: Optional[SoulStatus] = None
    search: Optional[str] = None


class SoulCreateUpdate(Schema):
    """Schema for creating or updating a soul."""
    first_name: str
    last_name: str
    phone_number: str
    gender: GenderType
    age_group: AgeGroupCategory
    location: Optional[int] = None
    status: SoulStatus
    date_added: Optional[datetime.date] = None
    mission: Optional[int] = None
    is_personal: bool = False
    user: Optional[int] = None
    description: Optional[str] = None


class SoulOut(BaseOut):
    """Schema for soul output."""
    first_name: str
    last_name: str
    phone_number: str
    gender: str
    age_group: str
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    status: str
    date_added: datetime.date
    mission_id: Optional[int] = None
    mission_title: Optional[str] = None
    is_personal: bool = False
    user_id: Optional[int] = None
    user_full_name: Optional[str] = None
    soul_full_name: str
    description: Optional[str] = None



class ProgressUpdateCreate(Schema):
    """Schema for creating a progress update."""
    soul_id: int
    content: str
    update_date: Optional[datetime.date] = None


class ProgressUpdateOut(BaseOut):
    """Schema for progress update output."""
    soul_id: int
    content: str
    update_date: datetime.date
    soul_full_name: Optional[str] = None


class ProgressUpdateQuery(BaseQuery, FilterQuery):
    """Schema for querying progress updates with pagination."""
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    search: Optional[str] = None
    soul: Optional[int] = None
