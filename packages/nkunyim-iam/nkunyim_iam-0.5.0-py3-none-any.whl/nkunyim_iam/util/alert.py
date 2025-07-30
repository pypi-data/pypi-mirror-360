from typing import Any, Union


ALERT_TYPE_DEBUG = "debug"
ALERT_TYPE_INFO = "info"
ALERT_TYPE_NOTICE = "notice"
ALERT_TYPE_SUCCESS = "success"
ALERT_TYPE_WARNING = "warning"
ALERT_TYPE_ERROR = "error"
ALERT_TYPE_CRITICAL= "critical"


class Alert(object):
    def __init__(self, msg: str, typ: Union[int, str, None] = ALERT_TYPE_DEBUG, ctx: Union[dict, None] = None) -> None:
        """A piece of information suitable for diplaying UI alerts and JS console logs

        Args:
            msg (str): This is the message to display in the UI alert of JS console.
            typ (Union[int, str, None], optional): The type or level of the message. Defaults to ALERT_TYPE_DEBUG.
            ctx (Union[dict, None], optional): Add a dictionary (if needed) of any extra context or meta data to display. Defaults to None.
        """
        self._msg: str = msg
        
        if not typ:
            typ = ALERT_TYPE_DEBUG
            
        if isinstance(typ, int):
            if typ < 0:
                typ = 0
                
            if typ > 6:
                typ = 6
                
            ALERT_TYPE_BAG: list[str] = [ALERT_TYPE_DEBUG, ALERT_TYPE_NOTICE, ALERT_TYPE_SUCCESS, ALERT_TYPE_WARNING, ALERT_TYPE_ERROR]
            typ = ALERT_TYPE_BAG[int(typ)]
            
        self._typ: str = typ
        
        self._ctx: Union[dict, None] = ctx
        
    @property
    def msg(self) -> str:
        return self._msg
    
    @property
    def typ(self) -> str:
        return self._typ
    
    @property
    def ctx(self) -> Union[dict, None]:
        return self.ctx
    
    @property
    def data(self) -> dict[str, Any]:
        return self.__dict__
