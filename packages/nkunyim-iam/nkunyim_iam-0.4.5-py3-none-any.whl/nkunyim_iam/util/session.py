from typing import Union
from django.http import HttpRequest


class Session:
    def __init__(self, req: HttpRequest) -> None:
        self.req = req
    
    def get_host_parts(self) -> list[str]:
        host = self.req.get_host()
        host_parts = host.lower().split('.')
        return host_parts
    
    
    def get_subdomain(self) -> str:
        host_parts = self.get_host_parts()
        return host_parts[-3] if len(host_parts) > 2 else "www"
    
    
    def get_domain(self) -> str:
        host_parts = self.get_host_parts()
        return f"{host_parts[-2]}.{host_parts[-1]}"
    
    
    def get_session_key(self) -> str:
        subdomain = self.get_subdomain()
        domain = self.get_domain()
        session_key = f"{subdomain}.{domain}"
        return session_key
    
        
    def set_app(self, data: dict) -> None:
        session_key = f"app.{self.get_session_key()}"
        self.req.session[session_key] = data
        self.req.session.modified = True
        
    
    def get_app(self) -> Union[dict, None]:
        session_key = f"app.{self.get_session_key()}"
        if not bool(session_key in self.req.session):
            return None

        app = self.req.session[session_key]
        return app
    
        
    def set_nat(self, data: dict) -> None:
        session_key = f"nat.{self.get_session_key()}"
        self.req.session[session_key] = data
        self.req.session.modified = True
        
    
    def get_nat(self) -> Union[dict, None]:
        session_key = f"nat.{self.get_session_key()}"
        if not bool(session_key in self.req.session):
            return None

        nat = self.req.session[session_key]
        return nat


    def set_token(self, data: Union[dict, None]) -> None:
        session_key = f"auth.{self.get_session_key()}"
        self.req.session[session_key] = data
        self.req.session.modified = True


    def get_token(self) -> Union[dict, None]:
        session_key = f"auth.{self.get_session_key()}"
        if not bool(session_key in self.req.session):
            return None

        token = self.req.session[session_key]
        return token
    
    

class HttpSession(Session):

    def __init__(self, req: HttpRequest) -> None:
        super().__init__(req=req)

        
    def set_account(self, data: dict) -> None:
        session_key = f"http.{self.get_session_key()}"
        self.req.session[session_key] = data
        self.req.session.modified = True


    def get_account(self) -> Union[dict, None]:
        session_key = f"http.{self.get_session_key()}"
        if not bool(session_key in self.req.session):
            return None

        account = self.req.session[session_key]
        return account


    def get_user(self) -> Union[dict, None]:
        user_data = None
        user = self.req.user
        if user.is_authenticated:
            user_data = user.__dict__.copy()
            if not user.is_superuser:
                user_data.pop('is_superuser')
            
        return user_data
    
    
    def get_app_data(self) -> dict:
        app = self.get_app()
        return app if app and 'name' in app else {}
    
    
    def get_nat_data(self) -> dict:
        nat = self.get_nat()
        return nat if nat and 'code' in nat else {}
    

    def kill(self) -> None:
        self.req.session.clear()
        self.req.session.flush()
        

