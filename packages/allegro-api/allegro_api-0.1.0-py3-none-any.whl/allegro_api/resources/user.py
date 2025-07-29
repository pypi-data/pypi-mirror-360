"""
User resource for Allegro API.
"""

from typing import Dict, Any, List, Optional

from .base import BaseResource


class UserResource(BaseResource):
    """Resource for user information and settings."""
    
    def get_me(self) -> Dict[str, Any]:
        """
        Get current user information.
        
        Returns:
            User information
        """
        self._ensure_authenticated()
        return self.client.get("/me")
    
    def get_ratings(
        self,
        user_id: Optional[str] = None,
        recommended: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get user ratings.
        
        Args:
            user_id: User ID (None for current user)
            recommended: Filter by recommended
            limit: Number of results
            offset: Results offset
            
        Returns:
            Ratings response
        """
        if user_id:
            endpoint = f"/users/{user_id}/ratings"
        else:
            self._ensure_authenticated()
            endpoint = "/sale/user-ratings"
        
        params = {
            "recommended": recommended,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get(endpoint, params=params)
    
    def get_rating_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user rating summary.
        
        Args:
            user_id: User ID (None for current user)
            
        Returns:
            Rating summary
        """
        if user_id:
            endpoint = f"/users/{user_id}/ratings-summary"
        else:
            self._ensure_authenticated()
            endpoint = "/sale/user-ratings-summary"
        
        return self.client.get(endpoint)
    
    def get_return_policies(self) -> Dict[str, Any]:
        """
        Get user's return policies.
        
        Returns:
            Return policies
        """
        self._ensure_authenticated()
        return self.client.get("/after-sales-service-conditions/return-policies")
    
    def get_return_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Get specific return policy.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Return policy details
        """
        self._ensure_authenticated()
        return self.client.get(f"/after-sales-service-conditions/return-policies/{policy_id}")
    
    def create_return_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create return policy.
        
        Args:
            policy_data: Policy data
            
        Returns:
            Created policy response
        """
        self._ensure_authenticated()
        return self.client.post("/after-sales-service-conditions/return-policies", json_data=policy_data)
    
    def update_return_policy(self, policy_id: str, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update return policy.
        
        Args:
            policy_id: Policy ID
            policy_data: Updated policy data
            
        Returns:
            Updated policy response
        """
        self._ensure_authenticated()
        return self.client.put(
            f"/after-sales-service-conditions/return-policies/{policy_id}",
            json_data=policy_data,
        )
    
    def get_warranties(self) -> Dict[str, Any]:
        """
        Get user's warranties.
        
        Returns:
            Warranties
        """
        self._ensure_authenticated()
        return self.client.get("/after-sales-service-conditions/warranties")
    
    def get_warranty(self, warranty_id: str) -> Dict[str, Any]:
        """
        Get specific warranty.
        
        Args:
            warranty_id: Warranty ID
            
        Returns:
            Warranty details
        """
        self._ensure_authenticated()
        return self.client.get(f"/after-sales-service-conditions/warranties/{warranty_id}")
    
    def create_warranty(self, warranty_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create warranty.
        
        Args:
            warranty_data: Warranty data
            
        Returns:
            Created warranty response
        """
        self._ensure_authenticated()
        return self.client.post("/after-sales-service-conditions/warranties", json_data=warranty_data)
    
    def update_warranty(self, warranty_id: str, warranty_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update warranty.
        
        Args:
            warranty_id: Warranty ID
            warranty_data: Updated warranty data
            
        Returns:
            Updated warranty response
        """
        self._ensure_authenticated()
        return self.client.put(
            f"/after-sales-service-conditions/warranties/{warranty_id}",
            json_data=warranty_data,
        )
    
    def get_shipping_rates(self) -> Dict[str, Any]:
        """
        Get user's shipping rates.
        
        Returns:
            Shipping rates
        """
        self._ensure_authenticated()
        return self.client.get("/sale/shipping-rates")
    
    def get_shipping_rate(self, rate_id: str) -> Dict[str, Any]:
        """
        Get specific shipping rate.
        
        Args:
            rate_id: Rate ID
            
        Returns:
            Shipping rate details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/shipping-rates/{rate_id}")
    
    def create_shipping_rate(self, rate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create shipping rate.
        
        Args:
            rate_data: Rate data
            
        Returns:
            Created rate response
        """
        self._ensure_authenticated()
        return self.client.post("/sale/shipping-rates", json_data=rate_data)
    
    def update_shipping_rate(self, rate_id: str, rate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update shipping rate.
        
        Args:
            rate_id: Rate ID
            rate_data: Updated rate data
            
        Returns:
            Updated rate response
        """
        self._ensure_authenticated()
        return self.client.put(f"/sale/shipping-rates/{rate_id}", json_data=rate_data)
    
    def get_disputes(
        self,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get user's disputes.
        
        Args:
            status: Dispute status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Disputes response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/disputes", params=params)
    
    def get_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """
        Get dispute details.
        
        Args:
            dispute_id: Dispute ID
            
        Returns:
            Dispute details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/disputes/{dispute_id}")
    
    def get_messages(
        self,
        limit: int = 20,
        offset: int = 0,
        read: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Get user messages.
        
        Args:
            limit: Number of results
            offset: Results offset
            read: Filter by read status
            
        Returns:
            Messages response
        """
        self._ensure_authenticated()
        
        params = {
            "limit": limit,
            "offset": offset,
            "read": read,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/messaging/threads", params=params)