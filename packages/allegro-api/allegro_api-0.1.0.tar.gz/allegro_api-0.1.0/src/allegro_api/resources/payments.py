"""
Payments resource for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class PaymentsResource(BaseResource):
    """Resource for payment operations."""
    
    def get_payment_operations(
        self,
        wallet_type: Optional[str] = None,
        wallet_payment_operator: Optional[str] = None,
        payment_id: Optional[str] = None,
        participant_login: Optional[str] = None,
        occurred_at_gte: Optional[datetime] = None,
        occurred_at_lte: Optional[datetime] = None,
        group: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get list of payment operations.
        
        Args:
            wallet_type: Wallet type filter
            wallet_payment_operator: Payment operator filter
            payment_id: Payment ID filter
            participant_login: Participant login filter
            occurred_at_gte: Filter by occurrence date (after)
            occurred_at_lte: Filter by occurrence date (before)
            group: Operation groups to include
            limit: Number of results
            offset: Results offset
            
        Returns:
            Payment operations response
        """
        self._ensure_authenticated()
        
        params = {
            "wallet.type": wallet_type,
            "wallet.paymentOperator": wallet_payment_operator,
            "payment.id": payment_id,
            "participant.login": participant_login,
            "group": group,
            "limit": limit,
            "offset": offset,
        }
        
        if occurred_at_gte:
            params["occurredAt.gte"] = occurred_at_gte.isoformat()
        if occurred_at_lte:
            params["occurredAt.lte"] = occurred_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/payments/payment-operations", params=params)
    
    def get_payment_operation(self, operation_id: str) -> Dict[str, Any]:
        """
        Get payment operation details.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Operation details
        """
        self._ensure_authenticated()
        return self.client.get(f"/payments/payment-operations/{operation_id}")
    
    def get_payment_history(
        self,
        payment_id: Optional[str] = None,
        wallet_id: Optional[str] = None,
        wallet_type: Optional[str] = None,
        wallet_payment_operator: Optional[str] = None,
        occurred_at_gte: Optional[datetime] = None,
        occurred_at_lte: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get payment history.
        
        Args:
            payment_id: Payment ID filter
            wallet_id: Wallet ID filter
            wallet_type: Wallet type filter
            wallet_payment_operator: Payment operator filter
            occurred_at_gte: Filter by occurrence date (after)
            occurred_at_lte: Filter by occurrence date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Payment history response
        """
        self._ensure_authenticated()
        
        params = {
            "payment.id": payment_id,
            "wallet.id": wallet_id,
            "wallet.type": wallet_type,
            "wallet.paymentOperator": wallet_payment_operator,
            "limit": limit,
            "offset": offset,
        }
        
        if occurred_at_gte:
            params["occurredAt.gte"] = occurred_at_gte.isoformat()
        if occurred_at_lte:
            params["occurredAt.lte"] = occurred_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/payments/payment-history", params=params)
    
    def initiate_refund(
        self,
        payment_id: str,
        amount: float,
        reason: str,
        line_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Initiate payment refund.
        
        Args:
            payment_id: Payment ID
            amount: Refund amount
            reason: Refund reason
            line_items: Items to refund
            
        Returns:
            Refund initiation response
        """
        self._ensure_authenticated()
        
        data = {
            "payment": {"id": payment_id},
            "refund": {
                "amount": str(amount),
                "reason": reason,
            }
        }
        
        if line_items:
            data["lineItems"] = line_items
        
        return self.client.post("/payments/refunds", json_data=data)
    
    def get_refunds(
        self,
        payment_id: Optional[str] = None,
        status: Optional[str] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get payment refunds.
        
        Args:
            payment_id: Payment ID filter
            status: Refund status filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Refunds response
        """
        self._ensure_authenticated()
        
        params = {
            "payment.id": payment_id,
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
        
        return self.client.get("/payments/refunds", params=params)
    
    def get_refund(self, refund_id: str) -> Dict[str, Any]:
        """
        Get refund details.
        
        Args:
            refund_id: Refund ID
            
        Returns:
            Refund details
        """
        self._ensure_authenticated()
        return self.client.get(f"/payments/refunds/{refund_id}")
    
    def get_surcharges(
        self,
        order_id: Optional[str] = None,
        status: Optional[str] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get payment surcharges.
        
        Args:
            order_id: Order ID filter
            status: Surcharge status filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Surcharges response
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
        
        return self.client.get("/payments/surcharges", params=params)
    
    def create_surcharge(
        self,
        order_id: str,
        amount: float,
        type_: str,
        description: str,
    ) -> Dict[str, Any]:
        """
        Create payment surcharge.
        
        Args:
            order_id: Order ID
            amount: Surcharge amount
            type_: Surcharge type
            description: Surcharge description
            
        Returns:
            Created surcharge response
        """
        self._ensure_authenticated()
        
        data = {
            "order": {"id": order_id},
            "surcharge": {
                "amount": str(amount),
                "type": type_,
                "description": description,
            }
        }
        
        return self.client.post("/payments/surcharges", json_data=data)
    
    def get_wallets(
        self,
        currency: Optional[str] = None,
        type_: Optional[str] = None,
        payment_operator: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get user wallets.
        
        Args:
            currency: Currency filter
            type_: Wallet type filter
            payment_operator: Payment operator filter
            
        Returns:
            Wallets response
        """
        self._ensure_authenticated()
        
        params = {
            "currency": currency,
            "type": type_,
            "paymentOperator": payment_operator,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/payments/wallets", params=params)
    
    def get_wallet(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get wallet details.
        
        Args:
            wallet_id: Wallet ID
            
        Returns:
            Wallet details
        """
        self._ensure_authenticated()
        return self.client.get(f"/payments/wallets/{wallet_id}")
    
    def get_wallet_balance(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get wallet balance.
        
        Args:
            wallet_id: Wallet ID
            
        Returns:
            Wallet balance
        """
        self._ensure_authenticated()
        return self.client.get(f"/payments/wallets/{wallet_id}/balance")