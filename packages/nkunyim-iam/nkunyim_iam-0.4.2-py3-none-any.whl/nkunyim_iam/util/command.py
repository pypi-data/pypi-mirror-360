from typing import Type, Union
from rest_framework.serializers import ModelSerializer

from nkunyim_iam.util.validation import Validation, VAL



class Command(Validation):
    
    def __init__(self):
        super().__init__()
        self.queryset = None
        

    def get(self, serializer: Type[ModelSerializer]) -> Union[dict[str, VAL], None]:
        result = serializer(self.queryset, many=False)
        return result.data
