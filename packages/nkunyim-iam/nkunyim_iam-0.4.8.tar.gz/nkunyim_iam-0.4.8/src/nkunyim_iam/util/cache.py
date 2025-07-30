
from typing import Union
from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS,  caches

from nkunyim_iam.util.location import Location
from nkunyim_iam.util.nation import Nation
from nkunyim_iam.util.useragent import UserAgent



class CacheManager:
    """
    A simple cache manager to handle caching operations.
    """

    def __init__(self, cache_alias: str = DEFAULT_CACHE_ALIAS) -> None:
        self.cache = caches[cache_alias]


    def set(self, key, value, timeout=None):
        """
        Set a value in the cache.
        
        :param key: The key under which the value is stored.
        :param value: The value to store.
        :param timeout: The time in seconds before the cache expires.
        """
        if self.cache:
            self.cache.set(key, value, timeout)


    def get(self, key):
        """
        Get a value from the cache.
        
        :param key: The key of the cached value.
        :return: The cached value or None if not found.
        """
        if self.cache:
            return self.cache.get(key)
        return None


    def delete(self, key):
        """
        Delete a value from the cache.
        
        :param key: The key of the cached value to delete.
        """
        if self.cache:
            self.cache.delete(key)
            
            
    def clear(self):
        """
        Clear the entire cache.
        """
        if self.cache:
            self.cache.clear()
            
            
class UserAgentCache:
    """
    A cache manager specifically for user agent data.
    """

    def __init__(self) -> None:
        """
        Initialize the UserAgentCache with the user agents cache alias.
        """
        self.cache = CacheManager(settings.USER_AGENTS_CACHE if hasattr(settings, 'USER_AGENTS_CACHE') else DEFAULT_CACHE_ALIAS)    
        
    def set_user_agent(self, key: str, user_agent_data: UserAgent, timeout: int = 60 * 60 * 24):
        """
        Set user agent data in the cache.
        
        :param key: The key under which the user agent data is stored.
        :param user_agent_data: The user agent data to store.
        :param timeout: The time in seconds before the cache expires.
        """
        self.cache.set(key=key, value=user_agent_data, timeout=timeout)
        
    def get_user_agent(self, key: str) -> Union[UserAgent, None]:
        """
        Get user agent data from the cache.
        :param key: The key of the cached user agent data.
        :return: The cached user agent data or None if not found.
        """
        return self.cache.get(key=key)
    
    
    def delete_user_agent(self, key: str) -> None:
        """
        Delete user agent data from the cache.
        
        :param key: The key of the cached user agent data to delete.
        """
        self.cache.delete(key=key)
        
    def clear_user_agents(self) -> None:
        """ 
        Clear all user agent data from the cache.
        """
        self.cache.clear()
        
        
class LocationCache:
    """
    A cache manager for location caching.
    """

    def __init__(self) -> None:
        """
        Initialize the Location Cache with the location cache alias.
        """
        self.cache = CacheManager(settings.LOCATION_CACHE if hasattr(settings, 'LOCATION_CACHE') else DEFAULT_CACHE_ALIAS)
        
    def set_location(self, key: str, location_data: Location, timeout: int = 60 * 60 * 24):
        """
        Set location data in the cache.
        :param key: The key under which the location data is stored.
        :param location: The location data to store.
        :param timeout: The time in seconds before the cache expires.
        """
        self.cache.set(key=key, value=location_data, timeout=timeout)
        
    def get_location(self, key: str) -> Union[Location, None]:
        """
        Get location data from the cache.
        :param key: The key of the cached location data.
        :return: The cached location data or None if not found.
        """
        return self.cache.get(key=key)
    
    def delete_location(self, key: str) -> None:
        """
        Delete location data from the cache.
        
        :param key: The key of the cached location data to delete.
        """
        self.cache.delete(key=key)
        
    def clear_locations(self) -> None:
        """
        Clear all location data from the cache.
        """
        self.cache.clear()
        
        
    
class NationCache:
    """
    A cache manager for nation caching.
    """

    def __init__(self) -> None:
        """
        Initialize the NaTion Cache with the nation cache alias.
        """
        self.cache = CacheManager(settings.NATION_CACHE if hasattr(settings, 'NATION_CACHE') else DEFAULT_CACHE_ALIAS)
        
    def set_nation(self, key: str, nation_data: Nation, timeout: int = 60 * 60 * 24):
        """
        Set nation data in the cache.
        :param key: The key under which the nation data is stored.
        :param nation: The nation data to store.
        :param timeout: The time in seconds before the cache expires.
        """
        self.cache.set(key=key, value=nation_data, timeout=timeout)
        
    def get_nation(self, key: str) -> Union[Nation, None]:
        """
        Get nation data from the cache.
        :param key: The key of the cached nation data.
        :return: The cached nation data or None if not found.
        """
        return self.cache.get(key=key)
    
    def delete_nation(self, key: str) -> None:
        """
        Delete nation data from the cache.
        
        :param key: The key of the cached nation data to delete.
        """
        self.cache.delete(key=key)
        
    def clear_nations(self) -> None:
        """
        Clear all nation data from the cache.
        """
        self.cache.clear()