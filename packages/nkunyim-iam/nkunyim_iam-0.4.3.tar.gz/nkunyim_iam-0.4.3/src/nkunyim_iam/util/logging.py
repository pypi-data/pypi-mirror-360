from django.conf import settings
from django.http import HttpRequest
from nkunyim_iam.util.client import HttpClient
from nkunyim_iam.util.command import Command


LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"


class GenLogCommand(Command):
    
    def __init__(self, data: dict):
        super().__init__()
        
        schema = {
            'label': {
                'typ': 'str',
            },
            'level': {
                'typ': 'str',
            },
            'message': {
                'typ': 'str',
            },
        }
        
        self.check(schema=schema, data=data)
        
        self.label = str(data['label'])
        self.level = str(data['level']) if 'level' in data else LOG_LEVEL_DEBUG
        self.message = str(data['message'])
        self.context = dict(data['context']) if 'context' in data else None


class SysLogCommand(Command):
    
    def __init__(self, data: dict):
        super().__init__()

        schema = {
            'label': {
                'typ': 'str',
            },
            'level': {
                'typ': 'str',
            },
            'message': {
                'typ': 'str',
            },
        }
        
        self.check(schema=schema, data=data)
        
        self.label = str(data['label'])
        self.level = str(data['level']) if 'level' in data else LOG_LEVEL_DEBUG
        self.message = str(data['message'])
        self.context = dict(data['context']) if 'context' in data else None


class ApiLogCommand(Command):
    
    def __init__(self, data: dict):
        super().__init__()

        schema = {
            'label': {
                'typ': 'str',
            },
            'service': {
                'typ': 'str',
            },
            'path': {
                'typ': 'str',
            },
            'method': {
                'typ': 'str',
            },
            'status': {
                'typ': 'int',
            },
            'request': {
                'typ': 'dict',
            },
            'response': {
                'typ': 'dict',
            },
        }
        
        self.check(schema=schema, data=data)
        
        self.label = str(data['label'])
        self.service = str(data['service'])
        self.path = str(data['path'])
        self.method = str(data['method'])
        self.status = int(data['status'])
        self.request = dict(data['request'])
        self.response = dict(data['response'])
        

class IamLogCommand(Command):
    
    def __init__(self, data: dict):
        super().__init__()
        
        schema = {
            'label': {
                'typ': 'str',
            },
            'user_ip': {
                'typ': 'str',
            },
            'accuracy_radius': {
                'typ': 'int',
            },
            'lattitude': {
                'typ': 'str',
            },
            'longitude': {
                'typ': 'str',
            },
            'time_zone': {
                'typ': 'str',
            },
            'browser': {
                'typ': 'str',
            },
            'os': {
                'typ': 'str',
            },
            'action': {
                'typ': 'str',
            },
            'message': {
                'typ': 'str',
            },
        }
        
        self.check(schema=schema, data=data)
        
        self.label = str(data['label'])
        self.user_ip = str(data['user_ip'])
        self.accuracy_radius = int(data['accuracy_radius'])
        self.city = str(data['city'])
        self.latitude = str(data['latitude'])
        self.longitude = str(data['label'])
        self.time_zone = str(data['time_zone'])
        self.browser = str(data['browser'])
        self.os = str(data['os'])
        self.action = str(data['action'])
        self.message = str(data['message'])
        self.context = dict(data['context']) if 'context' in data else None

    
class Logging:
    
    def __init__(self, req: HttpRequest):
        super().__init__()
        self.req = req
        self.path = ""
        self.data = {}
        
    def create(self) -> None:
        client = HttpClient(req=self.req, name=settings.LOGGING_SERVICE)
        client.post(path=self.path, data=self.data)
        
        
    def gen(self, command: GenLogCommand) -> None:
        if not command.is_valid:
            return
        
        self.path = "/api/gen_logs/"
        self.data = {
            'label': command.label,
            'level': command.level,
            'message': command.message,
            'context': command.context
        }
        self.create()
        
        
    def sys(self, command: SysLogCommand) -> None:
        if not command.is_valid:
            return
        
        self.path = "/api/sys_logs/"
        self.data = {
            'label': command.label,
            'level': command.level,
            'message': command.message,
            'context': command.context
        }
        self.create()
        
        
    def api(self, command: ApiLogCommand) -> None:
        if not command.is_valid:
            return
        
        self.path = "/api/api_logs/"
        self.data = {
            'label': command.label,
            'service': command.service,
            'path': command.path,
            'method': command.method,
            'status': command.status,
            'request': command.request,
            'response': command.response,
        }
        self.create()
        
        
    def iam(self, command: IamLogCommand) -> None:
        if not command.is_valid:
            return
        
        self.path = "/api/iam_logs/"
        self.data = {
            'label': command.label,
            'user_ip': command.user_ip,
            'accuracy_radius': command.accuracy_radius,
            'city': command.city,
            'latitude': command.latitude,
            'longitude': command.longitude,
            'time_zone': command.time_zone,
            'browser': command.browser,
            'os': command.os,
            'action': command.action,
            'message': command.message,
            'context': command.context
        }
        self.create()
        
    