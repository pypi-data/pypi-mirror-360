"""
Offers resource for Allegro API.
"""

from typing import Dict, Any, List, Optional, Union
import json

from .base import BaseResource


class OffersResource(BaseResource):
    """Resource for managing offers."""
    
    def list(
        self,
        offer_id: Optional[str] = None,
        name: Optional[str] = None,
        selling_format: Optional[str] = None,
        publication_status: Optional[List[str]] = None,
        selling_status: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List user's offers.
        
        Args:
            offer_id: Filter by offer ID
            name: Filter by name
            selling_format: Filter by format (BUY_NOW, AUCTION, ADVERTISEMENT)
            publication_status: Filter by publication status
            selling_status: Filter by selling status
            external_id: Filter by external ID
            limit: Number of results (max 1000)
            offset: Results offset
            sort: Sort order
            
        Returns:
            Offers list response
        """
        self._ensure_authenticated()
        
        params = {
            "offer.id": offer_id,
            "name": name,
            "sellingMode.format": selling_format,
            "external.id": external_id,
            "limit": min(limit, 1000),
            "offset": offset,
            "sort": sort,
        }
        
        # Handle list parameters
        if publication_status:
            params["publication.status"] = publication_status
        if selling_status:
            params["sellingMode.status"] = selling_status
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/offers", params=params)
    
    def get(self, offer_id: str) -> Dict[str, Any]:
        """
        Get offer details.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Offer details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/offers/{offer_id}")
    
    def create(self, offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new offer.
        
        Args:
            offer_data: Offer data
            
        Returns:
            Created offer response
        """
        self._ensure_authenticated()
        return self.client.post("/sale/offers", json_data=offer_data)
    
    def update(self, offer_id: str, offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing offer.
        
        Args:
            offer_id: Offer ID
            offer_data: Updated offer data
            
        Returns:
            Updated offer response
        """
        self._ensure_authenticated()
        return self.client.put(f"/sale/offers/{offer_id}", json_data=offer_data)
    
    def patch(
        self,
        offer_id: str,
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Partially update offer using JSON Patch.
        
        Args:
            offer_id: Offer ID
            operations: List of patch operations
            
        Returns:
            Patched offer response
        """
        self._ensure_authenticated()
        
        headers = {
            "Content-Type": "application/vnd.allegro.public.v1+json",
        }
        
        return self.client.patch(
            f"/sale/offers/{offer_id}",
            json_data=operations,
            headers=headers,
        )
    
    def delete(self, offer_id: str) -> None:
        """
        End offer.
        
        Args:
            offer_id: Offer ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/offers/{offer_id}")
    
    def publish(self, offer_id: str) -> Dict[str, Any]:
        """
        Publish draft offer.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Publication response
        """
        self._ensure_authenticated()
        return self.client.put(f"/sale/offer-publication-commands/{offer_id}")
    
    def unpublish(self, offer_id: str) -> Dict[str, Any]:
        """
        Unpublish offer.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Unpublication response
        """
        self._ensure_authenticated()
        return self.client.delete(f"/sale/offer-publication-commands/{offer_id}")
    
    def get_events(
        self,
        from_: Optional[str] = None,
        type_: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get offer events.
        
        Args:
            from_: Event ID to start from
            type_: Event types to filter
            limit: Number of events (max 1000)
            
        Returns:
            Events response
        """
        self._ensure_authenticated()
        
        params = {
            "from": from_,
            "type": type_,
            "limit": min(limit, 1000),
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/offer-events", params=params)
    
    def get_quantity(self, offer_id: str) -> Dict[str, Any]:
        """
        Get offer quantity.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Quantity information
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/offers/{offer_id}/quantity")
    
    def update_quantity(
        self,
        offer_id: str,
        quantity: int,
        operation: str = "set"
    ) -> Dict[str, Any]:
        """
        Update offer quantity.
        
        Args:
            offer_id: Offer ID
            quantity: New quantity
            operation: Operation type (set, increase, decrease)
            
        Returns:
            Updated quantity response
        """
        self._ensure_authenticated()
        
        data = {
            "quantity": quantity,
            "operation": operation,
        }
        
        return self.client.put(
            f"/sale/offers/{offer_id}/quantity",
            json_data=data,
        )
    
    def get_price(self, offer_id: str) -> Dict[str, Any]:
        """
        Get offer price.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Price information
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/offers/{offer_id}/price")
    
    def update_price(
        self,
        offer_id: str,
        amount: float,
        currency: str = "PLN"
    ) -> Dict[str, Any]:
        """
        Update offer price.
        
        Args:
            offer_id: Offer ID
            amount: New price amount
            currency: Price currency
            
        Returns:
            Updated price response
        """
        self._ensure_authenticated()
        
        data = {
            "amount": str(amount),
            "currency": currency,
        }
        
        return self.client.put(
            f"/sale/offers/{offer_id}/price",
            json_data=data,
        )
    
    def create_from_product(
        self,
        product_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create offer from product.
        
        Args:
            product_id: Product ID
            parameters: Product parameters
            **kwargs: Additional offer fields
            
        Returns:
            Created offer response
        """
        self._ensure_authenticated()
        
        data = {
            "product": {
                "id": product_id,
            }
        }
        
        if parameters:
            data["product"]["parameters"] = parameters
        
        # Add any additional fields
        data.update(kwargs)
        
        return self.client.post("/sale/product-offers", json_data=data)
    
    def batch_update(
        self,
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch update multiple offers.
        
        Args:
            operations: List of update operations
            
        Returns:
            Batch operation response
        """
        self._ensure_authenticated()
        
        data = {"operations": operations}
        
        return self.client.post("/sale/offer-modifications", json_data=data)
    
    def get_batch_status(self, command_id: str) -> Dict[str, Any]:
        """
        Get batch operation status.
        
        Args:
            command_id: Command ID from batch operation
            
        Returns:
            Status response
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/offer-modifications/{command_id}")
    
    def get_promotions(self, offer_id: str) -> Dict[str, Any]:
        """
        Get offer promotions.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Promotions information
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/offers/{offer_id}/promotions")
    
    def get_tags(self, offer_id: str) -> Dict[str, Any]:
        """
        Get offer tags.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Tags information
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/offers/{offer_id}/tags")
    
    def update_tags(self, offer_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Update offer tags.
        
        Args:
            offer_id: Offer ID
            tags: List of tag IDs
            
        Returns:
            Updated tags response
        """
        self._ensure_authenticated()
        
        data = {"tags": [{"id": tag} for tag in tags]}
        
        return self.client.put(f"/sale/offers/{offer_id}/tags", json_data=data)