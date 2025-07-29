"""
Tests for OAuth2 authentication.
"""

import pytest
from unittest.mock import Mock, patch
import time

from allegro_api.auth import OAuth2Client, OAuth2Token
from allegro_api.exceptions import AuthenticationError


class TestOAuth2Token:
    """Test OAuth2Token class."""
    
    def test_token_creation(self):
        """Test token creation."""
        token = OAuth2Token(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh_token",
            scope="allegro:api:sale:offers:read",
        )
        
        assert token.access_token == "test_token"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600
        assert token.refresh_token == "refresh_token"
        assert token.scope == "allegro:api:sale:offers:read"
        assert token._created_at is not None
    
    def test_token_expiry(self):
        """Test token expiry check."""
        # Non-expired token
        token = OAuth2Token(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
        )
        assert not token.is_expired
        
        # Expired token
        token = OAuth2Token(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
            _created_at=time.time() - 4000,  # Created 4000 seconds ago
        )
        assert token.is_expired
    
    def test_from_response(self):
        """Test creating token from API response."""
        response_data = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "refresh_token",
            "scope": "allegro:api:sale:offers:read",
        }
        
        token = OAuth2Token.from_response(response_data)
        
        assert token.access_token == "test_token"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600
        assert token.refresh_token == "refresh_token"
        assert token.scope == "allegro:api:sale:offers:read"
    
    def test_to_dict(self):
        """Test converting token to dictionary."""
        token = OAuth2Token(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh_token",
            scope="allegro:api:sale:offers:read",
        )
        
        token_dict = token.to_dict()
        
        assert token_dict["access_token"] == "test_token"
        assert token_dict["token_type"] == "Bearer"
        assert token_dict["expires_in"] == 3600
        assert token_dict["refresh_token"] == "refresh_token"
        assert token_dict["scope"] == "allegro:api:sale:offers:read"
        assert "_created_at" in token_dict


class TestOAuth2Client:
    """Test OAuth2Client class."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = OAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000",
            sandbox=False,
        )
        
        assert client.client_id == "test_client_id"
        assert client.client_secret == "test_client_secret"
        assert client.redirect_uri == "http://localhost:8000"
        assert not client.sandbox
        assert client.authorization_url == OAuth2Client.AUTHORIZATION_URL
        assert client.token_url == OAuth2Client.TOKEN_URL
        assert client.device_url == OAuth2Client.DEVICE_URL
    
    def test_client_sandbox_urls(self):
        """Test sandbox URLs."""
        client = OAuth2Client(
            client_id="test_client_id",
            sandbox=True,
        )
        
        assert client.sandbox
        assert client.authorization_url == OAuth2Client.SANDBOX_AUTHORIZATION_URL
        assert client.token_url == OAuth2Client.SANDBOX_TOKEN_URL
        assert client.device_url == OAuth2Client.SANDBOX_DEVICE_URL
    
    def test_get_authorization_url(self):
        """Test authorization URL generation."""
        client = OAuth2Client(
            client_id="test_client_id",
            redirect_uri="http://localhost:8000",
        )
        
        # Without state
        url = client.get_authorization_url()
        assert "https://allegro.pl/auth/oauth/authorize" in url
        assert "response_type=code" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000" in url
        
        # With state
        url = client.get_authorization_url(state="test_state")
        assert "state=test_state" in url
    
    @patch("requests.post")
    def test_exchange_code_for_token(self, mock_post):
        """Test exchanging authorization code for token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "refresh_token",
        }
        mock_post.return_value = mock_response
        
        client = OAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
        )
        
        token = client.exchange_code_for_token("test_code")
        
        assert isinstance(token, OAuth2Token)
        assert token.access_token == "test_token"
        assert token.refresh_token == "refresh_token"
        
        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == client.token_url
        assert kwargs["data"]["grant_type"] == "authorization_code"
        assert kwargs["data"]["code"] == "test_code"
    
    def test_exchange_code_without_secret(self):
        """Test that exchange_code requires client secret."""
        client = OAuth2Client(client_id="test_client_id")
        
        with pytest.raises(AuthenticationError, match="Client secret required"):
            client.exchange_code_for_token("test_code")
    
    @patch("requests.post")
    def test_refresh_token(self, mock_post):
        """Test refreshing access token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "new_refresh_token",
        }
        mock_post.return_value = mock_response
        
        client = OAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
        )
        
        token = client.refresh_token("old_refresh_token")
        
        assert isinstance(token, OAuth2Token)
        assert token.access_token == "new_token"
        assert token.refresh_token == "new_refresh_token"
        
        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == client.token_url
        assert kwargs["data"]["grant_type"] == "refresh_token"
        assert kwargs["data"]["refresh_token"] == "old_refresh_token"
    
    @patch("requests.post")
    def test_device_flow_start(self, mock_post):
        """Test starting device flow."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "device_code": "test_device_code",
            "user_code": "TEST-CODE",
            "verification_uri": "https://allegro.pl/device",
            "verification_uri_complete": "https://allegro.pl/device?user_code=TEST-CODE",
            "expires_in": 600,
            "interval": 5,
        }
        mock_post.return_value = mock_response
        
        client = OAuth2Client(client_id="test_client_id")
        
        response = client.device_flow_start()
        
        assert response["device_code"] == "test_device_code"
        assert response["user_code"] == "TEST-CODE"
        assert response["verification_uri"] == "https://allegro.pl/device"
        
        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == client.device_url
        assert kwargs["data"]["client_id"] == "test_client_id"
    
    @patch("requests.post")
    def test_device_flow_poll_success(self, mock_post):
        """Test successful device flow polling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "refresh_token",
        }
        mock_post.return_value = mock_response
        
        client = OAuth2Client(client_id="test_client_id")
        
        token = client.device_flow_poll("test_device_code")
        
        assert isinstance(token, OAuth2Token)
        assert token.access_token == "test_token"
    
    @patch("requests.post")
    def test_device_flow_poll_pending(self, mock_post):
        """Test device flow polling with pending authorization."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "authorization_pending"}
        mock_post.return_value = mock_response
        
        client = OAuth2Client(client_id="test_client_id")
        
        with pytest.raises(AuthenticationError, match="Authorization pending"):
            client.device_flow_poll("test_device_code")
    
    @patch("requests.post")
    def test_client_credentials_flow(self, mock_post):
        """Test client credentials flow."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response
        
        client = OAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
        )
        
        token = client.client_credentials_flow()
        
        assert isinstance(token, OAuth2Token)
        assert token.access_token == "test_token"
        assert token.refresh_token is None  # No refresh token in client credentials
        
        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == client.token_url
        assert kwargs["data"]["grant_type"] == "client_credentials"