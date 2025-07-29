"""
Billing resource for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class BillingResource(BaseResource):
    """Resource for billing operations."""
    
    def get_billing_entries(
        self,
        occurred_at_gte: Optional[datetime] = None,
        occurred_at_lte: Optional[datetime] = None,
        type_id: Optional[List[str]] = None,
        offer_id: Optional[List[str]] = None,
        order_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get billing entries.
        
        Args:
            occurred_at_gte: Filter by occurrence date (after)
            occurred_at_lte: Filter by occurrence date (before)
            type_id: Billing type IDs to filter
            offer_id: Offer IDs to filter
            order_id: Order ID to filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Billing entries response
        """
        self._ensure_authenticated()
        
        params = {
            "order.id": order_id,
            "limit": limit,
            "offset": offset,
        }
        
        if occurred_at_gte:
            params["occurredAt.gte"] = occurred_at_gte.isoformat()
        if occurred_at_lte:
            params["occurredAt.lte"] = occurred_at_lte.isoformat()
        if type_id:
            params["type.id"] = type_id
        if offer_id:
            params["offer.id"] = offer_id
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/billing/billing-entries", params=params)
    
    def get_billing_entry(self, entry_id: str) -> Dict[str, Any]:
        """
        Get billing entry details.
        
        Args:
            entry_id: Billing entry ID
            
        Returns:
            Billing entry details
        """
        self._ensure_authenticated()
        return self.client.get(f"/billing/billing-entries/{entry_id}")
    
    def get_billing_types(self) -> Dict[str, Any]:
        """
        Get available billing types.
        
        Returns:
            Billing types response
        """
        self._ensure_authenticated()
        return self.client.get("/billing/billing-types")
    
    def get_commission_refunds(
        self,
        order_id: Optional[str] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get commission refunds.
        
        Args:
            order_id: Order ID filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            status: Refund status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Commission refunds response
        """
        self._ensure_authenticated()
        
        params = {
            "order.id": order_id,
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
        
        return self.client.get("/order/refund-claims", params=params)
    
    def create_commission_refund(
        self,
        order_id: str,
        line_items: List[Dict[str, Any]],
        delivery: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create commission refund claim.
        
        Args:
            order_id: Order ID
            line_items: Items to claim refund for
            delivery: Delivery refund details
            
        Returns:
            Created refund claim response
        """
        self._ensure_authenticated()
        
        data = {
            "id": order_id,
            "lineItems": line_items,
        }
        
        if delivery:
            data["delivery"] = delivery
        
        return self.client.post(f"/order/refund-claims", json_data=data)
    
    def get_commission_refund(self, claim_id: str) -> Dict[str, Any]:
        """
        Get commission refund claim details.
        
        Args:
            claim_id: Refund claim ID
            
        Returns:
            Refund claim details
        """
        self._ensure_authenticated()
        return self.client.get(f"/order/refund-claims/{claim_id}")
    
    def cancel_commission_refund(self, claim_id: str) -> None:
        """
        Cancel commission refund claim.
        
        Args:
            claim_id: Refund claim ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/order/refund-claims/{claim_id}")
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance summary.
        
        Returns:
            Balance summary
        """
        self._ensure_authenticated()
        return self.client.get("/account/balance")
    
    def get_operations_history(
        self,
        wallet_id: Optional[str] = None,
        operation_type: Optional[List[str]] = None,
        occurred_at_gte: Optional[datetime] = None,
        occurred_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get financial operations history.
        
        Args:
            wallet_id: Wallet ID filter
            operation_type: Operation types to filter
            occurred_at_gte: Filter by occurrence date (after)
            occurred_at_lte: Filter by occurrence date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Operations history response
        """
        self._ensure_authenticated()
        
        params = {
            "wallet.id": wallet_id,
            "operation.type": operation_type,
            "limit": limit,
            "offset": offset,
        }
        
        if occurred_at_gte:
            params["occurredAt.gte"] = occurred_at_gte.isoformat()
        if occurred_at_lte:
            params["occurredAt.lte"] = occurred_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/account/operations-history", params=params)