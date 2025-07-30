from typing import Union

from nkunyim_iam.models import App, Nat, User
from nkunyim_iam.serializers import AppSerializer, NatSerializer, UserSerializer
from nkunyim_iam.util.query import Query



class AppQuery(Query):
    
    def __init__(self, query_params: Union[dict, None] = None):
        super().__init__(serializer=AppSerializer, model=App)
        
        self.path = 'api/apps/'
        schema = {
            'id': 'uuid',
        }
        
        self.extract(schema=schema, query_params=query_params)


class NatQuery(Query):
    
    def __init__(self, query_params: Union[dict, None] = None):
        super().__init__(serializer=NatSerializer, model=Nat)
        
        self.path = 'api/nats/'
        schema = {
            'id': 'uuid',
            'code': 'str',
            'name': 'str',
        }
        
        self.extract(schema=schema, query_params=query_params)


class UserQuery(Query):
    
    def __init__(self, query_params: Union[dict, None] = None):
        super().__init__(serializer=UserSerializer, model=User)
        
        self.path = 'api/users/'
        schema = {
            'id': 'uuid',
            'username': 'str',
            'phone_number': 'str',
            'email_address': 'str',
            'is_active': 'bool',
        }
        
        self.extract(schema=schema, query_params=query_params)
