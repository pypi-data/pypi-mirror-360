"""
Base resource class for API resources.
"""

from typing import TYPE_CHECKING, Dict, Any, List, Optional

if TYPE_CHECKING:
    from ..client import AllegroAPI


class BaseResource:
    """Base class for API resources."""
    
    def __init__(self, client: "AllegroAPI"):
        """
        Initialize resource.
        
        Args:
            client: AllegroAPI client instance
        """
        self.client = client
    
    def _ensure_authenticated(self) -> None:
        """Ensure client is authenticated."""
        self.client.ensure_authenticated()
    
    def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        max_pages: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Paginate through API results.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            limit: Items per page
            offset: Starting offset
            max_pages: Maximum pages to fetch
            
        Returns:
            List of all items
        """
        if params is None:
            params = {}
        
        items = []
        page = 0
        
        while True:
            page_params = params.copy()
            page_params["offset"] = offset
            if limit:
                page_params["limit"] = limit
            
            response = self.client.get(endpoint, params=page_params)
            
            # Get items from response
            page_items = response.get("offers", response.get("items", []))
            if not page_items:
                break
            
            items.extend(page_items)
            
            # Check if we have more pages
            if len(page_items) < (limit or 20):
                break
            
            page += 1
            if max_pages and page >= max_pages:
                break
            
            offset += len(page_items)
        
        return items