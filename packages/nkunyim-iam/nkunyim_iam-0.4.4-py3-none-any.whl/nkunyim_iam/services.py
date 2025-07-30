import json
import os
from typing import Union

from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.models import User
from nkunyim_iam.commands import AuthCommand
from nkunyim_iam.util.logging import GenLogCommand, Logging, LOG_LEVEL_ERROR


class AuthService:
    
    def login(self, req: HttpRequest, data: dict) -> Union[User, None]:
        self.req = req
        
        try:
            command = AuthCommand(data=data)
            
            if not command.is_valid:
                self.log(
                    msg=f"Login failed. Invalid data: {json.dumps(command.errors)}"
                )
                return None

            command.save_app()
            command.save_nation()
            user = command.save_user()
            
            return user
        except Exception as ex:
            self.log(msg=f"Login failed. Exception: {str(ex)}")
            return None


    def log(self, msg: str, level: str = LOG_LEVEL_ERROR, context: dict = {}) -> None:
        context['file'] = os.path.basename(__file__)
        data = {
            'label': f"{settings.NKUNYIM_SERVICE}_SERVICE_AUTHENTICATION",
            'level': level,
            'message': msg,
            'context': context
        }
        command = GenLogCommand(data=data)
        if command.is_valid:
            logging = Logging(req=self.req)
            logging.gen(command=command)

