from uuid import UUID, uuid4

from nkunyim_iam.util.command import Command
from nkunyim_iam.models import App, Nat, User



class AppCommand(Command):
    
    def __init__(self, data: dict) -> None:
        super().__init__()
        
        schema = {
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
        
        self.check(schema=schema, data=data)
        
        self.id = UUID(data['id'])
        self.name = str(data['name'])
        self.title = str(data['title'])


    def save(self) -> App:
        app = App.objects.get(pk=self.id)
        if app:
            app.name = self.name
            app.title = self.title
        else:
            app = App.objects.create(
                id=self.id,
                name=self.name,
                title=self.title
            )
        
        app.save()
        
        return app


class NatCommand(Command):
    
    def __init__(self, data: dict) -> None:
        super().__init__()
        
        schema = {
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
        
        self.check(schema=schema, data=data)
        
        self.id = UUID(data['id'])
        self.code = str(data['code'])
        self.name = str(data['name'])

        
    def save(self) -> Nat:
        nat = Nat.objects.get(pk=self.id)
        if nat:
            nat.code = self.code
            nat.name = self.name
        else:
            nat = Nat.objects.create(
                id=self.id,
                code=self.code,
                name=self.name,
            )
        
        return nat


class UserCommand(Command):
    
    def __init__(self, data: dict) -> None:
        super().__init__()
        
        schema = {
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
        
        self.check(schema=schema, data=data)
        
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


    def save(self) -> User:
        user = User.objects.get(pk=self.id)

        if user:
            user.username = self.username
            user.nickname = self.nickname
            user.first_name = self.first_name
            user.last_name = self.last_name
            user.phone_number = self.phone_number
            user.email_address = self.email_address
            user.is_verified = self.is_verified
            user.is_active = self.is_active
            user.is_admin = self.is_admin
            user.is_superuser = self.is_superuser
        else:
            user = User.objects.create(
                id=self.id,
                username=self.username,
                nickname=self.nickname,
                first_name=self.first_name,
                last_name=self.last_name,
                phone_number=self.phone_number,
                email_address=self.email_address,
                is_admin=self.is_admin,
                is_superuser=self.is_superuser,
                is_verified=self.is_verified,
                is_active=self.is_active,
            )

        password = str(uuid4())
        user.set_password(password)
        
        if self.photo_url:
            user.photo_url = self.photo_url
            
        user.save()
            
        return user

