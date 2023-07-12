from . import config
from typing import Tuple, Optional, Literal

class AuthHandler:

    def __init__(self, api: object) -> None:
        self._api = api
        self._cache_handler = api._cache_handler
        
        self._base_url = api._base_url
        self._token_url = config.TOKEN_URL
        self._refresh_token_url = config.REFRESH_TOKEN_URL
        
        self._api_id = api._api_id
        self._api_key = api._api_key
        
        if not self._api_id or not self._api_key:
            raise ValueError('API ID and API key are required to authenticate.')
    
    def get_token_from_cache(self, token: Literal['token', 'refresh_token']) -> str:
        """ Returns the token from the cache. If not found, returns None. 
        
        :param token: the token to get from the cache.
        :type token: Literal['token', 'refresh_token']
        :return: the token from the cache or None if not found.
        :rtype: str or None
        """
        
        if token == 'refresh_token':
            token = 'refreshToken'
        
        cache = self._cache_handler.get(self._api_id)
        if cache:
            try:
                return cache.get(token)
            except KeyError:
                return None
        return None
        
    def get_tokens(self) -> str:
        """ Returns the tokens for the user. Checks the cache first. If not found, authenticates and returns the tokens. """
        
        # Check if the token is in the cache
        cached_tokens = self._cache_handler.get(self._api_id)
        if cached_tokens:
            return cached_tokens
        
        # If not, authenticate and return the token
        tokens = self._authenticate()
        return tokens
    
    def refresh_tokens(self) -> None:
        """ Refreshes the tokens for the user. Uses the refresh token from the cache. If not found, authenticates again using the API id and key. Sets the new Bearer token in the headers for the next requests. """
        
        refresh_token = self.get_token_from_cache('refresh_token')
            
        # If we have a refresh token, get a new access token with it
        if refresh_token:
            auth_tokens = self._get_tokens_from_refresh_token(refresh_token)
            
            if not auth_tokens:
                # Delete cache and get new tokens
                # This will force new tokens without the cached refresh token
                self._cache_handler.delete(self._api_id)
                auth_tokens = self.get_tokens()
        else:
            # No refresh token, get new tokens with username and password
            auth_tokens = self.get_tokens()

        # Set the new token in the headers
        self._api._set_token_header(auth_tokens.get('token'))
    
    def _make_auth_request(self, type: Literal['token', 'refresh_token'], params: dict) -> dict:
        """ Makes a request to the authentication server. """
        
        # Get the correct endpoint
        if type not in ['token', 'refresh_token']:
            raise ValueError('Type must be either "token" or "refresh_token".')
        
        endpoint = self._token_url if type == 'token' else self._refresh_token_url

        # Make the request
        response = self._api._do_request('POST', endpoint, data=params, prepend_base_to_url=False)
        response_type = response.headers.get('Content-Type')
        status_code = response.status_code
        content = response.json() if 'text/json' in response_type else response.text
        
        # Check if the request was successful
        if status_code != 200:
            return None
        
        # Write the tokens to the cache
        self._cache_handler.write(self._api_id, content)
        
        return content
    
    def _authenticate(self) -> dict:
        """ Authenticates the user and returns the tokens. """
        
        params = {
            'username' : self._api_id,
            'password' : self._api_key
        }
        
        content = self._make_auth_request(params=params, type='token')
        return content
    
    def _get_tokens_from_refresh_token(self, refresh_token: str) -> dict:
        """ Gets the tokens from a refresh token. """
        
        params = {
            'refreshToken' : refresh_token
        }

        content = self._make_auth_request(params=params, type='refresh_token')
        return content