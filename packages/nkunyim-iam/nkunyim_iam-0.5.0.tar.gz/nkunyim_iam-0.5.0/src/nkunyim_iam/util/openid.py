from typing import Union
from uuid import uuid4
from urllib.parse import urlencode

import requests
from django.http import HttpRequest

from nkunyim_iam.util.session import Session


class OpenIdConnect:
    def __init__(self, req: HttpRequest) -> None:
        self.req = req
        self.session = Session(req=req)

    def _session_key(self) -> str:
        return f"oidc.{self.session.get_session_key()}"

    def _get_from_session(self, key: str) -> Union[dict, None]:
        return self.req.session.get(key)

    def _set_to_session(self, key: str, value: dict) -> None:
        self.req.session[key] = value
        self.req.session.modified = True

    def _del_from_session(self, key: str) -> None:
        if key in self.req.session:
            del self.req.session[key]
            self.req.session.modified = True

    def _get_app(self) -> dict:
        app = self.session.get_app()
        if not app:
            raise Exception("App Exception: Could not load client details.")
        return app

    def _get_token(self) -> dict:
        token = self.session.get_token()
        if not token or 'access_token' not in token:
            raise Exception("Token exception. No access token found.")
        return token

    def get_authorization_url(self) -> str:
        app = self._get_app()
        oidc_data = self.get_oidc_data()

        query_params = {
            "response_type": app["response_type"],
            "client_id": app["client_id"],
            "redirect_uri": self.get_redirect_url(),
            "state": oidc_data["state"],
            "nonce": oidc_data["nonce"],
            "scope": app["scope"],
        }
        return f"{self.get_issuer_url()}/authorize?{urlencode(query_params)}"

    def get_oidc_data(self) -> dict:
        key = self._session_key()
        if key in self.req.session:
            return self.req.session[key]

        data = {
            "nonce": str(uuid4()),
            "state": str(uuid4()),
            "issuer": self.get_issuer_url(),
        }
        self._set_to_session(key, data)
        return data

    def set_oidc_data(self, data: dict) -> None:
        self._set_to_session(self._session_key(), data)

    def delete_oidc_data(self) -> None:
        self._del_from_session(self._session_key())

    def get_issuer_url(self) -> str:
        return f"https://iam.{self.session.get_domain()}"

    def get_redirect_url(self) -> str:
        return f"https://app.{self.session.get_domain()}/login/"

    def get_post_logout_redirect_url(self) -> str:
        return f"https://app.{self.session.get_domain()}/logout/"

    def get_access_token(self) -> bool:
        state = self.req.GET.get("state")
        code = self.req.GET.get("code")
        oidc_data = self.get_oidc_data()

        if state != oidc_data["state"]:
            raise Exception("Token exception. Invalid state.")

        app = self._get_app()
        data = {
            "grant_type": "access_token",
            "code": code,
            "redirect_uri": self.get_redirect_url(),
            "client_id": app["client_id"],
            "client_secret": app["client_secret"],
        }

        res = requests.post(
            f"{self.get_issuer_url()}/token",
            data=data,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        if res.ok:
            self.session.set_token(res.json())
            self.delete_oidc_data()
            return True
        raise Exception(f"Token exception. {res.status_code} - {res.text}")

    def get_user_info(self) -> dict:
        token = self._get_token()
        res = requests.get(
            f"{self.get_issuer_url()}/userinfo",
            headers={
                "Authorization": f"Bearer {token['access_token']}",
                "Accept": "application/json",
            },
        )
        if res.ok:
            return res.json()
        raise Exception(f"User info exception. {res.status_code} - {res.text}")

    def logout(self) -> bool:
        token = self._get_token()
        app = self._get_app()
        res = requests.get(
            f"{self.get_issuer_url()}/logout",
            headers={
                "Authorization": f"Bearer {token['access_token']}",
                "Accept": "application/json",
            },
            params={
                "client_id": app["client_id"],
                "post_logout_redirect_uri": self.get_post_logout_redirect_url(),
            },
        )
        if res.ok:
            self.session.set_token(None)
            return True
        raise Exception(f"Logout exception. {res.status_code} - {res.text}")

    def get_logout_url(self) -> str:
        app = self._get_app()
        return (
            f"{self.get_issuer_url()}/logout?"
            f"client_id={app['client_id']}&"
            f"post_logout_redirect_uri={self.get_post_logout_redirect_url()}"
        )

    def end_session(self) -> bool:
        token = self._get_token()
        app = self._get_app()
        res = requests.get(
            f"{self.get_issuer_url()}/end_session",
            headers={
                "Authorization": f"Bearer {token['access_token']}",
                "Accept": "application/json",
            },
            params={
                "client_id": app["client_id"],
                "post_logout_redirect_uri": self.get_redirect_url(),
            },
        )
        if res.ok:
            self.session.set_token(None)
            return True
        raise Exception(f"End session exception. {res.status_code} - {res.text}")

    def get_refresh_token(self) -> bool:
        token = self._get_token()
        if "refresh_token" not in token:
            raise Exception("Token exception. No refresh token found.")

        app = self._get_app()
        res = requests.post(
            f"{self.get_issuer_url()}/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": token["refresh_token"],
                "client_id": app["client_id"],
                "client_secret": app["client_secret"],
            },
            headers={
                "Authorization": f"Bearer {token['access_token']}",
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        if res.ok:
            self.session.set_token(res.json())
            return True
        raise Exception(f"Refresh token exception. {res.status_code} - {res.text}")

    def is_authenticated(self) -> bool:
        return self.is_token_valid() and not self.is_token_expired()

    def is_token_valid(self) -> bool:
        token = self.session.get_token()
        return bool(token and "access_token" in token and "expires_in" in token)

    def is_token_expired(self) -> bool:
        token = self.session.get_token()
        if not token or "expires_in" not in token:
            raise Exception("Token exception. No expiry time found.")
        return token["expires_in"] <= 5

    def is_session_valid(self) -> bool:
        return self.is_authenticated()

    def is_token_refreshable(self) -> bool:
        token = self.session.get_token()
        return bool(token and "refresh_token" in token)

    def get_access_token_value(self) -> str:
        return self._get_token()["access_token"]

    def get_refresh_token_value(self) -> str:
        token = self._get_token()
        if "refresh_token" not in token:
            raise Exception("Token exception. No refresh token found.")
        return token["refresh_token"]

    def get_expiry_time(self) -> int:
        token = self._get_token()
        if "expires_in" not in token:
            raise Exception("Token exception. No expiry time found.")
        return token["expires_in"]




class OpenIdProvider:
    def __init__(self, req: HttpRequest) -> None:
        self.req = req
        self.session = Session(req=req)

    def _session_key(self) -> str:
        return f"oidc.{self.session.get_session_key()}"

    def _get_from_session(self) -> Union[dict, None]:
        return self.req.session.get(self._session_key())

    def _set_to_session(self, value: dict) -> None:
        self.req.session[self._session_key()] = value
        self.req.session.modified = True

    def _del_from_session(self) -> None:
        key = self._session_key()
        if key in self.req.session:
            del self.req.session[key]
            self.req.session.modified = True

    def _get_token(self) -> dict:
        token = self.session.get_token()
        if not token or 'access_token' not in token:
            raise Exception("Token exception. No access token found.")
        return token

    def _require_param(self, name: str, allowed: Union[list, None] = None) -> str:
        value = self.req.GET.get(name)
        if not value:
            raise Exception(f"{name.replace('_', ' ').title()} not provided in the request.")
        if allowed and value not in allowed:
            raise Exception(f"Invalid {name}. Must be one of {allowed}.")
        return value

    def get_client(self) -> str:
        existing = self._get_from_session()
        if existing:
            return existing['client_id']

        client_id = self._require_param('client_id')
        redirect_uri = self._require_param('redirect_uri')
        state = self._require_param('state')
        response_type = self._require_param('response_type', allowed=['code', 'token'])
        scope = self.req.GET.get('scope', 'openid')

        if 'openid' not in scope.split():
            raise Exception("Scope must include 'openid'.")

        nonce = self.req.GET.get('nonce') or str(uuid4())

        oidc_data = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'state': state,
            'response_type': response_type,
            'scope': scope,
            'nonce': nonce
        }

        self._set_to_session(oidc_data)
        return client_id

    def get_oidc_data(self) -> Union[dict, None]:
        return self._get_from_session()

    def set_oidc_data(self, data: dict) -> None:
        self._set_to_session(data)

    def delete_oidc_data(self) -> None:
        self._del_from_session()

    def is_authenticated(self) -> bool:
        return self.is_token_valid() and not self.is_token_expired()

    def is_token_valid(self) -> bool:
        token = self.session.get_token()
        return bool(token and 'access_token' in token and 'expires_in' in token)

    def is_token_expired(self) -> bool:
        token = self.session.get_token()
        if not token or 'expires_in' not in token:
            raise Exception("Token exception. No expiry time found.")
        return token['expires_in'] <= 5

    def is_session_valid(self) -> bool:
        return self.is_authenticated()

    def is_token_refreshable(self) -> bool:
        token = self.session.get_token()
        return bool(token and 'refresh_token' in token)

    def get_expiry_time(self) -> int:
        token = self._get_token()
        if 'expires_in' not in token:
            raise Exception("Token exception. No expiry time found.")
        return token['expires_in']

    def get_access_token_value(self) -> str:
        return self._get_token()['access_token']

    def get_refresh_token_value(self) -> str:
        token = self._get_token()
        if 'refresh_token' not in token:
            raise Exception("Token exception. No refresh token found.")
        return token['refresh_token']
