from datetime import datetime
from typing import Type, Union
from uuid import UUID

from django.conf import settings
from django.core.paginator import Paginator
from rest_framework.serializers import ModelSerializer

from nkunyim_iam.util.validation import is_uuid, VAL


class Pagination:
    def __init__(self) -> None:
        self.rows: int = 0
        self.page: int = 0
        self.params: dict[str, VAL] = {}
        self.path: str = ""

    def build(self, key: str, typ: str, val: Union[int, bool, str, float]) -> None:
        str_val = str(val)

        type_map = {
            'uuid': lambda v: UUID(v) if is_uuid(v) else None,
            'bool': lambda v: str(v).lower() in ['true', '1'],
            'str': str,
            'int': int,
            'float': float,
            'date': lambda v: datetime.strptime(v, '%Y-%m-%d %H:%M:%S').date(),
            'time': lambda v: datetime.strptime(v, '%Y-%m-%d %H:%M:%S').time(),
            'timez': lambda v: datetime.strptime(v, '%Y-%m-%d %H:%M:%S').timestamp(),
            'datetime': lambda v: datetime.strptime(v, '%Y-%m-%d %H:%M:%S'),
        }

        if typ in type_map:
            try:
                parsed_value = type_map[typ](str_val)
                if parsed_value is not None:
                    self.params[key] = parsed_value
            except Exception:
                pass  # You may want to log or raise validation errors here
        else:
            self.params[key] = val

    def extract(self, schema: Union[dict, None] = None, query_params: Union[dict, None] = None) -> None:
        query_params = query_params or {}

        self.rows = int(query_params.get('rows', 0)) or settings.REST_FRAMEWORK.get('PAGE_SIZE', 25)
        self.page = int(query_params.get('page', 0)) or 1

        if schema:
            for key, typ in schema.items():
                if key in query_params:
                    self.build(key=key, typ=typ, val=query_params[key])

    def list(self, queryset, serializer: Type[ModelSerializer]):
        paginator = Paginator(queryset, self.rows)
        page_obj = paginator.page(self.page)

        query_str = ''.join(f"&{key}={self.params[key]}" for key in self.params)

        base_url = f"{settings.APP_BASE_URL}/{self.path}"
        _next = f"{base_url}?rows={self.rows}&page={self.page + 1}{query_str}" if page_obj.has_next() else None
        _prev = f"{base_url}?rows={self.rows}&page={self.page - 1}{query_str}" if page_obj.has_previous() else None

        serialized = serializer(page_obj, many=True)
        return {
            'count': paginator.count,
            'next': _next,
            'prev': _prev,
            'data': serialized.data
        }
