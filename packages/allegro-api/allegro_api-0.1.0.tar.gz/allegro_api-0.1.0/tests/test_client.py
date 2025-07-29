"""
Tests for main Allegro API client.
"""

import pytest
from unittest.mock import Mock, patch

from allegro_api import AllegroAPI
from allegro_api.auth import OAuth2Token, OAuth2Client
from allegro_api.exceptions import AuthenticationError
from allegro_api.resources import OffersResource, CategoriesResource, OrdersResource, UserResource


class TestAllegroAPI:
    """Test AllegroAPI client."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        api = AllegroAPI(
            client_id="test_client_id",
            client_secret="test_client_secret",
            access_token="test_token",
            refresh_token="refresh_token",
            sandbox=False,
        )
        
        assert api.client_id == "test_client_id"
        assert api.client_secret == "test_client_secret"
        assert api.access_token == "test_token"
        assert api.refresh_token == "refresh_token"
        assert not api.sandbox
        assert api.base_url == AllegroAPI.API_BASE_URL
        assert api.oauth_client is not None
        
        # Check resources initialization
        assert isinstance(api.offers, OffersResource)
        assert isinstance(api.categories, CategoriesResource)
        assert isinstance(api.orders, OrdersResource)
        assert isinstance(api.user, UserResource)
    
    def test_sandbox_initialization(self):
        """Test sandbox environment initialization."""
        api = AllegroAPI(sandbox=True)
        
        assert api.sandbox
        assert api.base_url == AllegroAPI.SANDBOX_API_BASE_URL
    
    def test_initialization_with_token_only(self):
        """Test initialization with access token only."""
        api = AllegroAPI(access_token="test_token")
        
        assert api.access_token == "test_token"
        assert api._token is not None
        assert api._token.access_token == "test_token"
        assert api.oauth_client is None  # No OAuth client without client_id
    
    @patch.object(OAuth2Client, "authenticate_with_device_flow")
    def test_authenticate_device_flow(self, mock_device_flow):
        """Test device flow authentication."""
        mock_token = OAuth2Token(
            access_token="new_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="new_refresh_token",
        )
        mock_device_flow.return_value = mock_token
        
        api = AllegroAPI(client_id="test_client_id")
        token = api.authenticate(method="device", open_browser=False)
        
        assert token == mock_token
        assert api.access_token == "new_token"
        assert api.refresh_token == "new_refresh_token"
        mock_device_flow.assert_called_once_with(False)
    
    @patch.object(OAuth2Client, "exchange_code_for_token")
    def test_authenticate_code_flow(self, mock_exchange):
        """Test authorization code flow authentication."""
        mock_token = OAuth2Token(
            access_token="new_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="new_refresh_token",
        )
        mock_exchange.return_value = mock_token
        
        api = AllegroAPI(
            client_id="test_client_id",
            client_secret="test_client_secret",
        )
        token = api.authenticate(method="code", code="test_code")
        
        assert token == mock_token
        assert api.access_token == "new_token"
        assert api.refresh_token == "new_refresh_token"
        mock_exchange.assert_called_once_with("test_code")
    
    def test_authenticate_without_code(self):
        """Test code flow without authorization code."""
        api = AllegroAPI(client_id="test_client_id")
        
        with pytest.raises(ValueError, match="Authorization code required"):
            api.authenticate(method="code")
    
    def test_authenticate_invalid_method(self):
        """Test authentication with invalid method."""
        api = AllegroAPI(client_id="test_client_id")
        
        with pytest.raises(ValueError, match="Invalid authentication method"):
            api.authenticate(method="invalid")
    
    def test_authenticate_without_oauth_client(self):
        """Test authentication without OAuth client."""
        api = AllegroAPI()
        
        with pytest.raises(ValueError, match="OAuth2 client not initialized"):
            api.authenticate()
    
    @patch.object(OAuth2Client, "refresh_token")
    def test_refresh_access_token(self, mock_refresh):
        """Test refreshing access token."""
        mock_token = OAuth2Token(
            access_token="refreshed_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="new_refresh_token",
        )
        mock_refresh.return_value = mock_token
        
        api = AllegroAPI(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="old_refresh_token",
        )
        
        token = api.refresh_access_token()
        
        assert token == mock_token
        assert api.access_token == "refreshed_token"
        assert api.refresh_token == "new_refresh_token"
        mock_refresh.assert_called_once_with("old_refresh_token")
    
    def test_refresh_without_refresh_token(self):
        """Test refresh without refresh token."""
        api = AllegroAPI(access_token="test_token")
        
        with pytest.raises(ValueError, match="No refresh token available"):
            api.refresh_access_token()
    
    def test_ensure_authenticated_valid_token(self):
        """Test ensure_authenticated with valid token."""
        api = AllegroAPI(access_token="test_token")
        api._token = OAuth2Token(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
        )
        
        # Should not raise
        api.ensure_authenticated()
    
    def test_ensure_authenticated_no_token(self):
        """Test ensure_authenticated without token."""
        api = AllegroAPI()
        
        with pytest.raises(AuthenticationError, match="Not authenticated"):
            api.ensure_authenticated()
    
    @patch.object(AllegroAPI, "refresh_access_token")
    def test_ensure_authenticated_expired_token(self, mock_refresh):
        """Test ensure_authenticated with expired token."""
        api = AllegroAPI(
            client_id="test_client_id",
            access_token="expired_token",
            refresh_token="refresh_token",
        )
        api._token = OAuth2Token(
            access_token="expired_token",
            token_type="Bearer",
            expires_in=1,
            _created_at=0,  # Very old token
        )
        
        api.ensure_authenticated()
        
        mock_refresh.assert_called_once()
    
    @patch.object(AllegroAPI, "get")
    def test_search_offers(self, mock_get):
        """Test search_offers convenience method."""
        mock_get.return_value = {"offers": []}
        
        api = AllegroAPI()
        result = api.search_offers(
            phrase="test",
            category_id="123",
            seller_id="456",
            parameters={"brand": "Test"},
            sort="price",
            include=["delivery"],
            exclude=["description"],
            limit=50,
            offset=10,
        )
        
        mock_get.assert_called_once_with(
            "/offers/listing",
            params={
                "phrase": "test",
                "category.id": "123",
                "seller.id": "456",
                "brand": "Test",
                "sort": "price",
                "include": "delivery",
                "exclude": "description",
                "limit": 50,
                "offset": 10,
            }
        )
    
    @patch.object(AllegroAPI, "get")
    def test_get_offer(self, mock_get):
        """Test get_offer convenience method."""
        mock_get.return_value = {"id": "123"}
        
        api = AllegroAPI()
        result = api.get_offer("123")
        
        mock_get.assert_called_once_with("/offers/123")
    
    @patch.object(AllegroAPI, "get")
    def test_get_user_offers(self, mock_get):
        """Test get_user_offers convenience method."""
        mock_get.return_value = {"offers": []}
        
        api = AllegroAPI(access_token="test_token")
        api._token = OAuth2Token(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
        )
        
        result = api.get_user_offers(
            offer_id="123",
            name="test",
            selling_format="BUY_NOW",
            publication_status=["ACTIVE"],
            selling_status=["ACTIVE"],
            external_id="ext123",
            limit=30,
            offset=5,
            sort="-startTime",
        )
        
        mock_get.assert_called_once_with(
            "/sale/offers",
            params={
                "offer.id": "123",
                "name": "test",
                "sellingMode.format": "BUY_NOW",
                "publication.status": ["ACTIVE"],
                "sellingMode.status": ["ACTIVE"],
                "external.id": "ext123",
                "limit": 30,
                "offset": 5,
                "sort": "-startTime",
            }
        )
    
    def test_get_authorization_url(self):
        """Test get_authorization_url method."""
        api = AllegroAPI(
            client_id="test_client_id",
            redirect_uri="http://localhost:8000",
        )
        
        url = api.get_authorization_url(state="test_state")
        
        assert "https://allegro.pl/auth/oauth/authorize" in url
        assert "client_id=test_client_id" in url
        assert "state=test_state" in url