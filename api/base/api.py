

from django.conf import settings
from django.core.paginator import Paginator
from .utils.exceptions import CustomValidationError


def paginate_response(queryset, schema, request, page: int = 1, page_size: int = settings.DEFAULT_PAGE_SIZE):
    paginator = Paginator(queryset, page_size)
    if page > paginator.num_pages:
        raise CustomValidationError("Invalid page number")
    paginated_data = paginator.get_page(page)
    data = [schema(**item.to_dict(request)).dict() for item in paginated_data]
    return {
        "count": paginator.count,
        "page": paginated_data.number,
        "page_size": page_size,
        "last_page": paginator.num_pages,
        "data": data
    }


def paginate_list(data, schema, request, page: int = 1, page_size: int = settings.DEFAULT_PAGE_SIZE):
    paginator = Paginator(data, page_size)
    paginated_data = paginator.get_page(page)
    data = [schema(**item).dict() for item in paginated_data]

    return {
        "count": paginator.count,
        "page": page,
        "page_size": page_size,
        "last_page": paginator.num_pages,
        "data": data,
    }

