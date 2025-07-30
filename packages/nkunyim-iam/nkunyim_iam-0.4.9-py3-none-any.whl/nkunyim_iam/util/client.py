import requests
import base64
import json
from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.util.encryption import Encryption
from nkunyim_iam.util.session import HttpSession


class HttpClient:

    def __init__(self, req: HttpRequest, name:str) -> None:
        """Initialize the HttpClient with a request object and service name.    
        Args:
            req (HttpRequest): The request object containing user information.
            name (str): The name of the service to connect to.
        Raises:
            Exception: If the service configuration variable is not defined or if an error occurs during initialization.
        """
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            base_url = str(settings.NKUNYIM_SERVICES[name.upper()])
            if base_url.endswith('/'):
                base_url = base_url[:-1]
                
            sess = HttpSession(req=req)
            encryption = Encryption()
            
            app_data = sess.get_app_data()
            nat_data = sess.get_nat_data()
            if bool(app_data and 'name' in app_data and nat_data and 'code' in nat_data):
                appnat_data = json.dumps({
                    'app': app_data,
                    'nat': nat_data
                })
                
                appnat_cipher = encryption.rsa_encrypt(plain_text=appnat_data, name=name)
                
                appnat_token = base64.b64encode(appnat_cipher)
                headers['Xan-Authorization'] = appnat_token.decode("utf-8")
            
            user_data = sess.get_user()
            if user_data and 'id' in user_data:
                
                plain_text = json.dumps(user_data)
                cipher_text = encryption.rsa_encrypt(plain_text=plain_text, name=name)
                
                access_token = base64.b64encode(cipher_text)
                headers['Authorization'] = f"JWT {access_token.decode("utf-8")}"
                
        except KeyError as e:
            raise Exception(f"The service configuration variable {name.upper()} has not defined. Error detail: {str(e)}")

        except Exception as ex:
            raise Exception(f"Exception error occured when initializing the HttpClient. Error detail: {str(ex)}")
        
        self.base_url = base_url
        self.headers = headers


    def post(self, path: str, data: dict) -> requests.Response:
        """Send a POST request to the specified path with the given data.
        Args:
            path (str): The path to send the POST request to.
            data (dict): The data to include in the POST request.
        Returns:
            requests.Response: The response from the POST request.
        """
        url = self.get_full_url(path)
        if not url.endswith('/'):
            url += '/'
            
        return requests.post(url=url, data=data, headers=self.headers)


    def get(self, path: str) -> requests.Response:
        """Send a GET request to the specified path.
        Args:
            path (str): The path to send the GET request to.
        Returns:
            requests.Response: The response from the GET request.
        """
        url = self.get_full_url(path)
        return requests.get(url=url, headers=self.headers)


    def put(self, path: str, data: dict) -> requests.Response:
        """Send a PUT request to the specified path with the given data.
        Args:
            path (str): The path to send the PUT request to.
            data (dict): The data to include in the PUT request.
        Returns:
            requests.Response: The response from the PUT request.
        """
        url = self.get_full_url(path)
        return requests.put(url=url, data=data, headers=self.headers)


    def delete(self, path: str) -> requests.Response:
        """Send a DELETE request to the specified path.
        Args:
            path (str): The path to send the DELETE request to.
        Returns:
            requests.Response: The response from the DELETE request.
        """
        url = self.get_full_url(path)
        return requests.delete(url=url, headers=self.headers)
    
    
    def patch(self, path: str, data: dict) -> requests.Response:
        """Send a PATCH request to the specified path with the given data.
        Args:
            path (str): The path to send the PATCH request to.
            data (dict): The data to include in the PATCH request.
        Returns:
            requests.Response: The response from the PATCH request.
        """
        url = self.get_full_url(path)
        return requests.patch(url=url, data=data, headers=self.headers) 
    
    
    def head(self, path: str) -> requests.Response:
        """Send a HEAD request to the specified path.
        Args:
            path (str): The path to send the HEAD request to.
        Returns:
            requests.Response: The response from the HEAD request.
        """
        url = self.get_full_url(path)
        if not url.endswith('/'):
            url += '/'
            
        return requests.head(url=url, headers=self.headers) 
    
    
    def options(self, path: str) -> requests.Response:
        """Send an OPTIONS request to the specified path.
        Args:
            path (str): The path to send the OPTIONS request to.
        Returns:
            requests.Response: The response from the OPTIONS request.
        """
        url = self.get_full_url(path)
        if not url.endswith('/'):
            url += '/'
            
        return requests.options(url=url, headers=self.headers)
    
    
    def get_base_url(self) -> str:
        """Get the base URL of the HTTP client.
        Returns:
            str: The base URL of the HTTP client.
        """
        base_url = self.base_url
        if not base_url.endswith('api'):
            base_url += "/api"
            
        return base_url
    
    
    def get_headers(self) -> dict:
        """Get the headers of the HTTP client.
        Returns:
            dict: The headers of the HTTP client.
        """
        return self.headers 
     
     
    def get_full_url(self, path: str) -> str:
        """Get the full URL by combining the base URL and the specified path.
        Args:
            path (str): The path to append to the base URL.
        Returns:
            str: The full URL.
        """
        if not path.startswith('/'):
            path = '/' + path
            
        return self.get_base_url() + path
