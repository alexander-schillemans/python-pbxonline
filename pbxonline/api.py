import requests
import json
from typing import Tuple, Optional, Literal
import re

from . import config
from .auth_handler import AuthHandler
from .cache_handler import CacheHandler

from pbxonline.endpoints.pbx import PBXEndpoint
from pbxonline.endpoints.action import ActionEndpoint

class PBXOnlineAPI:

    def __init__(self, api_id: str, api_key: str) -> None:
        """ Initializes the PBXOnlineAPI class. 
        
        :param api_id: the API ID to use for authentication.
        :type api_id: str
        :param api_key: the API key to use for authentication.
        :type api_key: str
        :param test_mode: whether to use the test environment for the API or not. Default False.
        :type test_mode: bool
        """
        
        self._api_id = api_id
        self._api_key = api_key
        
        self._base_url = config.BASE_URL
        self._headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json' }
        self._cache_handler = CacheHandler(fail_silently=True)
        
        self._auth_handler = AuthHandler(self)
        self._access_token = None
        
        self.pbx = PBXEndpoint(self)
        self.action = ActionEndpoint(self)
        
    def _set_token_header(self, token: str) -> None:
        """ Sets the Authorization Bearer token for the next requests. """
        
        self._access_token = token
        self._headers.update({'Authorization' : f'Bearer {token}' })
    
    def _check_header_tokens(self) -> None:
        """ Checks if a token is present in the headers. If not, request one and add to the headers."""
        
        if not self._access_token or not 'Authorization' in self._headers:
            auth_tokens = self._auth_handler.get_tokens()
            self._set_token_header(auth_tokens.get('token'))

    def _update_headers(self, headers: dict) -> dict:
        """ Takes the initial headers and updates it with the given headers. Returns the updated headers. 
        
        :param headers: the headers to update the initial headers with.
        :type headers: dict
        :return: the updated headers.
        :rtype: dict
        """
        
        tmp_headers = self._headers.copy()
        tmp_headers.update(headers)
        return tmp_headers

    def _parse_response_content(self, response: requests.Response) -> dict | str:
        """ Parses the response content to a dict if the response is JSON, otherwise returns the response content as a string. """
        
        response_type = response.headers.get('Content-Type', '')
        response_content_decoded = response.content.decode('utf-8')
        
        # Remove the first part of the response if it's not JSON
        # Sometimes the API returns a response that starts with html. To get a valid JSON response, we need to remove the html part.
        resp_content = response_content_decoded[response_content_decoded.find('{'):]
        
        # If the response is JSON, parse it to a dict
        resp_content = json.loads(resp_content) if 'text/json' in response_type else resp_content
        
        return resp_content

    def _do_request(self, method: Literal['GET', 'POST', 'PUT'], url: str, data: Optional[dict] = None, headers: Optional[dict] = None, prepend_base_to_url: Optional[bool] = True) -> requests.Response:
        """ Makes a request to the given url, with the given method and data; updates headers with new values if given.
        By default, the BASE_URL is prepended to the URL. If the arg "prepend_base_to_url" is set to False, it will not be prepended.
        
        :param method: the HTTP method to use for the request.
        :type method: Literal['GET', 'POST', 'PUT']
        :param url: the URL to make the request to.
        :type url: str
        :param data: the data to send with the request. Default None.
        :type data: Optional[dict]
        :param headers: the headers to send with the request. Default None.
        :type headers: Optional[dict]
        :param prepend_base_to_url: whether to prepend the BASE_URL to the URL. Default True.
        :type prepend_base_to_url: Optional[bool]
        :return: the response from the request.
        :rtype: requests.Response
        """
        
        headers = self._update_headers(headers) if headers else self._headers

        if prepend_base_to_url:
            request_url = f'{self._base_url}/{url}'
        else:
            request_url = url

        if method == 'GET':
            response = requests.get(request_url, params=data, headers=headers)
        elif method == 'POST':
            response = requests.post(request_url, data=json.dumps(data), headers=headers)
        elif method == 'PUT':
            response = requests.put(request_url, data=json.dumps(data), headers=headers)
        elif method == 'DELETE':
            response = requests.delete(request_url, data=json.dumps(data), headers=headers)
        
        return response


    def _request(self, method: Literal['GET', 'POST', 'PUT', 'DELETE'], url: str, data: Optional[dict] = None, headers: Optional[dict] = None, **kwargs: dict) -> Tuple[int, dict, dict]:
        """ Checks the header tokens and then carries out the request.
        Returns the status code, returned headers and content. 
        
        :param method: the HTTP method to use for the request.
        :type method: Literal['GET', 'POST', 'PUT']
        :param url: the URL to make the request to.
        :type url: str
        :param data: the data to send with the request. Default None.
        :type data: Optional[dict]
        :param headers: the headers to send with the request. Default None.
        :type headers: Optional[dict]
        :return: the status code, returned headers and content.
        :rtype: Tuple[int, dict, dict]
        """
        
        # Check the headers for appropriate tokens before we make a request
        self._check_header_tokens()

        # Make the request
        response = self._do_request(method, url, data, headers, **kwargs)
        resp_content = self._parse_response_content(response)
        
        # Unauthorized, token is not valid anymore
        if response.status_code == 401:
            
            # Force new tokens
            self._auth_handler.refresh_tokens()
            
            # Resend request after forcing new tokens
            response = self._do_request(method, url, data, headers, **kwargs)
            resp_content = self._parse_response_content(response)
            
        return response.status_code, response.headers, resp_content
    
    def get(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, **kwargs: dict) -> Tuple[int, dict, dict]:
        """ Makes a GET request to the given URL, with the given data and headers. """
        status, headers, response = self._request('GET', url, data, headers, **kwargs)
        return status, headers, response
    
    def post(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, **kwargs: dict) -> Tuple[int, dict, dict]:
        """ Makes a POST request to the given URL, with the given data and headers. """
        status, headers, response = self._request('POST', url, data, headers, **kwargs)
        return status, headers, response
    
    def put(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, **kwargs: dict) -> Tuple[int, dict, dict]:
        """ Makes a PUT request to the given URL, with the given data and headers. """
        status, headers, response = self._request('PUT', url, data, headers, **kwargs)
        return status, headers, response
    
    def delete(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, **kwargs: dict) -> Tuple[int, dict, dict]:
        """ Makes a DELETE request to the given URL, with the given data and headers. """
        status, headers, response = self._request('DELETE', url, data, headers, **kwargs)
        return status, headers, response