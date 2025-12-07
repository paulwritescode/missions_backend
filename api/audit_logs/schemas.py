from enum import Enum

from ninja import Schema

from base.schemas import BaseOut, BaseQuery


class AuditLogSchema(BaseOut):
    user_id: int
    action_type: str
    action_category: str
    action_description: str
    is_successful: bool
    ip_address: str | None = None
    flag_suspicious: bool


class ActionType(Enum, str):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATION = "creation"
    MODIFICATION = "modification"
    DELETION = "deletion"
    REPORTS = "reports"


class ActionCategory(Enum, str):
    AUTHENTICATION = "authentication"
    SOULS = "souls"
    LOCATIONS = "locations"
    MISSION_CATEGORIES = "mission_categories"
    MISSIONS = "missions"
    USERS = "users"
    REPORTS = "reports"


class AuditLogQueryIn(BaseQuery):
    user_id: int | None = None
    action_type: ActionType | None = None
    action_category: ActionCategory | None = None
    is_successful: bool | None = None
    flag_suspicious: bool | None = None
    ip_address: str | None = None
