import base64
import json
from typing import Union

from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from nkunyim_iam.commands import AppCommand, NatCommand
from nkunyim_iam.models import App, Nat
from nkunyim_iam.util.encryption import Encryption



class XANAuthenticationMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.


    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        self.process_request(request)
        
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
    
    
    def get_app_nat(self, req: HttpRequest) -> Union[tuple[App, Nat], None]:
        header_xan = req.META.get('HTTP_XAN_AUTHORIZATION', None)
        if not header_xan:
            return None
    
        cipher_token = header_xan[2:-1] # Cater for bytes str concatenation issue
    
        # Get Userinfo
        encryption = Encryption()
        cipher_text = base64.b64decode(cipher_token)
        
        plain_text = encryption.rsa_decrypt(cipher_text=cipher_text)
        
        app_nat = json.loads(plain_text)
        if not bool('app' in app_nat and 'nat' in app_nat):
            return None
        
        app_command = AppCommand(data=app_nat['app'])
        if not app_command.is_valid:
            return None
            
        nat_command = NatCommand(data=app_nat['nat'])
        if not nat_command.is_valid:
            return None
        
        app = app_command.save()
        nat = nat_command.save()
        return app, nat
        
        
    def process_request(self, request):
        app, nat = None, None
        
        app_nat = self.get_app_nat(request)
        if app_nat:
            _app, _nat = app_nat
            app = SimpleLazyObject(lambda: _app)
            nat = SimpleLazyObject(lambda: _nat)
            
        request.app = app
        request.nat = nat
        