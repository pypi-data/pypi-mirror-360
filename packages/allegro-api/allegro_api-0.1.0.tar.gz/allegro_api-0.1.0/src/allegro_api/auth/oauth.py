"""
OAuth2 implementation for Allegro API authentication.
"""

import time
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urlencode, urlparse, parse_qs
import webbrowser
import logging

import requests
from requests.auth import HTTPBasicAuth

from ..exceptions import AuthenticationError


logger = logging.getLogger(__name__)


@dataclass
class OAuth2Token:
    """OAuth2 token data."""
    
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    _created_at: float = None
    
    def __post_init__(self):
        if self._created_at is None:
            self._created_at = time.time()
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if self.expires_in is None:
            return False
        return time.time() > (self._created_at + self.expires_in - 60)  # 60s buffer
    
    @classmethod
    def from_response(cls, response_data: Dict[str, Any]) -> "OAuth2Token":
        """Create token from OAuth2 response."""
        return cls(
            access_token=response_data["access_token"],
            token_type=response_data.get("token_type", "Bearer"),
            expires_in=response_data["expires_in"],
            refresh_token=response_data.get("refresh_token"),
            scope=response_data.get("scope"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "_created_at": self._created_at,
        }


class OAuth2Client:
    """OAuth2 client for Allegro API authentication."""
    
    AUTHORIZATION_URL = "https://allegro.pl/auth/oauth/authorize"
    TOKEN_URL = "https://allegro.pl/auth/oauth/token"
    DEVICE_URL = "https://allegro.pl/auth/oauth/device"
    
    SANDBOX_AUTHORIZATION_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth/authorize"
    SANDBOX_TOKEN_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth/token"
    SANDBOX_DEVICE_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth/device"
    
    def __init__(
        self,
        client_id: str,
        client_secret: Optional[str] = None,
        redirect_uri: str = "http://localhost:8000",
        sandbox: bool = False,
    ):
        """
        Initialize OAuth2 client.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret (required for web apps)
            redirect_uri: Redirect URI for authorization code flow
            sandbox: Whether to use sandbox environment
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.sandbox = sandbox
        
        # Set appropriate URLs based on environment
        if sandbox:
            self.authorization_url = self.SANDBOX_AUTHORIZATION_URL
            self.token_url = self.SANDBOX_TOKEN_URL
            self.device_url = self.SANDBOX_DEVICE_URL
        else:
            self.authorization_url = self.AUTHORIZATION_URL
            self.token_url = self.TOKEN_URL
            self.device_url = self.DEVICE_URL
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Get authorization URL for web flow.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        
        if state:
            params["state"] = state
        
        return f"{self.authorization_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> OAuth2Token:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code
            
        Returns:
            OAuth2Token object
            
        Raises:
            AuthenticationError: If token exchange fails
        """
        if not self.client_secret:
            raise AuthenticationError("Client secret required for authorization code flow")
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
            )
            response.raise_for_status()
            return OAuth2Token.from_response(response.json())
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Token exchange failed: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> OAuth2Token:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New OAuth2Token object
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        if not self.client_secret:
            raise AuthenticationError("Client secret required for token refresh")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
            )
            response.raise_for_status()
            return OAuth2Token.from_response(response.json())
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    def device_flow_start(self) -> Dict[str, Any]:
        """
        Start device flow authentication.
        
        Returns:
            Device flow response with device_code, user_code, verification_uri, etc.
            
        Raises:
            AuthenticationError: If device flow initialization fails
        """
        data = {"client_id": self.client_id}
        
        try:
            response = requests.post(self.device_url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Device flow start failed: {str(e)}")
    
    def device_flow_poll(self, device_code: str) -> OAuth2Token:
        """
        Poll for device flow token.
        
        Args:
            device_code: Device code from device_flow_start
            
        Returns:
            OAuth2Token when authorization is complete
            
        Raises:
            AuthenticationError: If polling fails or times out
        """
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
        }
        
        if self.client_secret:
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
        else:
            data["client_id"] = self.client_id
            auth = None
        
        try:
            response = requests.post(self.token_url, data=data, auth=auth)
            
            if response.status_code == 400:
                error_data = response.json()
                error = error_data.get("error")
                
                if error == "authorization_pending":
                    raise AuthenticationError("Authorization pending", status_code=400)
                elif error == "slow_down":
                    raise AuthenticationError("Slow down", status_code=400)
                elif error == "access_denied":
                    raise AuthenticationError("Access denied by user", status_code=400)
                elif error == "expired_token":
                    raise AuthenticationError("Device code expired", status_code=400)
                else:
                    raise AuthenticationError(f"Device flow error: {error}", status_code=400)
            
            response.raise_for_status()
            return OAuth2Token.from_response(response.json())
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError):
                raise
            raise AuthenticationError(f"Device flow poll failed: {str(e)}")
    
    def authenticate_with_device_flow(self, open_browser: bool = True) -> OAuth2Token:
        """
        Complete device flow authentication.
        
        Args:
            open_browser: Whether to automatically open browser
            
        Returns:
            OAuth2Token
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Start device flow
        device_response = self.device_flow_start()
        
        device_code = device_response["device_code"]
        user_code = device_response["user_code"]
        verification_uri = device_response["verification_uri"]
        verification_uri_complete = device_response.get("verification_uri_complete")
        expires_in = device_response["expires_in"]
        interval = device_response.get("interval", 5)
        
        print(f"\nTo authenticate, visit: {verification_uri}")
        print(f"And enter code: {user_code}")
        
        if verification_uri_complete:
            print(f"\nOr visit: {verification_uri_complete}")
        
        if open_browser and verification_uri_complete:
            webbrowser.open(verification_uri_complete)
        
        # Poll for token
        print("\nWaiting for authorization...")
        start_time = time.time()
        
        while time.time() - start_time < expires_in:
            try:
                token = self.device_flow_poll(device_code)
                print("Authorization successful!")
                return token
            except AuthenticationError as e:
                if "Authorization pending" in str(e):
                    time.sleep(interval)
                    continue
                elif "Slow down" in str(e):
                    interval += 5
                    time.sleep(interval)
                    continue
                else:
                    raise
        
        raise AuthenticationError("Device flow authentication timed out")
    
    def client_credentials_flow(self) -> OAuth2Token:
        """
        Get token using client credentials flow (for server-to-server).
        
        Returns:
            OAuth2Token
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if not self.client_secret:
            raise AuthenticationError("Client secret required for client credentials flow")
        
        data = {"grant_type": "client_credentials"}
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
            )
            response.raise_for_status()
            return OAuth2Token.from_response(response.json())
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Client credentials flow failed: {str(e)}")