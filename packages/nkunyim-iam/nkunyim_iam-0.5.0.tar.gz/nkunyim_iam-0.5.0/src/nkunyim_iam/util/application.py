import json
from uuid import UUID
from typing import Optional, Any
from django.conf import settings
from django.dispatch import Signal
from django.http import HttpRequest

from nkunyim_iam.util.client import HttpClient


# Custom signal
application_initialized = Signal()


class Application:
    def __init__(self, req: HttpRequest) -> None:
        self._data = None
        domain = '.'.join(req.get_host().rsplit('.', 2)[-2:]).lower()

        client = HttpClient(req=req, name=settings.MARKET_SERVICE)
        response = client.get(path=f"/api/applications/?domain={domain}")

        if response.ok:
            json_data = response.json()
            self._data = json_data.get("data", [None])[0]

        # Send signal after initialization
        application_initialized.send(sender=self.__class__, instance=self)

    def _get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default) if self._data else default

    def _get_uuid(self, key: str) -> Optional[UUID]:
        value = self._get(key)
        return UUID(str(value)) if value else None

    def _get_str(self, key: str) -> Optional[str]:
        value = self._get(key)
        return str(value) if value is not None else None

    def _get_bool(self, key: str) -> Optional[bool]:
        value = self._get(key)
        return bool(value) if value is not None else None

    def _get_json(self, key: str) -> Optional[dict]:
        value = self._get(key)
        return json.loads(value) if value else None

    @property
    def id(self): return self._get_uuid('id')
    @property
    def business_id(self): return self._get_uuid('business')
    @property
    def client_id(self): return self._get_str('client_id')
    @property
    def client_secret(self): return self._get_str('client_secret')
    @property
    def response_type(self): return self._get_str('response_type')
    @property
    def grant_type(self): return self._get_str('grant_type')
    @property
    def domain(self): return self._get_str('domain')
    @property
    def scope(self): return self._get_str('scope')
    @property
    def name(self): return self._get_str('name')
    @property
    def title(self): return self._get_str('title')
    @property
    def caption(self): return self._get_str('caption')
    @property
    def description(self): return self._get_str('description')
    @property
    def keywords(self): return self._get_str('keywords')
    @property
    def image_url(self): return self._get_str('image_url')
    @property
    def logo_url(self): return self._get_str('logo_url')
    @property
    def logo_light_url(self): return self._get_str('logo_light_url')
    @property
    def logo_dark_url(self): return self._get_str('logo_dark_url')
    @property
    def icon_url(self): return self._get_str('icon_url')
    @property
    def icon_light_url(self): return self._get_str('icon_light_url')
    @property
    def icon_dark_url(self): return self._get_str('icon_dark_url')
    @property
    def colour(self): return self._get_str('colour')
    @property
    def aes_key(self): return self._get_str('aes_key')
    @property
    def rsa_public_pem(self): return self._get_str('rsa_public_pem')
    @property
    def rsa_private_pem(self): return self._get_str('rsa_private_pem')
    @property
    def rsa_passphrase(self): return self._get_str('rsa_passphrase')
    @property
    def algorithm(self): return self._get_str('algorithm')
    @property
    def claims(self): return self._get_json('claims')
    @property
    def tags(self): return self._get_str('tags')
    @property
    def is_active(self): return self._get_bool('is_active')
    @property
    def created_at(self): return self._get_str('created_at')
    @property
    def updated_at(self): return self._get_str('updated_at')
    @property
    def data(self): return self._data
