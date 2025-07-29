"""
Fulfillment resources for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class FulfillmentResource(BaseResource):
    """Resource for One Fulfillment operations."""
    
    # Advance Ship Notices
    def get_advance_ship_notices(
        self,
        status: Optional[str] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get advance ship notices.
        
        Args:
            status: Status filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            updated_at_gte: Filter by update date (after)
            updated_at_lte: Filter by update date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Advance ship notices response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        if created_at_gte:
            params["createdAt.gte"] = created_at_gte.isoformat()
        if created_at_lte:
            params["createdAt.lte"] = created_at_lte.isoformat()
        if updated_at_gte:
            params["updatedAt.gte"] = updated_at_gte.isoformat()
        if updated_at_lte:
            params["updatedAt.lte"] = updated_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/fulfillment/advance-ship-notices", params=params)
    
    def create_advance_ship_notice(
        self,
        items: List[Dict[str, Any]],
        labels: Optional[List[Dict[str, Any]]] = None,
        handling_unit: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create advance ship notice.
        
        Args:
            items: Items to ship
            labels: Shipping labels
            handling_unit: Handling unit information
            
        Returns:
            Created advance ship notice
        """
        self._ensure_authenticated()
        
        data = {"items": items}
        
        if labels:
            data["labels"] = labels
        if handling_unit:
            data["handlingUnit"] = handling_unit
        
        return self.client.post("/fulfillment/advance-ship-notices", json_data=data)
    
    def get_advance_ship_notice(self, notice_id: str) -> Dict[str, Any]:
        """
        Get advance ship notice details.
        
        Args:
            notice_id: Notice ID
            
        Returns:
            Notice details
        """
        self._ensure_authenticated()
        return self.client.get(f"/fulfillment/advance-ship-notices/{notice_id}")
    
    def update_advance_ship_notice(
        self,
        notice_id: str,
        items: Optional[List[Dict[str, Any]]] = None,
        labels: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update advance ship notice.
        
        Args:
            notice_id: Notice ID
            items: Updated items
            labels: Updated labels
            
        Returns:
            Updated notice
        """
        self._ensure_authenticated()
        
        data = {}
        if items:
            data["items"] = items
        if labels:
            data["labels"] = labels
        
        return self.client.put(
            f"/fulfillment/advance-ship-notices/{notice_id}",
            json_data=data,
        )
    
    def submit_advance_ship_notice(self, notice_id: str) -> Dict[str, Any]:
        """
        Submit advance ship notice for processing.
        
        Args:
            notice_id: Notice ID
            
        Returns:
            Submission response
        """
        self._ensure_authenticated()
        return self.client.post(f"/fulfillment/advance-ship-notices/{notice_id}/submit")
    
    def get_advance_ship_notice_labels(self, notice_id: str) -> bytes:
        """
        Get advance ship notice labels PDF.
        
        Args:
            notice_id: Notice ID
            
        Returns:
            Labels PDF content
        """
        self._ensure_authenticated()
        response = self.client.get(
            f"/fulfillment/advance-ship-notices/{notice_id}/labels",
            headers={"Accept": "application/pdf"},
        )
        return response.content
    
    # Fulfillment Stock
    def get_stock_levels(
        self,
        offer_id: Optional[List[str]] = None,
        product_id: Optional[List[str]] = None,
        ean: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get fulfillment stock levels.
        
        Args:
            offer_id: Offer IDs filter
            product_id: Product IDs filter
            ean: EAN codes filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Stock levels response
        """
        self._ensure_authenticated()
        
        params = {
            "offer.id": offer_id,
            "product.id": product_id,
            "ean": ean,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/fulfillment/stock", params=params)
    
    def get_stock_movements(
        self,
        offer_id: Optional[str] = None,
        type_: Optional[List[str]] = None,
        occurred_at_gte: Optional[datetime] = None,
        occurred_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get stock movements history.
        
        Args:
            offer_id: Offer ID filter
            type_: Movement types filter
            occurred_at_gte: Filter by occurrence date (after)
            occurred_at_lte: Filter by occurrence date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Stock movements response
        """
        self._ensure_authenticated()
        
        params = {
            "offer.id": offer_id,
            "type": type_,
            "limit": limit,
            "offset": offset,
        }
        
        if occurred_at_gte:
            params["occurredAt.gte"] = occurred_at_gte.isoformat()
        if occurred_at_lte:
            params["occurredAt.lte"] = occurred_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/fulfillment/stock-movements", params=params)
    
    # Fulfillment Parcels
    def get_parcels(
        self,
        status: Optional[List[str]] = None,
        carrier: Optional[str] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get fulfillment parcels.
        
        Args:
            status: Status filter
            carrier: Carrier filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Parcels response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "carrier": carrier,
            "limit": limit,
            "offset": offset,
        }
        
        if created_at_gte:
            params["createdAt.gte"] = created_at_gte.isoformat()
        if created_at_lte:
            params["createdAt.lte"] = created_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/fulfillment/parcels", params=params)
    
    def get_parcel(self, parcel_id: str) -> Dict[str, Any]:
        """
        Get parcel details.
        
        Args:
            parcel_id: Parcel ID
            
        Returns:
            Parcel details
        """
        self._ensure_authenticated()
        return self.client.get(f"/fulfillment/parcels/{parcel_id}")
    
    def get_parcel_tracking(self, parcel_id: str) -> Dict[str, Any]:
        """
        Get parcel tracking information.
        
        Args:
            parcel_id: Parcel ID
            
        Returns:
            Tracking information
        """
        self._ensure_authenticated()
        return self.client.get(f"/fulfillment/parcels/{parcel_id}/tracking")
    
    # Fulfillment Products
    def get_fulfillment_products(
        self,
        offer_id: Optional[List[str]] = None,
        product_id: Optional[List[str]] = None,
        ean: Optional[List[str]] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get products in fulfillment.
        
        Args:
            offer_id: Offer IDs filter
            product_id: Product IDs filter
            ean: EAN codes filter
            status: Status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Fulfillment products response
        """
        self._ensure_authenticated()
        
        params = {
            "offer.id": offer_id,
            "product.id": product_id,
            "ean": ean,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/fulfillment/products", params=params)
    
    def create_fulfillment_product(
        self,
        offer_id: str,
        dimensions: Dict[str, Any],
        weight: Dict[str, Any],
        dangerous_goods: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add product to fulfillment.
        
        Args:
            offer_id: Offer ID
            dimensions: Product dimensions
            weight: Product weight
            dangerous_goods: Dangerous goods information
            
        Returns:
            Created fulfillment product
        """
        self._ensure_authenticated()
        
        data = {
            "offer": {"id": offer_id},
            "dimensions": dimensions,
            "weight": weight,
        }
        
        if dangerous_goods:
            data["dangerousGoods"] = dangerous_goods
        
        return self.client.post("/fulfillment/products", json_data=data)
    
    def update_fulfillment_product(
        self,
        product_id: str,
        dimensions: Optional[Dict[str, Any]] = None,
        weight: Optional[Dict[str, Any]] = None,
        dangerous_goods: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update fulfillment product.
        
        Args:
            product_id: Product ID
            dimensions: Updated dimensions
            weight: Updated weight
            dangerous_goods: Updated dangerous goods info
            
        Returns:
            Updated product
        """
        self._ensure_authenticated()
        
        data = {}
        if dimensions:
            data["dimensions"] = dimensions
        if weight:
            data["weight"] = weight
        if dangerous_goods:
            data["dangerousGoods"] = dangerous_goods
        
        return self.client.put(f"/fulfillment/products/{product_id}", json_data=data)
    
    # Fulfillment Removal
    def get_removal_requests(
        self,
        status: Optional[List[str]] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get removal requests.
        
        Args:
            status: Status filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Removal requests response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        if created_at_gte:
            params["createdAt.gte"] = created_at_gte.isoformat()
        if created_at_lte:
            params["createdAt.lte"] = created_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/fulfillment/removal-requests", params=params)
    
    def create_removal_request(
        self,
        items: List[Dict[str, Any]],
        type_: str,
        reason: str,
        address: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create removal request.
        
        Args:
            items: Items to remove
            type_: Removal type (RETURN_TO_SELLER, DISPOSAL)
            reason: Removal reason
            address: Return address (for RETURN_TO_SELLER)
            
        Returns:
            Created removal request
        """
        self._ensure_authenticated()
        
        data = {
            "items": items,
            "type": type_,
            "reason": reason,
        }
        
        if address and type_ == "RETURN_TO_SELLER":
            data["address"] = address
        
        return self.client.post("/fulfillment/removal-requests", json_data=data)
    
    def get_removal_request(self, request_id: str) -> Dict[str, Any]:
        """
        Get removal request details.
        
        Args:
            request_id: Request ID
            
        Returns:
            Request details
        """
        self._ensure_authenticated()
        return self.client.get(f"/fulfillment/removal-requests/{request_id}")
    
    def cancel_removal_request(self, request_id: str) -> None:
        """
        Cancel removal request.
        
        Args:
            request_id: Request ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/fulfillment/removal-requests/{request_id}")