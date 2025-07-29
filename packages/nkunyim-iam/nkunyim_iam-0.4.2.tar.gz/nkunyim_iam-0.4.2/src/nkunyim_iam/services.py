from typing import Union

from nkunyim_iam.models import User
from nkunyim_iam.commands import UserCommand


class UserService:

    def login(self, data: dict) -> Union[User, None]:
        command = UserCommand(data=data)
        
        if not command.is_valid:
            raise ValueError("Invalid data provided for user login.")
        
        user_data = User.objects.get(pk=command.id)

        if not user_data:
            user_data = command.create()
        else:
            user_data = command.update(pk=command.id)
            
        return user_data
