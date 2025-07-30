from django.contrib.gis.geoip2 import GeoIP2
from django.http import HttpRequest


class Location(object):
    """
    A class to get the geographical location of a user based on their IP address.    
    This class uses the GeoIP2 database to retrieve location data such as city, country, latitude, longitude, etc.
    It is designed to be used in a Django application, and it extracts the user's IP address from the HTTP request.
    The class provides properties to access various location attributes such as city, country code, latitude, longitude, etc.
    It also includes a method to return the raw data from the GeoIP2 database.
    """
    
    def __init__(self, req: HttpRequest) -> None:
        # https://docs.djangoproject.com/en/5.2/ref/contrib/gis/geoip2/
        
        x_forwarded_for = str(req.META.get('HTTP_X_FORWARDED_FOR'))
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        elif req.META.get('HTTP_X_REAL_IP'):
            ip = str(req.META.get('HTTP_X_REAL_IP')).strip()
        else:
            ip = str(req.META.get('REMOTE_ADDR')).strip()
     
            
        # IP Address
        if ip.startswith("192.168.") or ip.endswith(".0.0.1"):
            ip = "154.160.22.132"

        g = GeoIP2()
        
        self._data = g.city(ip)
        self._user_ip = ip
        

    @property
    def user_ip(self) -> str:
        """
        Returns the IP address of the user.
        If the IP address is a private IP address,
        it returns a default IP address.
        """
        return str(self._user_ip)
    
    @property
    def data(self) -> dict:
        """Returns the geo data of the user."""
        return self._data
    
    @property
    def accuracy_radius(self) -> int:
        """
        Returns the accuracy radius of the location.
        The accuracy radius is the radius of the circle around the location
        that contains the location with a certain level of confidence.
        It is expressed in meters.
        For example, if the accuracy radius is 1000 meters,
        it means that the location is accurate within a circle of 1000 meters radius.
        This property returns the accuracy radius as an integer.
        """
        return int(self.data['accuracy_radius'])

    @property
    def city(self):
        """Returns the city of the location."""
        return str(self.data['city'])
        
    @property
    def continent_code(self) -> str:
        """
        Returns the continent code of the location.
        For example, 'EU' for Europe, 'NA' for North America.
        This is a two-letter code.
        """
        return str(self.data['continent_code'])
        
    @property
    def continent_name(self) -> str:
        """
        Returns the continent name of the location.
        For example, 'Europe', 'North America', etc.
        This is the full name of the continent.
        """
        return str(self.data['continent_name'])
        
    @property
    def country_code(self) -> str:
        """
        Returns the country code of the location.
        For example, 'US' for United States, 'GB' for United Kingdom.
        This is a two-letter code.
        """
        return str(self.data['country_code'])
        
    @property
    def country_name(self) -> str:
        """
        Returns the country name of the location.
        For example, 'United States', 'United Kingdom', etc.
        This is the full name of the country.
        """
        return str(self.data['country_name'])
        
    @property
    def is_in_eu(self) -> bool:
        """Returns True if the location is in the European Union, False otherwise."""
        return bool(self.data['is_in_european_union'])
        
    @property
    def latitude(self) -> float:
        """
        Returns the latitude of the location.
        Latitude is the geographic coordinate that specifies the north-south position of a point on the Earth's surface.
        It is expressed in degrees, with positive values indicating locations north of the equator and negative values indicating locations south of the equator.
        Latitude ranges from -90 degrees at the South Pole to +90 degrees at the North Pole.
        For example, the latitude of London, UK is approximately 51.5074° N.
        This property returns the latitude as a float.
        """
        return float(self.data['latitude'])
        
    @property
    def longitude(self) -> float:
        """
        Returns the longitude of the location.
        Longitude is the geographic coordinate that specifies the east-west position of a point on the Earth's surface.
        It is expressed in degrees, with positive values indicating locations east of the Prime Meridian and negative values indicating locations west of the Prime Meridian.
        Longitude ranges from -180 degrees at the International Date Line to +180 degrees at the opposite side of the globe.
        For example, the longitude of London, UK is approximately -0.1278° W.
        This property returns the longitude as a float.
        """
        return float(self.data['longitude'])
        
    @property
    def metro_code(self) -> str:
        """
        Returns the metro code of the location.
        The metro code is a code that represents a metropolitan area.
        It is often used to identify a specific urban area or region.
        For example, the metro code for New York City is 'NYC'.
        This property returns the metro code as a string.
        """
        return str(self.data['metro_code'])
        
    @property
    def postal_code(self) -> str:
        """
        Returns the postal code of the location.
        The postal code is a code used by postal services to identify specific geographic areas for mail delivery.
        It is often used to identify a specific area within a city or town.
        For example, the postal code for London, UK is 'EC1A 1BB'.
        This property returns the postal code as a string.
        """
        return str(self.data['postal_code'])
        
    @property
    def region_code(self) -> str:
        """
        Returns the region code of the location.
        The region code is a code that represents a specific region within a country.
        It is often used to identify a specific area within a country or a group of countries.
        For example, the region code for California in the United States is 'CA'.
        This property returns the region code as a string.
        """
        return str(self.data['region_code'])
        
    @property
    def region_name(self) -> str:
        """
        Returns the region name of the location.
        The region name is a broader geographical area that can encompass multiple countries.
        It is often used to refer to a specific part of a country or a group of countries
        that share common cultural, historical, or geographical characteristics.
        For example, 'California' is a region that includes multiple cities such as Los Angeles and San Francisco.
        This property returns the region name as a string.
        """
        return str(self.data['region_name'])
        
    @property
    def time_zone(self) -> str:
        """
        Returns the time zone of the location.
        The time zone is a region of the Earth that has the same standard time.
        It is often used to determine the local time in a specific area.
        For example, 'America/New_York' is a time zone that represents the Eastern Time Zone in the United States.
        This property returns the time zone as a string.
        """
        return str(self.data['time_zone'])
        
    @property
    def dma_code(self) -> str:
        """
        Returns the DMA code of the location.
        The DMA (Designated Market Area) code is a code that represents a specific television market area.
        It is often used in the United States to identify specific regions for television broadcasting and advertising purposes.
        For example, the DMA code for New York City is '501'.
        This property returns the DMA code as a string.
        """
        return str(self.data['dma_code'])
        
    @property
    def region(self) -> str:
        """Returns the region of the location.
        The region is a broader geographical area that can encompass multiple countries.
        It is often used to refer to a specific part of a country or a group of countries
        that share common cultural, historical, or geographical characteristics.
        For example, 'Europe' is a region that includes multiple countries such as France, Germany, and Italy.
        This property returns the region as a string.
        """
        return str(self.data['region'])
