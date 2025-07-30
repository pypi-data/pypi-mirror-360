from decimal import Decimal
from typing import Union
from uuid import UUID
from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.util.client import HttpClient



class Nation(object):
    
    def __init__(self, req: HttpRequest, code: str) -> None:
        self._data: Union[dict[str, Union[str, bool]], None] = None
        client = HttpClient(req=req, name=settings.PLACE_SERVICE)
        result = client.get(path=f"/api/nations/?code={code.upper()}")
        if result.ok:
            json = result.json()
            self._data = json['data'][0]


    @property
    def id(self) -> Union[UUID, None]:
        return UUID(str(self._data['id'])) if self._data and 'id' in self._data else None
    
    @property
    def code(self) -> Union[str, None]:
        return str(self._data['code']) if self._data and 'code' in self._data else None
    
    @property
    def name(self) -> Union[str, None]:
        return str(self._data['name']) if self._data and 'name' in self._data else None
    
    @property
    def phone(self) -> Union[str, None]:
        return str(self._data['phone']) if self._data and 'phone' in self._data else None
    
    @property
    def capital(self) -> Union[str, None]:
        return str(self._data['capital']) if self._data and 'capital' in self._data else None
    
    @property
    def languages(self) -> Union[str, None]:
        return str(self._data['languages']) if self._data and 'languages' in self._data else None
    
    @property
    def north(self) -> Union[Decimal, None]:
        return Decimal(str(self._data['north'])) if self._data and 'north' in self._data else None
    
    @property
    def south(self) -> Union[Decimal, None]:
        return Decimal(str(self._data['south'])) if self._data and 'south' in self._data else None
    
    @property
    def east(self) -> Union[Decimal, None]:
        return Decimal(str(self._data['east'])) if self._data and 'east' in self._data else None
    
    @property
    def west(self) -> Union[Decimal, None]:
        return Decimal(str(self._data['west'])) if self._data and 'west' in self._data else None
    
    @property
    def flag(self) -> Union[str, None]:
        return str(self._data['flag']) if self._data and 'flag' in self._data else None
    
    @property
    def flag_2x(self) -> Union[str, None]:
        return str(self._data['flag_2x']) if self._data and 'flag_2x' in self._data else None
    
    @property
    def flag_3x(self) -> Union[str, None]:
        return str(self._data['flag_3x']) if self._data and 'flag_3x' in self._data else None
    
    @property
    def flag_svg(self) -> Union[str, None]:
        return str(self._data['flag_svg']) if self._data and 'flag_svg' in self._data else None
    
    @property
    def is_active(self) -> Union[bool, None]:
        return bool(self._data['is_active']) if self._data and 'is_active' in self._data else None
    
    @property
    def continent_id(self) -> Union[UUID, None]:
        return UUID(str(self._data['continent'])) if self._data and 'continent' in self._data else None
    
    @property
    def currency_id(self) -> Union[UUID, None]:
        return UUID(str(self._data['currency'])) if self._data and 'currency' in self._data else None
    
    @property
    def data(self) -> Union[dict[str, Union[str, bool]], None]:
        return self._data
