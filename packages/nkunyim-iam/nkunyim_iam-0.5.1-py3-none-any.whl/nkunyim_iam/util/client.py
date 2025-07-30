import base64
import json
import requests
from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.util.encryption import Encryption
from nkunyim_iam.util.session import HttpSession


class HttpClient:
    def __init__(self, req: HttpRequest, name: str) -> None:
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.req = req
        self.name = name.upper()
        self._init_base_url()
        self._init_headers()

    def _init_base_url(self) -> None:
        try:
            base_url = str(settings.NKUNYIM_SERVICES[self.name])
            self.base_url = base_url.rstrip('/')
        except KeyError:
            raise Exception(f"Service configuration '{self.name}' is not defined in settings.")

    def _init_headers(self) -> None:
        sess = HttpSession(self.req)
        encryption = Encryption()

        self._add_xan_authorization_header(sess, encryption)
        self._add_jwt_authorization_header(sess, encryption)

    def _add_xan_authorization_header(self, sess: HttpSession, encryption: Encryption) -> None:
        app_data = sess.get_app_data()
        nat_data = sess.get_nat_data()

        if app_data and nat_data and 'name' in app_data and 'code' in nat_data:
            payload = json.dumps({'app': app_data, 'nat': nat_data})
            encrypted = encryption.rsa_encrypt(plain_text=payload, name=self.name)
            token = base64.b64encode(encrypted).decode('utf-8')
            self.headers['Xan-Authorization'] = token

    def _add_jwt_authorization_header(self, sess: HttpSession, encryption: Encryption) -> None:
        user_data = sess.get_user()
        if user_data and 'id' in user_data:
            payload = json.dumps(user_data)
            encrypted = encryption.rsa_encrypt(plain_text=payload, name=self.name)
            token = base64.b64encode(encrypted).decode('utf-8')
            self.headers['Authorization'] = f'JWT {token}'

    def _build_url(self, path: str) -> str:
        base = self.base_url
        if not base.endswith('/api'):
            base += '/api'

        if not path.startswith('/'):
            path = '/' + path

        return base + path

    def get(self, path: str):
        return requests.get(self._build_url(path), headers=self.headers)

    def post(self, path: str, data: dict):
        url = self._build_url(path)
        if not url.endswith('/'):
            url += '/'
        return requests.post(url, data=data, headers=self.headers)

    def put(self, path: str, data: dict):
        return requests.put(self._build_url(path), data=data, headers=self.headers)

    def patch(self, path: str, data: dict):
        return requests.patch(self._build_url(path), data=data, headers=self.headers)

    def delete(self, path: str):
        return requests.delete(self._build_url(path), headers=self.headers)
