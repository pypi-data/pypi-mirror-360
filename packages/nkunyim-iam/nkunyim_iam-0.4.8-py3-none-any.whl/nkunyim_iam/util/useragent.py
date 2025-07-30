from typing import Union
from user_agents.parsers import  UserAgent as BaseUserAgent


class UserAgent(BaseUserAgent):
    
    def __init__(self, req) -> None:
        
        """Initialize the UserAgent class with a request object.
        Args:
            req: The request object containing user agent information.
        """
        
        self._data: Union[dict, None] = None
        
        ua_string = req.META['HTTP_USER_AGENT']

        if not ua_string and 'User-Agent' in req.headers:
            ua_string = req.headers['User-Agent']

        if not ua_string and 'user-agent' in req.headers:
            ua_string = req.headers['user-agent']
                
        if ua_string:
            if not isinstance(ua_string, str):
                ua_string = ua_string.decode('utf-8', 'ignore')
        else:
            ua_string = ''
        
        super().__init__(ua_string)

        if ua_string not in (None, ''):
            self._data = {
                "is_mobile": self.is_mobile,
                "is_tablet": self.is_tablet,
                "is_touch_capable": self.is_touch_capable,
                "is_pc": self.is_pc,
                "is_bot": self.is_bot,
                "is_email_client": self.is_email_client,
                "browser_name": self.browser.family,
                "browser_version": self.browser.version_string,
                "os_name": self.os.family,
                "os_version": self.os.version_string,
                "device_name": self.device.family,
                "device_brand": self.device.brand,
                "device_model": self.device.model,
            }

    @property
    def data(self) -> Union[dict, None]:
        """Returns the user agent data as a dictionary."""
        return self._data
   