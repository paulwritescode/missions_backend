from decimal import Decimal
from typing import Union

from missions_backend.api.base.utils.exceptions import CustomValidationError


def commas(value: Union[Decimal, int, float]) -> str:
    return "{:,.2f}".format(value)


def format_phone_number(phone_number):
    phone_number = str(phone_number)
    if len(phone_number) < 9:
        raise CustomValidationError("Invalid Phone Number")
    phone = phone_number[-9:]
    return "+254{}".format(phone)
