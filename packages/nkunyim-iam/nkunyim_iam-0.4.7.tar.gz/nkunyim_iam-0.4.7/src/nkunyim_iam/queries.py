from typing import Type, Union
from rest_framework.serializers import ModelSerializer

from nkunyim_iam.models import App, Nat, User
from nkunyim_iam.util.query import Query



class AppQuery(Query):
    
    def __init__(self, serializer: Type[ModelSerializer], query_params: Union[dict, None] = None):
        super().__init__(serializer=serializer, model=App)
        
        self.path = 'api/apps/'
        schema = {
            'id': 'uuid',
            'name': 'str',
            'title': 'str',
        }
        
        self.extract(schema=schema, query_params=query_params)


class NatQuery(Query):
    
    def __init__(self, serializer: Type[ModelSerializer], query_params: Union[dict, None] = None):
        super().__init__(serializer=serializer, model=Nat)
        
        self.path = 'api/nats/'
        schema = {
            'id': 'uuid',
            'code': 'str',
            'name': 'str',
        }
        
        self.extract(schema=schema, query_params=query_params)


class UserQuery(Query):
    
    def __init__(self, serializer: Type[ModelSerializer], query_params: Union[dict, None] = None):
        super().__init__(serializer=serializer, model=User)
        
        self.path = 'api/users/'
        schema = {
            'id': 'uuid',
            'username': 'str',
            'phone_number': 'str',
            'email_address': 'str',
            'is_active': 'bool',
        }
        
        self.extract(schema=schema, query_params=query_params)
