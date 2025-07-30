from decimal import Decimal
from functools import cached_property
from django.contrib.gis.geoip2 import GeoIP2
from django.http import HttpRequest


class Location:
    FALLBACK_IP = "154.160.22.132"
    PRIVATE_IP_PREFIXES = ("192.168.",)
    LOCALHOST_SUFFIXES = (".0.0.1",)

    def __init__(self, request: HttpRequest) -> None:
        self._user_ip = self._extract_ip(request)
        self._geoip = GeoIP2()

    def _extract_ip(self, request: HttpRequest) -> str:
        ip = (
            request.META.get("HTTP_X_FORWARDED_FOR")
            or request.META.get("HTTP_X_REAL_IP")
            or request.META.get("REMOTE_ADDR", "")
        ).split(",")[0].strip()

        if ip.startswith(self.PRIVATE_IP_PREFIXES) or any(ip.endswith(suffix) for suffix in self.LOCALHOST_SUFFIXES):
            return self.FALLBACK_IP
        return ip

    @cached_property
    def data(self) -> dict:
        return self._geoip.city(self._user_ip)

    @property
    def user_ip(self) -> str:
        return self._user_ip

    def _get_str(self, key: str, default=None, cast=str):
        value = self.data.get(key, default)
        return cast(value) if value is not None else None

    def _get_int(self, key: str, default=None, cast=int):
        value = self.data.get(key, default)
        return cast(value) if value is not None else None

    def _get_dec(self, key: str, default=None, cast=Decimal):
        value = self.data.get(key, default)
        return cast(value) if value is not None else None

    # Accessors
    @property
    def accuracy_radius(self): return self._get_int('accuracy_radius', 0, int)
    @property
    def city(self): return self._get_str('city')
    @property
    def continent_code(self): return self._get_str('continent_code')
    @property
    def continent_name(self): return self._get_str('continent_name')
    @property
    def country_code(self): return self._get_str('country_code')
    @property
    def country_name(self): return self._get_str('country_name')
    @property
    def is_in_eu(self): return self.data.get('is_in_european_union', False)
    @property
    def latitude(self): return self._get_dec('latitude', 0.0, Decimal)
    @property
    def longitude(self): return self._get_dec('longitude', 0.0, Decimal)
    @property
    def metro_code(self): return self._get_str('metro_code')
    @property
    def postal_code(self): return self._get_str('postal_code')
    @property
    def region_code(self): return self._get_str('region_code')
    @property
    def region_name(self): return self._get_str('region_name')
    @property
    def time_zone(self): return self._get_str('time_zone')
    @property
    def dma_code(self): return self._get_str('dma_code')
    @property
    def region(self): return self._get_str('region')
