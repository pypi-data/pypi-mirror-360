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
    
        if typ not in ['int', 'bool', 'str', 'uuid', 'float', 'date', 'time', 'timez', 'datetime']:
            self.params[key] = val
            
        if typ == 'uuid' and is_uuid(val=str(val)):
            self.params[key] = UUID(str(val))
    
        if typ == 'bool':
            self.params[key] = bool(val)
    
        if typ == 'str':
            self.params[key] = str(val)
            
        if typ == 'int':
            self.params[key] = int(val)
            
        if typ == 'float':
            self.params[key] = float(val)
            
        if typ == 'date':
            self.params[key] = datetime.strptime(str(val), '%Y-%m-%d %H:%M:%S').date()
            
        if typ == 'time':
            self.params[key] = datetime.strptime(str(val), '%Y-%m-%d %H:%M:%S').time()
            
        if typ == 'timez':
            self.params[key] = datetime.strptime(str(val), '%Y-%m-%d %H:%M:%S').timestamp()
            
        if typ == 'datetime':
            self.params[key] = datetime.strptime(str(val), '%Y-%m-%d %H:%M:%S')
    

    def extract(self, schema: Union[dict, None] = None, query_params: Union[dict, None] = None) -> None:
        if query_params:
            self.rows = int(query_params.get('rows', 0))
            self.page = int(query_params.get('page', 0))
            
        if self.rows == 0:
            self.rows = settings.REST_FRAMEWORK['PAGE_SIZE'] if settings.REST_FRAMEWORK and 'PAGE_SIZE' in settings.REST_FRAMEWORK else 25
            
        if self.page == 0:
            self.page = 1
            
        if schema:
            for key in list(schema.keys()):
                if query_params and key in query_params:
                    typ = schema[key]
                    self.build(key=key, typ=typ, val=query_params[key])
             
    
    def list(self, queryset, serializer: Type[ModelSerializer]):
        
        paginator = Paginator(queryset, int(self.rows))
        queryset = paginator.page(int(self.page))
        
        query_params = ""
        if self.params:
            for key in dict(self.params).keys():
                query_params += f"&{key}={self.params[key]}"
                
        _next = f"{settings.APP_BASE_URL}/{self.path}?rows={self.rows}&page={self.page + 1}{query_params}" if queryset.has_next() else None
        _prev = f"{settings.APP_BASE_URL}/{self.path}?rows={self.rows}&page={self.page - 1}{query_params}" if queryset.has_previous() else None
        
        result = serializer(queryset, many=True)
        return {
            'count': paginator.count,
            'next': _next,
            'prev': _prev,
            'data': result.data
        }
