"""
Orders resource for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class OrdersResource(BaseResource):
    """Resource for managing orders."""
    
    def list(
        self,
        status: Optional[str] = None,
        fulfillment_status: Optional[str] = None,
        fulfillment_shipment_summary_line_items_sent: Optional[str] = None,
        line_items_bought_at_lte: Optional[datetime] = None,
        line_items_bought_at_gte: Optional[datetime] = None,
        payment_id: Optional[str] = None,
        surcharges_id: Optional[str] = None,
        delivery_method_id: Optional[str] = None,
        buyer_login: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        updated_at_lte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List orders.
        
        Args:
            status: Order status filter
            fulfillment_status: Fulfillment status filter
            fulfillment_shipment_summary_line_items_sent: Shipment filter
            line_items_bought_at_lte: Filter by purchase date (before)
            line_items_bought_at_gte: Filter by purchase date (after)
            payment_id: Payment ID filter
            surcharges_id: Surcharges ID filter
            delivery_method_id: Delivery method filter
            buyer_login: Buyer login filter
            marketplace_id: Marketplace ID filter
            updated_at_lte: Filter by update date (before)
            updated_at_gte: Filter by update date (after)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Orders list response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "fulfillment.status": fulfillment_status,
            "fulfillment.shipmentSummary.lineItemsSent": fulfillment_shipment_summary_line_items_sent,
            "payment.id": payment_id,
            "surcharges.id": surcharges_id,
            "delivery.method.id": delivery_method_id,
            "buyer.login": buyer_login,
            "marketplace.id": marketplace_id,
            "limit": limit,
            "offset": offset,
        }
        
        # Format datetime filters
        if line_items_bought_at_lte:
            params["lineItems.boughtAt.lte"] = line_items_bought_at_lte.isoformat()
        if line_items_bought_at_gte:
            params["lineItems.boughtAt.gte"] = line_items_bought_at_gte.isoformat()
        if updated_at_lte:
            params["updatedAt.lte"] = updated_at_lte.isoformat()
        if updated_at_gte:
            params["updatedAt.gte"] = updated_at_gte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/order/checkout-forms", params=params)
    
    def get(self, order_id: str) -> Dict[str, Any]:
        """
        Get order details.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order details
        """
        self._ensure_authenticated()
        return self.client.get(f"/order/checkout-forms/{order_id}")
    
    def get_events(
        self,
        from_: Optional[str] = None,
        type_: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get order events.
        
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
        
        return self.client.get("/order/events", params=params)
    
    def get_shipments(self, order_id: str) -> Dict[str, Any]:
        """
        Get order shipments.
        
        Args:
            order_id: Order ID
            
        Returns:
            Shipments information
        """
        self._ensure_authenticated()
        return self.client.get(f"/order/checkout-forms/{order_id}/shipments")
    
    def create_shipment(
        self,
        order_id: str,
        carrier_id: str,
        carrier_name: str,
        tracking_number: Optional[str] = None,
        line_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create shipment for order.
        
        Args:
            order_id: Order ID
            carrier_id: Carrier ID
            carrier_name: Carrier name
            tracking_number: Tracking number
            line_items: Items to include in shipment
            
        Returns:
            Created shipment response
        """
        self._ensure_authenticated()
        
        data = {
            "carrierId": carrier_id,
            "carrierName": carrier_name,
        }
        
        if tracking_number:
            data["trackingNumber"] = tracking_number
        
        if line_items:
            data["lineItems"] = line_items
        
        return self.client.post(
            f"/order/checkout-forms/{order_id}/shipments",
            json_data=data,
        )
    
    def get_invoices(self, order_id: str) -> Dict[str, Any]:
        """
        Get order invoices.
        
        Args:
            order_id: Order ID
            
        Returns:
            Invoices information
        """
        self._ensure_authenticated()
        return self.client.get(f"/order/checkout-forms/{order_id}/invoices")
    
    def upload_invoice(
        self,
        order_id: str,
        invoice_file: bytes,
        invoice_number: str,
    ) -> Dict[str, Any]:
        """
        Upload invoice for order.
        
        Args:
            order_id: Order ID
            invoice_file: Invoice file content
            invoice_number: Invoice number
            
        Returns:
            Upload response
        """
        self._ensure_authenticated()
        
        # This is a simplified version - actual implementation would handle file upload
        data = {
            "invoiceNumber": invoice_number,
        }
        
        return self.client.post(
            f"/order/checkout-forms/{order_id}/invoices",
            json_data=data,
        )
    
    def get_refunds(self, order_id: str) -> Dict[str, Any]:
        """
        Get order refunds.
        
        Args:
            order_id: Order ID
            
        Returns:
            Refunds information
        """
        self._ensure_authenticated()
        return self.client.get(f"/order/checkout-forms/{order_id}/refunds")
    
    def create_refund(
        self,
        order_id: str,
        amount: float,
        reason: str,
        line_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create refund for order.
        
        Args:
            order_id: Order ID
            amount: Refund amount
            reason: Refund reason
            line_items: Items to refund
            
        Returns:
            Created refund response
        """
        self._ensure_authenticated()
        
        data = {
            "refund": {
                "amount": str(amount),
                "reason": reason,
            }
        }
        
        if line_items:
            data["lineItems"] = line_items
        
        return self.client.post(
            f"/order/checkout-forms/{order_id}/refunds",
            json_data=data,
        )
    
    def add_comment(
        self,
        order_id: str,
        text: str,
        type_: str = "SELLER_MESSAGE",
    ) -> Dict[str, Any]:
        """
        Add comment to order.
        
        Args:
            order_id: Order ID
            text: Comment text
            type_: Comment type
            
        Returns:
            Comment response
        """
        self._ensure_authenticated()
        
        data = {
            "text": text,
            "type": type_,
        }
        
        return self.client.post(
            f"/order/checkout-forms/{order_id}/comments",
            json_data=data,
        )
    
    def get_returns(
        self,
        status: Optional[str] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get customer returns.
        
        Args:
            status: Return status filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Returns list response
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
        
        return self.client.get("/after-sales-service-conditions/returns", params=params)
    
    def get_return(self, return_id: str) -> Dict[str, Any]:
        """
        Get return details.
        
        Args:
            return_id: Return ID
            
        Returns:
            Return details
        """
        self._ensure_authenticated()
        return self.client.get(f"/after-sales-service-conditions/returns/{return_id}")