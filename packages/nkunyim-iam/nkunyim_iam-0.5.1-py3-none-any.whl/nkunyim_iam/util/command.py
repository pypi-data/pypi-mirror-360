from typing import Type, Union

from rest_framework.serializers import ModelSerializer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from nkunyim_iam.util.validation import Validation



class Command(Validation):
    
    def __init__(self):
        super().__init__()
        self.queryset = None
        

    def get(self, serializer: Type[ModelSerializer]) -> Union[ReturnDict, ReturnList]:
        result = serializer(self.queryset, many=False)
        return result.data
