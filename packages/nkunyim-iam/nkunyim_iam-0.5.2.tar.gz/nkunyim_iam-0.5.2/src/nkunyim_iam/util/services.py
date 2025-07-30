
from django.http import HttpRequest

from nkunyim_iam.util.application import Application
from nkunyim_iam.util.cache import ApplicationCache, LocationCache, NationCache, UserAgentCache
from nkunyim_iam.util.location import Location
from nkunyim_iam.util.nation import Nation
from nkunyim_iam.util.session import HttpSession
from nkunyim_iam.util.useragent import UserAgent


class ApplicationService:
    
    def __init__(self, req: HttpRequest, sess: HttpSession) -> None:
        self.sess = sess
        self.req = req
        
    def get(self) -> Application:
        key = f"app.{self.sess.get_session_key()}"
        cache_manager = ApplicationCache()
        application = cache_manager.get_application(key=key)
        if not application:
            application = Application(req=self.req)
            cache_manager.set_application(key=key, application_data=application, timeout=60 * 60 * 24)
            
        nat_data = {
            'id': application.id,
            'client_id': application.client_id,
            'name': application.name,
            'title': application.title,
        }
        self.sess.set_nat(data=nat_data)
        
        return application
    

class NationService:
    
    def __init__(self, req: HttpRequest, sess: HttpSession) -> None:
        self.sess = sess
        self.req = req
        
    def get(self, code: str) -> Nation:
        key = f"nat.{self.sess.get_session_key()}"
        cache_manager = NationCache()
        nation = cache_manager.get_nation(key=key)
        if not nation:
            nation = Nation(req=self.req, code=code.upper())
            cache_manager.set_nation(key=key, nation_data=nation, timeout=60 * 60 * 24)
            
        nat_data = {
            'id': nation.id,
            'code': nation.code,
            'name': nation.name
        }
        self.sess.set_nat(data=nat_data)
        
        return nation
        

class LocationService:
    
    def __init__(self, req: HttpRequest, sess: HttpSession) -> None:
        self.sess = sess
        self.req = req
    
    def get(self) -> Location:
        key = f"loc.{self.sess.get_session_key()}"
        cache_manager = LocationCache()
        location = cache_manager.get_location(key=key)
        if not location:
            location = Location(req=self.req)
            cache_manager.set_location(key=key, location_data=location, timeout=60 * 60 * 24)
            
        return location
    
    

class UserAgentService:
    
    def __init__(self, req: HttpRequest, sess: HttpSession) -> None:
        self.sess = sess
        self.req = req
    
    def get(self) -> UserAgent:
        key = f"ua.{self.sess.get_session_key()}"
        cache_manager = UserAgentCache()
        user_agent = cache_manager.get_user_agent(key=key)
        if not user_agent:
            user_agent = UserAgent(req=self.req)
            cache_manager.set_user_agent(key=key, user_agent_data=user_agent, timeout=60 * 60 * 24)
            
        return user_agent