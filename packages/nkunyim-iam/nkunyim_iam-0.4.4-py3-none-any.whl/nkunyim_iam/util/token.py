# from datetime import datetime, timedelta, timezone
# import hashlib
# import logging
# import os
# import random
# import string
# from typing import Union
# from uuid import UUID

# import jwt
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.backends import default_backend

    
# from nkunyim_iam.util.command import Command
# from nkunyim_iam.util.encryption import Encryption


# logger = logging.getLogger(__name__)


# ALGO_HS256 = 'HS256'
# ALGO_RS256 = 'RS256'
# ALGO_PS256 = 'PS256'
# ALGO_EdDSA = 'EdDSA'
# ALGO_ES256 = 'ES256'

# GRANT_TYPE_CODE = 'code'
# GRANT_TYPE_ACCESS_TOKEN = 'access_token'
# GRANT_TYPE_REFRESH_TOKEN = 'refresh_token'


# class TokenApp:
    
#     def __init__(self, data: dict) -> None:
    
#         self.id = UUID(data['id'])
#         self.name = str(data['name'])
#         self.client_id = str(data['client_id'])
#         self.domain = str(data['domain'])
#         self.scope = str(data['scope']) if 'scope' in data else 'openid profile email phone'


# class TokenAud:
    
#     def __init__(self, data: dict) -> None:
    
#         self.id = UUID(data['id'])
#         self.name = str(data['name'])
#         self.type = str(data['type'])
#         self.roles = list(data['roles'])
#         self.claims = list(data['claims'])


# class TokenJwt:
    
#     def __init__(self, data: dict) -> None:
#         logger.info('TokenJwt "__init__" called')
    
#         self.id = UUID(data['id'])
#         self.aes_key = str(data['aes_key'])
#         self.rsa_private_pem = bytes(data['rsa_private_pem'])
#         self.rsa_key_phrase = bytes(data['rsa_key_phrase'])
#         self.algorithm = str(data['algorithm']) if 'algorithm' in data else 'HS256'
#         self.access_token_lifetime = int(data['access_token_lifetime']) if 'access_token_lifetime' in data else 5 # [minutes]
#         self.refresh_token_lifetime = int(data['refresh_token_lifetime']) if 'refresh_token_lifetime' in data else 24 # [hours]
#         self.rotate_refresh_token = bool(data['rotate_refresh_token']) if 'rotate_refresh_token' in data else False
#         self.header_kid = str(data['header_kid'])
#         self.grant_type = data['grant_type']


# class TokenUser:
    
#     def __init__(self, data: dict) -> None:
#         self.id = UUID(data['id'])
#         self.username = str(data['username'])
#         self.nickname = data['nickname']
#         self.first_name = data['first_name']
#         self.last_name = data['last_name']
#         self.email_address = data['email_address']
#         self.phone_number = data['phone_number']
#         self.gender = data['gender']
#         self.middle_name = data['middle_name'] if 'middle_name' in data else None
#         self.email_verified = bool(data['email_verified']) if 'email_verified' in data else False
#         self.phone_verified = bool(data['phone_verified']) if 'phone_verified' in data else False
#         self.birth_date = data['birth_date'] if 'birth_date' in data else None
#         self.photo_url = data['photo_url'] if 'photo_url' in data else None
#         self.photo_verified = bool(data['photo_verified']) if 'photo_verified' in data else False
#         self.profile = data['profile'] if 'profile' in data else None


# class BaseToken(Command):
    
#     def random_upper_str(self, n: int = 10) -> str:
#         return ''.join(random.choice(string.ascii_uppercase) for _ in range(n))

#     def random_lower_str(self, n: int = 10) -> str:
#         return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))

#     def random_upper_code(self, n: int = 10) -> str:
#         return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
    
#     def random_lower_code(self, n: int = 10) -> str:
#         return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))
    
#     def random_hash(self) -> str:
#         return hashlib.sha256(os.urandom(1024)).hexdigest()

#     def random_int(self, n: int) -> str:
#         ri = random.randint(0, 10 ** n - 1)
#         return str(ri)

#     def make_aes_key(self) -> str:
#         key = Fernet.generate_key()
#         return key.decode()


# class TokenEncoder(BaseToken):

#     def __init__(self, data: dict) -> None:
#         schema = {
#             'sid': {
#                 'typ': 'str',
#             },
#             'jwt': {
#                 'typ': 'dict',
#                 'prop': {
#                     'aes_key': {
#                         'typ': 'str',
#                     },
#                     'rsa_private_pem': {
#                         'typ': 'str',
#                     },
#                     'rsa_key_phrase': {
#                         'typ': 'str',
#                     },
#                     'algorithm': {
#                         'typ': 'str',
#                         'enum': [ALGO_HS256, ALGO_RS256, ALGO_PS256, ALGO_EdDSA, ALGO_ES256]
#                     },
#                     'access_token_lifetime': {
#                         'typ': 'int',
#                     },
#                     'refresh_token_lifetime': {
#                         'typ': 'int',
#                     },
#                     'rotate_refresh_token': {
#                         'typ': 'bool',
#                     },
#                     'header_kid': {
#                         'typ': 'str',
#                     },
#                     'grant_type': {
#                         'typ': 'str',
#                         'enum': [GRANT_TYPE_CODE, GRANT_TYPE_ACCESS_TOKEN, GRANT_TYPE_REFRESH_TOKEN]
#                     },
                    
#                 }
#             },
#             'app': {
#                 'typ': 'dict',
#                 'prop': {
#                     'id': {
#                         'typ': 'uuid',
#                     },
#                     'name': {
#                         'typ': 'str',
#                     },
#                     'client_id': {
#                         'typ': 'str',
#                     },
#                     'domain': {
#                         'typ': 'str',
#                     },
#                     'scope': {
#                         'typ': 'str',
#                     },
#                 }
#             },
#             'aud': {
#                 'typ': 'dict',
#                 'prop': {
#                     'id': {
#                         'typ': 'uuid',
#                     },
#                     'name': {
#                         'typ': 'str',
#                     },
#                     'type': {
#                         'typ': 'str',
#                     },
#                     'roles': {
#                         'typ': 'list',
#                     },
#                     'claims': {
#                         'typ': 'list',
#                     }
#                 }
#             },
#             'user': {
#                 'typ': 'dict',
#                 'prop': {
#                     'id': {
#                         'typ': 'uuid',
#                     },
#                     'username': {
#                         'typ': 'str',
#                     },
#                     'nickname': {
#                         'typ': 'str',
#                     },
#                     'first_name': {
#                         'typ': 'str',
#                     },
#                     'last_name': {
#                         'typ': 'str',
#                     },
#                     'email_address': {
#                         'typ': 'str',
#                     },
#                     'phone_number': {
#                         'typ': 'str',
#                     },
#                     'gender': {
#                         'typ': 'str',
#                     },
#                 }
#             }
#         }
        
#         self.check(schema=schema, data=data)

#         self.sid = UUID(data['sid'])
#         self.app = TokenApp(data=data['app'])
#         self.aud = TokenAud(data=data['aud'])
#         self.jwt = TokenJwt(data=data['jwt'])
#         self.user = TokenUser(data=data['user'])




#     def encode(self) -> Union[str, None]:
#         try:
#             if not self.is_valid:
#                 return None
            
#             aud = []
#             realm_access = {}
#             resource_access = {
#                 'roles': [],
#                 'claims': []
#             }
            
#             token_lifetime =  datetime.now(tz=timezone.utc) + timedelta(hours=self.jwt.refresh_token_lifetime)  
#             if self.jwt.grant_type == GRANT_TYPE_ACCESS_TOKEN :
#                 token_lifetime =  datetime.now(tz=timezone.utc) + timedelta(minutes=self.jwt.access_token_lifetime)
                
#             data = {
#                 'exp': token_lifetime,
#                 'nbf': datetime.now(tz=timezone.utc) + timedelta(seconds=3),
#                 'iat': datetime.now(tz=timezone.utc),
#                 'jti': '',
#                 'iss': f"https://iam.{self.app.domain}/",
#                 'aud': aud,
#                 'sub': self.user.id,
#                 'typ': 'Bearer',
#                 'azp': self.app.name,
#                 'sid': self.sid,
#                 'scope': self.app.scope,
#                 'client_id': self.app.client_id,
#                 'user': {
#                     'id': self.user.id,
#                     'username': self.user.username,
#                     'nickname': self.user.nickname,
#                     'first_name': self.user.first_name,
#                     'middle_name': self.user.middle_name,
#                     'last_name': self.user.last_name,
#                     'email_address': self.user.email_address,
#                     'email_verified': self.user.email_verified,
#                     'phone_number': self.user.phone_number,
#                     'phone_verified': self.user.phone_verified,
#                     'gender': self.user.gender,
#                     'birth_date': self.user.birth_date,
#                     'photo_url': self.user.photo_url,
#                     'photo_verified': self.user.photo_verified,
#                     'profile': self.user.profile,
#                 },
#                 'realm_access': realm_access,
#                 'resource_access': resource_access
#             }

#             key = self.jwt.aes_key
#             headers = {'kid': self.jwt.header_kid}
#             if self.jwt.algorithm != ALGO_HS256:
#                 key = serialization.load_pem_private_key(
#                     self.jwt.rsa_private_pem, password=self.jwt.rsa_key_phrase, backend=default_backend()
#                 )

#             encoded = jwt.encode(data, key, algorithm=self.jwt.algorithm, headers=headers)
#             return encoded
#         except Exception as ex:
            
#             return None


# class TokenDecoder(BaseToken):
    
#     def __init__(self, data: dict) -> None:
#         schema = {
#             'token': {
#                 'typ': 'str',
#             },
#             'aes_key': {
#                 'typ': 'str',
#             },
#             'rsa_public_pem': {
#                 'typ': 'str',
#             },
#             'leeway': {
#                 'typ': 'int',
#             },
#             'algorithm': {
#                 'typ': 'str',
#                 'enum': [ALGO_HS256, ALGO_RS256, ALGO_PS256, ALGO_EdDSA, ALGO_ES256]
#             },
#             'header_kid': {
#                 'typ': 'str',
#             },
#         }
        
#         self.check(schema=schema, data=data)
        
#         self.token = str(data['token'])
#         self.aes_key = str(data['aes_key'])
#         self.rsa_public_pem = bytes(data['rsa_public_pem'])
#         self.algorithm = str(data['algorithm'])
#         self.leeway = int(data['leeway']) if 'leeway' in data else 0
#         self.header_kid = str(data['leeway'])
#         self.iss = f"https://iam.{data['domain']}/"
#         self.aud = []
        
        
#     def decode(self) -> Union[dict, None]:
#         try:
#             if not self.is_valid:
#                 return None
                
#             key = self.aes_key
#             if self.algorithm != ALGO_HS256:
#                 key = serialization.load_pem_public_key(self.rsa_public_pem)
                
#             data = jwt.decode(
#                 jwt=self.token, 
#                 key=key, 
#                 issuer=self.iss, 
#                 audience=self.aud, 
#                 leeway=self.leeway, 
#                 options={"require": ["exp", "iss", "sub"]},
#                 algorithms=[self.algorithm]
#             )
#             return dict(data)
#         except jwt.ExpiredSignatureError:
#             print("expired")
#             return None
#         except jwt.InvalidIssuerError:
#             print("invalid issuer")
#             return None
#         except jwt.InvalidAudienceError:
#             print("invalid audience")
#             return None
#         except jwt.MissingRequiredClaimError as ex:
#             print(ex)
#             return None
