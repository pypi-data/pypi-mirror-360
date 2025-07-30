from typing import Type, Union
from uuid import UUID

from django.db import models
from rest_framework.serializers import ModelSerializer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from nkunyim_iam.util.pagination import Pagination


class Query(Pagination):

    def __init__(self, model: Type[models.Model], serializer:  Type[ModelSerializer]):
        self.model = model
        self.serializer: Type[ModelSerializer] = serializer
        super().__init__()
 

    def one(self, pk: UUID) -> Union[ReturnDict, ReturnList]:
        queryset = self.model.objects.get(pk=pk)
        result = self.serializer(queryset, many=False)
        return result.data
    

    def first(self) -> Union[ReturnDict, ReturnList, None]:
        if not self.params:
            return None
        
        queryset = self.model.objects.filter(**self.params).first()
        result = self.serializer(queryset, many=False)
        return result.data


    def many(self) -> dict:
        if self.params:
            queryset = self.model.objects.filter(**self.params)
        else:
            queryset = self.model.objects.all()

        return self.list(queryset=queryset, serializer=self.serializer)


    def all(self) -> dict:
        queryset = self.model.objects.all()
        return self.list(queryset=queryset, serializer=self.serializer)

