from datetime import datetime
from typing import Optional

from django.conf import settings
from ninja import Schema
from pydantic import conint, field_validator


class DetailOut(Schema):
    detail: str


class BaseOut(Schema):
    id: int
    created_at: str
    updated_at: str


class BaseQuery(Schema):
    page: conint(gt=0) = 1  # type: ignore
    page_size: conint(gt=0, le=1000) = settings.DEFAULT_PAGE_SIZE  # type: ignore


class FilterQuery(Schema):
    end_date: Optional[str] = None
    start_date: Optional[str] = None

    @field_validator("end_date", "start_date")
    def validate_datetime(cls, value, field):
        if value is not None:
            try:
                parsed_datetime = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format: {value}, expected YYYY-MM-DD")
            if parsed_datetime < datetime.min or parsed_datetime > datetime.max:
                raise ValueError(f"Datetime out of range for {field.name}: {value}")
        return value
