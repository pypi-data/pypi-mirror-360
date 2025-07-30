from abc import ABC, abstractmethod
from typing import Union



class BaseDataxMigration(ABC):
    
    @abstractmethod
    def migrate(self) -> Union[str, None]:
        pass
        
    @abstractmethod
    def reverse(self) -> Union[str, None]:
        pass
        
