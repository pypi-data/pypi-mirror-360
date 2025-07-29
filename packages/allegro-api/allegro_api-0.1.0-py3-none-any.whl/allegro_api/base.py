"""
Base classes for Allegro API client.
"""

from typing import Optional, Dict, Any, Union
import logging
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .exceptions import (
    AllegroAPIException,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError,
)


logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base class for API clients with common HTTP functionality."""
    
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BACKOFF_FACTOR = 0.3
    
    def __init__(
        self,
        base_url: str,
        access_token: Optional[str] = None,
        sandbox: bool = False,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Initialize base API client.
        
        Args:
            base_url: Base URL for API endpoints
            access_token: OAuth2 access token
            sandbox: Whether to use sandbox environment
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retries
        """
        self.base_url = base_url
        self.access_token = access_token
        self.sandbox = sandbox
        self.timeout = timeout
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self._update_headers()
    
    def _update_headers(self) -> None:
        """Update session headers."""
        headers = {
            "Accept": "application/vnd.allegro.public.v1+json",
            "Content-Type": "application/vnd.allegro.public.v1+json",
            "Accept-Language": "pl-PL",
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        self.session.headers.update(headers)
    
    def set_access_token(self, access_token: str) -> None:
        """
        Set or update access token.
        
        Args:
            access_token: OAuth2 access token
        """
        self.access_token = access_token
        self._update_headers()
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL for endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL
        """
        return urljoin(self.base_url, endpoint.lstrip("/"))
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response object
            
        Returns:
            Response data as dictionary
            
        Raises:
            Various AllegroAPIException subclasses based on status code
        """
        try:
            response_data = response.json() if response.text else {}
        except ValueError:
            response_data = {"raw_response": response.text}
        
        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed. Check your access token.",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 403:
            raise AuthorizationError(
                "Access forbidden. Check your permissions.",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                "Resource not found.",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 422:
            raise ValidationError(
                f"Validation error: {response_data.get('message', 'Invalid request data')}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded.",
                retry_after=int(retry_after) if retry_after else None,
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code >= 500:
            raise ServerError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif not response.ok:
            raise AllegroAPIException(
                f"API error: {response.status_code}",
                status_code=response.status_code,
                response_data=response_data,
            )
        
        return response_data
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON body data
            data: Raw body data
            headers: Additional headers
            **kwargs: Additional arguments for requests
            
        Returns:
            Response data
        """
        url = self._build_url(endpoint)
        
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        logger.debug(f"{method} {url}")
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            data=data,
            headers=request_headers,
            timeout=self.timeout,
            **kwargs,
        )
        
        return self._handle_response(response)
    
    def get(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make GET request."""
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make POST request."""
        return self._request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make PUT request."""
        return self._request("PUT", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make PATCH request."""
        return self._request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._request("DELETE", endpoint, **kwargs)