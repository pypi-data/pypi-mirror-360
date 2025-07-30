from uuid import UUID, uuid4

from nkunyim_iam.util.command import Command
from nkunyim_iam.models import App, Nation, User



class AppCommand:
    
    def __init__(self, data: dict) -> None:
        self.id = UUID(data['id'])
        self.name = str(data['name'])
        self.title = str(data['title'])


class NationCommand:
    
    def __init__(self, data: dict) -> None:
        self.id = UUID(data['id'])
        self.code = str(data['code'])
        self.name = str(data['name'])


class UserCommand:
    
    def __init__(self, data: dict):
        self.id = UUID(data['id'])
        self.username = str(data['username'])
        self.nickname = str(data['nickname'])
        self.first_name = str(data['first_name'])
        self.last_name = str(data['last_name'])
        self.phone_number = str(data['phone_number'])
        self.email_address = str(data['email_address'])
        self.photo_url = str(data['photo_url']) if 'photo_url' in data else None
        self.is_admin = bool(data['is_admin']) if 'is_admin' in data else False
        self.is_superuser = bool(data['is_superuser']) if 'is_superuser' in data else False
        self.is_verified = bool(data['is_verified']) if 'is_verified' in data else False
        self.is_active = bool(data['is_active']) if 'is_active' in data else True



class AuthCommand(Command):
    
    def __init__(self, data: dict):
        super().__init__()
        
        schema = {
            'app': {
                'typ': 'dict',
                'prop': {
                    'id': {
                        'typ': 'uuid',
                    },
                    'name': {
                        'typ': 'str',
                    },
                    'title': {
                        'typ': 'str',
                    },
                    
                }
            },
            'nation': {
                'typ': 'dict',
                'prop': {
                    'id': {
                        'typ': 'uuid',
                    },
                    'code': {
                        'typ': 'str',
                    },
                    'name': {
                        'typ': 'str',
                    },
                }
            },
            'user': {
                'typ': 'dict',
                'prop': {
                    'id': {
                        'typ': 'uuid',
                    },
                    'username': {
                        'typ': 'str',
                    },
                    'nickname': {
                        'typ': 'str',
                    },
                    'first_name': {
                        'typ': 'str',
                    },
                    'last_name': {
                        'typ': 'str',
                    },
                    'phone_number': {
                        'typ': 'str',
                    },
                    'email_address': {
                        'typ': 'str',
                    }
                }
            }
        }

        
        self.check(schema=schema, data=data)
        
        self.app = AppCommand(data=data['app'])
        self.nation = NationCommand(data=data['nation'])
        self.user = UserCommand(data=data['user'])
        
        
    def save_app(self) -> App:
        if not self.is_valid:
            raise ValueError("Invalid data provided for app creation.")
        
        app = App.objects.get(pk=self.app.id)
        if app:
            app.name = self.app.name
            app.title = self.app.title
        else:
            app = App.objects.create(
                id=self.app.id,
                name=self.app.name,
                title=self.app.title
            )
        
        app.save()
        
        return app

        
        
    def save_nation(self) -> Nation:
        if not self.is_valid:
            raise ValueError("Invalid data provided for nation creation.")
        
        nation = Nation.objects.get(pk=self.nation.id)
        if nation:
            nation.code = self.nation.code
            nation.name = self.nation.name
        else:
            nation = Nation.objects.create(
                id=self.nation.id,
                code=self.nation.code,
                name=self.nation.name,
            )
        
        return nation
    
        
    def save_user(self) -> User:
        if not self.is_valid:
            raise ValueError("Invalid data provided for user creation.")
        
        user = User.objects.get(pk=self.user.id)

        if user:
            user.username = self.user.username
            user.nickname = self.user.nickname
            user.first_name = self.user.first_name
            user.last_name = self.user.last_name
            user.phone_number = self.user.phone_number
            user.email_address = self.user.email_address
            user.is_verified = self.user.is_verified
            user.is_active = self.user.is_active
            user.is_admin = self.user.is_admin
            user.is_superuser = self.user.is_superuser
        else:
            user = User.objects.create(
                id=self.user.id,
                username=self.user.username,
                nickname=self.user.nickname,
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                phone_number=self.user.phone_number,
                email_address=self.user.email_address,
                is_admin=self.user.is_admin,
                is_superuser=self.user.is_superuser,
                is_verified=self.user.is_verified,
                is_active=self.user.is_active,
            )

        password = str(uuid4())
        user.set_password(password)
        
        if self.user.photo_url:
            user.photo_url = self.user.photo_url
            
        user.save()
            
        return user

