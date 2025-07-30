import base64
import binascii
import json
from typing import Optional, Tuple

from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from nkunyim_iam.commands import AppCommand, NatCommand
from nkunyim_iam.models import App, Nat
from nkunyim_iam.util.encryption import Encryption


class XANAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        self.process_request(request)
        return self.get_response(request)

    def get_app_nat(self, request: HttpRequest) -> Optional[Tuple[App, Nat]]:
        header = request.META.get('HTTP_XAN_AUTHORIZATION')
        if not header:
            return None

        try:
            # Strip prefix/suffix or encoding markers
            cipher_token = header[2:-1]
            cipher_text = base64.b64decode(cipher_token)

            # Decrypt token
            plain_text = Encryption().rsa_decrypt(cipher_text)
            app_nat_data = json.loads(plain_text)

            # Validate expected structure
            if 'app' not in app_nat_data or 'nat' not in app_nat_data:
                return None

            app_cmd = AppCommand(data=app_nat_data['app'])
            nat_cmd = NatCommand(data=app_nat_data['nat'])

            if not app_cmd.is_valid or not nat_cmd.is_valid:
                return None

            app = app_cmd.save()
            nat = nat_cmd.save()

            return app, nat

        except (ValueError, KeyError, json.JSONDecodeError, binascii.Error):
            return None

    def process_request(self, request: HttpRequest):
        result = self.get_app_nat(request)
        if result:
            app, nat = result
            request.app = SimpleLazyObject(lambda: app) # type: ignore
            request.nat = SimpleLazyObject(lambda: nat) # type: ignore
        else:
            request.app = None # type: ignore
            request.nat = None # type: ignore
