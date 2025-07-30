from typing import Union
from user_agents.parsers import UserAgent as BaseUserAgent


class UserAgent(BaseUserAgent):
    def __init__(self, req) -> None:
        """
        Initialize the UserAgent class with a request object.
        Args:
            req: The request object containing user agent information.
        """
        ua_string = req.META.get('HTTP_USER_AGENT') or \
                    req.headers.get('User-Agent') or \
                    req.headers.get('user-agent', '')

        if isinstance(ua_string, bytes):
            ua_string = ua_string.decode('utf-8', 'ignore')

        super().__init__(ua_string)

        self._data: Union[dict, None] = {
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
        } if ua_string else None

    @property
    def data(self) -> Union[dict, None]:
        """Returns the parsed user agent data as a dictionary."""
        return self._data
