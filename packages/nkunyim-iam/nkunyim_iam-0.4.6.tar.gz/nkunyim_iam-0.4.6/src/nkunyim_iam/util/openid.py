from typing import Union
import requests
from uuid import uuid4
from urllib.parse import urlencode

from django.http import HttpRequest

from nkunyim_iam.util.session import Session



class OpenIdConnect:
        
    def __init__(self, req: HttpRequest) -> None:
        self.session = Session(req=req)
        self.req =  req
        
    # The OpenIdConnect class provides methods to interact with an OpenID Connect provider.
    # It allows you to get the authorization URL, retrieve OIDC data, get the issuer URL,
    # get the redirect URL, exchange a code for an access token, retrieve user info,
    # and perform logout or end session operations. The class uses the Session utility
    # to manage session data and store OIDC-related information in the Django session.
    # It also handles exceptions related to token retrieval and user info access.
    # The class provides methods to check if the user is authenticated, get access and refresh tokens,
    # check token validity, and determine if the session is valid. It also includes methods to
    # check if the access token is expired and if it can be refreshed.

        
    def get_authorization_url(self) -> str:
        # Load app else raise exception
        app = self.session.get_app()
        if not app:
            raise Exception(f"App Exception: Could not load client details.")
        
        oidc_data = self.get_oidc_data()
        authorization_url = f"{self.get_issuer_url()}/authorize?" + urlencode(
            {
                "response_type": app['response_type'],
                "client_id": app['client_id'],
                "redirect_uri": self.get_redirect_url(),
                "state": oidc_data['state'],
                "nonce": oidc_data['nonce'],
                "scope": app['scope'],
            }
        )

        return authorization_url
    
    
    def get_oidc_data(self) -> dict:
        session_key = f"oidc.{self.session.get_session_key()}"
        if bool(session_key in self.req.session):
            return self.req.session[session_key]
        
        oidc_data = {
            'nonce': str(uuid4()),
            'state': str(uuid4()),
            'issuer': self.get_issuer_url(),
        }
        self.req.session[session_key] = oidc_data
        self.req.session.modified = True
        
        return oidc_data
    
    
    def set_oidc_data(self, data: dict) -> None:
        session_key = f"oidc.{self.session.get_session_key()}"
        self.req.session[session_key] = data
        self.req.session.modified = True
        
    
    def delete_oidc_data(self) -> None:
        session_key = f"oidc.{self.session.get_session_key()}"
        if bool(session_key in self.req.session):
            del self.req.session[session_key]
            self.req.session.modified = True
    
    
    def get_issuer_url(self) -> str:
        domain = self.session.get_domain()
        return f"https://iam.{domain}"
    
    
    def get_redirect_url(self) -> str:
        """
        Returns the redirect URL for the OpenID Connect flow.
        This URL is where the user will be redirected after authentication.
        """ 
        domain = self.session.get_domain()
        return f"https://app.{domain}/login/"
    
    
    def get_post_logout_redirect_url(self) -> str:
        """
        Returns the post-logout redirect URL for the OpenID Connect flow.
        This URL is where the user will be redirected after logging out.
        """
        domain = self.session.get_domain()
        return f"https://app.{domain}/logout/"
    
    
    def get_access_token(self) -> bool:
        state = self.req.GET.get('state', None)
        code = self.req.GET.get('code', None)
        oidc_data = self.get_oidc_data()
        if state != oidc_data['state']:
            raise Exception("Token exception. Invalid state")
        
        app = self.session.get_app()
        if not app:
            raise Exception(f"App Exception: Could not load client details.")
        
        data = {
            'grant_type': 'access_token',
            'code': code,
            'redirect_uri': self.get_redirect_url(),
            'client_id': app['client_id'],
            'client_secret': app['client_secret']
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        token_url = f"{self.get_issuer_url()}/token"
        
        res = requests.post(token_url, data=data, headers=headers)
        if res.ok:
            access_token = res.json()
            self.session.set_token(data=access_token)
            self.delete_oidc_data()  # Clear OIDC data after successful token retrieval
            return True
        else:
            raise Exception(f"Token exception. {res.status_code} - {res.text}")
    
     
    def get_user_info(self) -> dict:
        token_data = self.session.get_token()
        if not token_data or 'access_token' not in token_data:
            raise Exception("Token exception. No access token found.")
        
        headers = {
            'Authorization': f"Bearer {token_data['access_token']}",
            'Accept': 'application/json',
        }
        userinfo_url = f"{self.get_issuer_url()}/userinfo"
        
        res = requests.get(userinfo_url, headers=headers)
        if res.ok:
            return res.json()
        else:
            raise Exception(f"User info exception. {res.status_code} - {res.text}")
            
            
    def logout(self) -> bool:
        token_data = self.session.get_token()
        if not token_data or 'access_token' not in token_data:
            raise Exception("Token exception. No access token found.")
        
        app = self.session.get_app()
        if not app:
            raise Exception(f"App Exception: Could not load client details.")
        
        headers = {
            'Authorization': f"Bearer {token_data['access_token']}",
            'Accept': 'application/json',
        }
        logout_url = f"{self.get_issuer_url()}/logout?client_id={app['client_id']}&post_logout_redirect_uri={self.get_post_logout_redirect_url()}"
        
        res = requests.get(logout_url, headers=headers)
        if res.ok:
            self.session.set_token(data=None)
            return True
        else:
            raise Exception(f"Logout exception. {res.status_code} - {res.text}")
        
        
    def get_logout_url(self) -> str:
        app = self.session.get_app()
        if not app:
            raise Exception(f"App Exception: Could not load client details.")
        
        logout_url = f"{self.get_issuer_url()}/logout?client_id={app['client_id']}&post_logout_redirect_uri={self.get_post_logout_redirect_url()}"
        return logout_url
    
        
    def end_session(self) -> bool:
        token_data = self.session.get_token()
        if not token_data or 'access_token' not in token_data:
            raise Exception("Token exception. No access token found.")
        
        app = self.session.get_app()
        if not app:
            raise Exception(f"App Exception: Could not load client details.")
        
        headers = {
            'Authorization': f"Bearer {token_data['access_token']}",
            'Accept': 'application/json',
        }
        end_session_url = f"{self.get_issuer_url()}/end_session?client_id={app['client_id']}&post_logout_redirect_uri={self.get_redirect_url()}"
        
        res = requests.get(end_session_url, headers=headers)
        if res.ok:
            self.session.set_token(data=None)
            return True
        else:
            raise Exception(f"End session exception. {res.status_code} - {res.text}")
        
        
    def get_refresh_token(self) -> bool:
        token_data = self.session.get_token()
        if not token_data or 'refresh_token' not in token_data:
            raise Exception("Token exception. No refresh token found.")
        
        app = self.session.get_app()
        if not app:
            raise Exception(f"App Exception: Could not load client details.")
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': token_data['refresh_token'],
            'client_id': app['client_id'],
            'client_secret': app['client_secret']
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Bearer {token_data['access_token']}",
        }
        token_url = f"{self.get_issuer_url()}/token"
        
        res = requests.post(token_url, data=data, headers=headers)
        if res.ok:
            new_token_data = res.json()
            self.session.set_token(data=new_token_data)
            return True
        else:
            raise Exception(f"Refresh token exception. {res.status_code} - {res.text}")


    def is_authenticated(self) -> bool:
        """
        Check if the user is authenticated by verifying if a valid access token exists.
        """
        token_data = self.session.get_token()
        return bool(token_data and 'access_token' in token_data and not self.is_token_expired())
    
    
    def get_expiry_time(self) -> int:
        """
        Get the expiry time of the access token in seconds.
        Returns the time in seconds until the access token expires.
        """
        token_data = self.session.get_token()
        if not token_data or 'expires_in' not in token_data:
            raise Exception("Token exception. No expiry time found.")
        
        return token_data['expires_in']
    
    
    def get_access_token_value(self) -> str:
        """
        Get the value of the access token.
        Returns the access token string if it exists, otherwise raises an exception.
        """
        token_data = self.session.get_token()
        if not token_data or 'access_token' not in token_data:
            raise Exception("Token exception. No access token found.")
        
        return token_data['access_token']
    
    
    def get_refresh_token_value(self) -> str:
        """
        Get the value of the refresh token.
        Returns the refresh token string if it exists, otherwise raises an exception.
        """
        token_data = self.session.get_token()
        if not token_data or 'refresh_token' not in token_data:
            raise Exception("Token exception. No refresh token found.")
        
        return token_data['refresh_token']
    
    
    def is_token_valid(self) -> bool:
        """
        Check if the access token is valid.
        Returns True if the access token is valid, False otherwise.
        """
        token_data = self.session.get_token()
        if not token_data or 'access_token' not in token_data:
            return False
        
        # Check if the access token is expired
        return not self.is_token_expired()
    
    
    def is_token_expired(self) -> bool:
        """
        Check if the access token is expired.
        Returns True if the access token is expired, False otherwise.
        """
        token_data = self.session.get_token()
        if not token_data or 'expires_in' not in token_data:
            raise Exception("Token exception. No expiry time found.")
        
        return token_data['expires_in'] <= 5 # 5 seconds before actual expiration to allow for refresh attempts

    def is_session_valid(self) -> bool:
        """
        Check if the session is valid.
        Returns True if the session is valid, False otherwise.
        """
        return self.is_authenticated() and self.is_token_valid()
    
    
    def is_token_refreshable(self) -> bool:
        """
        Check if the access token is refreshable.
        Returns True if the access token can be refreshed, False otherwise.
        """
        token_data = self.session.get_token()
        return bool(token_data and 'refresh_token' in token_data)



class OpenIdProvider:
    
    def __init__(self, req: HttpRequest) -> None:
        self.session = Session(req=req)
        self.req =  req
    
    # The OpenIdProvider class provides methods to interact with an OpenID Connect provider.
    # It allows you to get the client details from the request, including client ID, redirect URI,
    # state, response type, scope, and nonce. The class raises exceptions if any of the required parameters
    # are missing or if the response type is invalid. It also ensures that the scope includes 'openid' and generates a nonce if it is not provided.
    # The get_client method returns a dictionary containing the client details,
    # which can be used for further processing in the OpenID Connect flow.  
        
    def get_client(self) -> str:
        oidc_data = self.get_oidc_data()
        if oidc_data:
            return oidc_data['client_id']
        
        client_id = self.req.GET.get('client_id', None)
        if not client_id:
            raise Exception("Client ID not provided in the request.")
        
        redirect_uri = self.req.GET.get('redirect_uri', None)
        if not redirect_uri:
            raise Exception("Redirect URI not provided in the request.")
        
        state = self.req.GET.get('state', None)
        if not state:
            raise Exception("State not provided in the request.")
        
        response_type = self.req.GET.get('response_type', 'code')
        if response_type not in ['code', 'token']:
            raise Exception("Invalid response type. Must be 'code' or 'token'.")
        
        scope = self.req.GET.get('scope', 'openid')
        scopes = scope.split(' ')
        if 'openid' not in scopes:
            raise Exception("Scope must include 'openid'.")
        
        nonce = self.req.GET.get('nonce', None)
        if not nonce:
            nonce = str(uuid4())
            
        oidc_data = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'state': state,
            'response_type': response_type,
            'scope': scope,
            'nonce': nonce
        }
        self.set_oidc_data(data=oidc_data)
        
        return client_id
    
    
    def get_oidc_data(self) -> Union[dict, None]:
        session_key = f"oidc.{self.session.get_session_key()}"
        if not bool(session_key in self.req.session):
            return None
            
        return self.req.session[session_key]
        
    
    def set_oidc_data(self, data: dict) -> None:
        session_key = f"oidc.{self.session.get_session_key()}"
        self.req.session[session_key] = data
        self.req.session.modified = True
        
    
    def delete_oidc_data(self) -> None:
        session_key = f"oidc.{self.session.get_session_key()}"
        if bool(session_key in self.req.session):
            del self.req.session[session_key]
            self.req.session.modified = True
    

    def is_authenticated(self) -> bool:
        """
        Check if the user is authenticated by verifying if a valid access token exists.
        """
        token_data = self.session.get_token()
        return bool(token_data and 'access_token' in token_data and not self.is_token_expired())
    
    
    def get_expiry_time(self) -> int:
        """
        Get the expiry time of the access token in seconds.
        Returns the time in seconds until the access token expires.
        """
        token_data = self.session.get_token()
        if not token_data or 'expires_in' not in token_data:
            raise Exception("Token exception. No expiry time found.")
        
        return token_data['expires_in']
    
    
    def get_access_token_value(self) -> str:
        """
        Get the value of the access token.
        Returns the access token string if it exists, otherwise raises an exception.
        """
        token_data = self.session.get_token()
        if not token_data or 'access_token' not in token_data:
            raise Exception("Token exception. No access token found.")
        
        return token_data['access_token']
    
    
    def get_refresh_token_value(self) -> str:
        """
        Get the value of the refresh token.
        Returns the refresh token string if it exists, otherwise raises an exception.
        """
        token_data = self.session.get_token()
        if not token_data or 'refresh_token' not in token_data:
            raise Exception("Token exception. No refresh token found.")
        
        return token_data['refresh_token']
    
    
    def is_token_valid(self) -> bool:
        """
        Check if the access token is valid.
        Returns True if the access token is valid, False otherwise.
        """
        token_data = self.session.get_token()
        if not token_data or 'access_token' not in token_data:
            return False
        
        # Check if the access token is expired
        return not self.is_token_expired()
    
    
    def is_token_expired(self) -> bool:
        """
        Check if the access token is expired.
        Returns True if the access token is expired, False otherwise.
        """
        token_data = self.session.get_token()
        if not token_data or 'expires_in' not in token_data:
            raise Exception("Token exception. No expiry time found.")
        
        return token_data['expires_in'] <= 5 # 5 seconds before actual expiration to allow for refresh attempts


    def is_session_valid(self) -> bool:
        """
        Check if the session is valid.
        Returns True if the session is valid, False otherwise.
        """
        return self.is_authenticated() and self.is_token_valid()
    
    
    def is_token_refreshable(self) -> bool:
        """
        Check if the access token is refreshable.
        Returns True if the access token can be refreshed, False otherwise.
        """
        token_data = self.session.get_token()
        return bool(token_data and 'refresh_token' in token_data)

