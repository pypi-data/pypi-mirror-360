"""
Miscellaneous resources for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class MiscResource(BaseResource):
    """Resource for miscellaneous operations."""
    
    # Information about marketplaces
    def get_marketplaces(self) -> Dict[str, Any]:
        """
        Get available marketplaces.
        
        Returns:
            Marketplaces response
        """
        return self.client.get("/marketplaces")
    
    def get_marketplace(self, marketplace_id: str) -> Dict[str, Any]:
        """
        Get marketplace details.
        
        Args:
            marketplace_id: Marketplace ID
            
        Returns:
            Marketplace details
        """
        return self.client.get(f"/marketplaces/{marketplace_id}")
    
    # Charity
    def get_charity_organizations(self) -> Dict[str, Any]:
        """
        Get charity organizations.
        
        Returns:
            Organizations response
        """
        return self.client.get("/charity/organizations")
    
    def get_charity_fundraising_campaigns(self) -> Dict[str, Any]:
        """
        Get charity fundraising campaigns.
        
        Returns:
            Campaigns response
        """
        self._ensure_authenticated()
        return self.client.get("/charity/fundraising-campaigns")
    
    # Public user information
    def get_user_public_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get public user information.
        
        Args:
            user_id: User ID
            
        Returns:
            User public information
        """
        return self.client.get(f"/users/{user_id}")
    
    def get_user_ratings_public(
        self,
        user_id: str,
        recommended: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get public user ratings.
        
        Args:
            user_id: User ID
            recommended: Filter by recommended
            limit: Number of results
            offset: Results offset
            
        Returns:
            Ratings response
        """
        params = {
            "recommended": recommended,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get(f"/users/{user_id}/ratings", params=params)
    
    def get_user_ratings_summary_public(self, user_id: str) -> Dict[str, Any]:
        """
        Get public user ratings summary.
        
        Args:
            user_id: User ID
            
        Returns:
            Ratings summary
        """
        return self.client.get(f"/users/{user_id}/ratings-summary")
    
    # Additional services
    def get_additional_services_groups(self) -> Dict[str, Any]:
        """
        Get additional services groups.
        
        Returns:
            Services groups response
        """
        self._ensure_authenticated()
        return self.client.get("/after-sales-service-conditions/additional-services/groups")
    
    def create_additional_services_group(
        self,
        name: str,
        services: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create additional services group.
        
        Args:
            name: Group name
            services: Services in group
            
        Returns:
            Created group
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "services": services,
        }
        
        return self.client.post(
            "/after-sales-service-conditions/additional-services/groups",
            json_data=data,
        )
    
    def get_additional_services_group(self, group_id: str) -> Dict[str, Any]:
        """
        Get additional services group details.
        
        Args:
            group_id: Group ID
            
        Returns:
            Group details
        """
        self._ensure_authenticated()
        return self.client.get(
            f"/after-sales-service-conditions/additional-services/groups/{group_id}"
        )
    
    def update_additional_services_group(
        self,
        group_id: str,
        name: Optional[str] = None,
        services: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update additional services group.
        
        Args:
            group_id: Group ID
            name: Updated name
            services: Updated services
            
        Returns:
            Updated group
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if services:
            data["services"] = services
        
        return self.client.put(
            f"/after-sales-service-conditions/additional-services/groups/{group_id}",
            json_data=data,
        )
    
    # Tax settings
    def get_tax_settings(self) -> Dict[str, Any]:
        """
        Get tax settings.
        
        Returns:
            Tax settings response
        """
        self._ensure_authenticated()
        return self.client.get("/sale/tax-settings")
    
    def get_tax_setting(self, setting_id: str) -> Dict[str, Any]:
        """
        Get tax setting details.
        
        Args:
            setting_id: Setting ID
            
        Returns:
            Setting details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/tax-settings/{setting_id}")
    
    # Pricing
    def calculate_fee_preview(
        self,
        offer: Dict[str, Any],
        command_type: str,
    ) -> Dict[str, Any]:
        """
        Calculate fee preview for offer.
        
        Args:
            offer: Offer data
            command_type: Command type (e.g., "CREATE_OFFER")
            
        Returns:
            Fee preview
        """
        self._ensure_authenticated()
        
        data = {
            "offer": offer,
            "commandType": command_type,
        }
        
        return self.client.post("/pricing/offer-fee-preview", json_data=data)
    
    def calculate_offer_quotes(
        self,
        offers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate quotes for offers.
        
        Args:
            offers: List of offers
            
        Returns:
            Quotes response
        """
        self._ensure_authenticated()
        
        data = {"offers": offers}
        
        return self.client.post("/pricing/offer-quotes", json_data=data)
    
    # Classification
    def suggest_category(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Suggest category for product.
        
        Args:
            name: Product name
            attributes: Product attributes
            
        Returns:
            Category suggestions
        """
        data = {"name": name}
        
        if attributes:
            data["attributes"] = attributes
        
        return self.client.post("/sale/category-suggestions", json_data=data)
    
    # Responsible persons/producers
    def get_responsible_persons(self) -> Dict[str, Any]:
        """
        Get responsible persons.
        
        Returns:
            Responsible persons response
        """
        self._ensure_authenticated()
        return self.client.get("/sale/responsible-persons")
    
    def create_responsible_person(
        self,
        name: str,
        address: Dict[str, Any],
        email: str,
        phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create responsible person.
        
        Args:
            name: Person name
            address: Person address
            email: Email address
            phone: Phone number
            
        Returns:
            Created person
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "address": address,
            "email": email,
        }
        
        if phone:
            data["phone"] = phone
        
        return self.client.post("/sale/responsible-persons", json_data=data)
    
    def get_responsible_producers(self) -> Dict[str, Any]:
        """
        Get responsible producers.
        
        Returns:
            Responsible producers response
        """
        self._ensure_authenticated()
        return self.client.get("/sale/responsible-producers")
    
    def create_responsible_producer(
        self,
        name: str,
        address: Dict[str, Any],
        contact: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create responsible producer.
        
        Args:
            name: Producer name
            address: Producer address
            contact: Contact information
            
        Returns:
            Created producer
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "address": address,
            "contact": contact,
        }
        
        return self.client.post("/sale/responsible-producers", json_data=data)
    
    # Conversions (Affiliate)
    def track_conversion(
        self,
        conversion_id: str,
        value: float,
        currency: str = "PLN",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Track affiliate conversion.
        
        Args:
            conversion_id: Conversion ID
            value: Conversion value
            currency: Currency
            metadata: Additional metadata
            
        Returns:
            Tracking response
        """
        data = {
            "conversionId": conversion_id,
            "value": str(value),
            "currency": currency,
        }
        
        if metadata:
            data["metadata"] = metadata
        
        return self.client.post("/affiliate/conversions", json_data=data)
    
    def get_conversions(
        self,
        conversion_id: Optional[str] = None,
        occurred_at_gte: Optional[datetime] = None,
        occurred_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get affiliate conversions.
        
        Args:
            conversion_id: Conversion ID filter
            occurred_at_gte: Filter by occurrence date (after)
            occurred_at_lte: Filter by occurrence date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Conversions response
        """
        params = {
            "conversionId": conversion_id,
            "limit": limit,
            "offset": offset,
        }
        
        if occurred_at_gte:
            params["occurredAt.gte"] = occurred_at_gte.isoformat()
        if occurred_at_lte:
            params["occurredAt.lte"] = occurred_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/affiliate/conversions", params=params)