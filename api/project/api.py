from typing import Union

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from pydantic import ValidationError

# from users.api import router as users_router

api = NinjaAPI()


# api.add_router("/users/", users_router)


@api.exception_handler(ValidationError)
def validation_errors(request: HttpRequest, exc: Union[ValidationError, str]) -> HttpResponse:
    """Customize validation error"""
    if isinstance(exc, str):
        response = {"detail": exc}
    else:
        response = {"detail": exc.errors}

    return api.create_response(request, response, status=400)
