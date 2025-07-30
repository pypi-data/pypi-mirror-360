from typing import Union
from uuid import uuid4
from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.util.application import Application
from nkunyim_iam.util.location import Location
from nkunyim_iam.util.nation import Nation
from nkunyim_iam.util.services import ApplicationService, LocationService, NationService, UserAgentService
from nkunyim_iam.util.session import HttpSession
from nkunyim_iam.util.useragent import UserAgent



class HttpContext:

    def __init__(self, req: HttpRequest) -> None:
        """
        Initializes the HttpContext with the given request.
        Args:
            req (HttpRequest): The HTTP request object containing request data.
        This class extends HttpSession to provide context-specific data for the request.
        It initializes user, role, business, page, pages, navigation, and alerts data.
        The context is created by processing the request path and setting up the necessary data structures.
        The context can be used to access user information, page details, navigation menus, and alerts
        """
        self._session = HttpSession(req=req)
        
        self._req = req
        self._app: dict = {}
        self._role: Union[dict, None] = None
        self._business: Union[dict, None] = None
        self._user: Union[dict, None] = self._session.get_user()
        self._page: Union[dict, None] = None
        self._pages: Union[dict, None] = None
        self._navs: Union[list[dict], None] = None


    def create(self) -> None:
        """
        Sets up the context by initializing app, user, role, business, menus, alerts, and navigation data.
        This method processes the request path to determine the current page and its associated data.
        """
        # Initialize user, role, business, menus, alerts, navs
        app = {}
        role = None
        business = None
        user = self.user
        
        menus = []
        navs = []
        
        toolbox_name = "toolbox"
        toolbox_menus = []
        
        manage_name =  "manage"
        manage_menus = []
        
        system_name = "system"
        system_menus = []
        
        env = settings.NKUNYIM_ENV
        
        path = self._req.path.lower()
        paths = ['/']
        node = "index"

        if len(path) > 1 and path.strip('/') != "":
            paths = path.strip('/').split('/')
            node = paths[-1]
        
        page = {
            "path": path,
            "paths": paths,
            "node": node,
            'name': "{}Page".format(node.title())
        }
        
        pages = dict(settings.NKUNYIM_PAGES)
        
        # Account and Role
        account = self._session.get_account()
        if account and 'role' in account:
            menus = account['menus']
            role = account['role']
            business = account['business']
            
        if user and 'is_superuser' in user and user['is_superuser']:
            menus.append(
               {
                "id": str(uuid4()),
                "node": "system", 
                "module": {
                    "id": str(uuid4()),
                    "name": "Xvix",
                    "title": "AutoFix",
                    "caption": "Manage auto-fix data",
                    "icon": "mdi mdi-auto-fix",
                    "path": "xvix",
                    "route": "#xvix",
                },
                "items": [],
                "is_active": True
            })

        for menu in menus:
            # Node
            if menu['node'] == toolbox_name:
                toolbox_menus.append(menu)
                
            if menu['node'] == manage_name:
                manage_menus.append(menu)
                
            if menu['node'] == system_name:
                system_menus.append(menu)

            # Menu
            m_name = menu['module']['name']
            m_path = menu['module']['path']
            m_key = "{}Page".format(str(m_name).title())
            m_val = "./{m}/home.{e}".format(m=str(m_path).lower(), e=env)
            pages[m_key] = m_val

            # Item
            if menu['items'] and len(menu['items']) > 0:
                for item in menu['items']:
                    i_name = item['page']['name']
                    i_path = item['page']['path']
                    i_key = "{}{}Page".format(str(m_name).title(), str(i_name).title())
                    i_val = "./{m}/{p}.{e}".format(m=str(m_path).lower(), p=str(i_path).lower(), e=env)
                    pages[i_key] = i_val

        if len(toolbox_menus) > 0:
            navs.append(
                {
                    "name": toolbox_name.title(),
                    "menus": toolbox_menus
                }
            )

        if len(manage_menus) > 0:
            navs.append(
                {
                    "name": manage_name.title(),
                    "menus": manage_menus
                }
            )
            
        if len(system_menus) > 0:
            navs.append(
                {
                    "name": system_name.title(),
                    "menus": system_menus
                }
            )
           
        self._page = page
        self._pages = pages
        self._navs = navs
        self._user = user
        
        if user and 'username' in user and self._session.get_subdomain() == "app":
            self._role = role
            self._business = business


    @property
    def app(self) -> Application:
        """ Returns the application data for the current request. """
        service = ApplicationService(req=self._req, sess=self._session)
        return service.get()
    
    @property
    def role(self) -> Union[dict, None]:
        """ Returns the role data for the current user. """
        return self._role
    
    @property
    def business(self) -> Union[dict, None]:
        """ Returns the business data for the current user. """
        return self._business
    
    @property
    def user(self) -> Union[dict, None]:
        """ Returns the user data for the current request. """
        return self._user
    
    @property
    def page(self) -> Union[dict, None]:
        """ Returns the current page data for the request. """
        return self._page
    
    @property
    def pages(self) -> Union[dict, None]:
        """ Returns the available pages data for the request. """
        return self._pages
    
    @property
    def navs(self) -> Union[list[dict], None]:
        """ Returns the navigation data for the request. """
        return self._navs
    
    @property
    def user_agent(self) -> UserAgent:
        """
        Returns the user agent from the request.
        """
        service = UserAgentService(req=self._req, sess=self._session)
        return service.get()
    
    @property
    def location(self) -> Location:
        """
        Returns the location of the request.
        """
        service = LocationService(req=self._req, sess=self._session)
        return service.get()
    
    @property
    def nation(self) -> Nation:
        """
        Returns the nation of the request.
        """
        service = NationService(req=self._req, sess=self._session)
        return service.get(code=self.location.country_code.upper())
    
    @property   
    def data(self) -> dict:
        """ Returns a dictionary containing the context data for the request.
        This includes application data, page information, navigation menus, alerts, 
        user, role, business, user_agent, location and nation data.
        """
        
        exclude_keys = {
            'aes_key',
            'rsa_public_pem',
            'rsa_private_pem',
            'rsa_passphrase',
            'algorithm',
            'client_secret', 
            'grant_type',
            'response_type', 
            'scope',
        }
        app = {
            key: value
            for key, value in (self.app.data or {}).items()
            if key not in exclude_keys
        }

        data = app.copy()
        data['page'] = self.page
        data['pages'] = self.pages
        data['navs'] = self.navs
        data['user'] = self.user
        data['role'] = self.role
        data['business'] = self.business
        data['user_agent'] = self.user_agent.data
        data['location'] = self.location.data
        data['nation'] = self.nation.data
        
        return data
    
    @property
    def root(self) -> str:
        return self._session.get_subdomain()