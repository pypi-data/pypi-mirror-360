"""
Promotions and marketing resources for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class PromotionsResource(BaseResource):
    """Resource for promotions, badges, and marketing campaigns."""
    
    # Rebates and Promotions
    def get_promotions(
        self,
        user_id: Optional[str] = None,
        status: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get available promotions.
        
        Args:
            user_id: User ID filter
            status: Status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Promotions response
        """
        params = {
            "user.id": user_id,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/loyalty/promotions", params=params)
    
    def create_promotion_campaign(
        self,
        name: str,
        benefits: List[Dict[str, Any]],
        target_offers: List[str],
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """
        Create promotion campaign.
        
        Args:
            name: Campaign name
            benefits: List of benefits
            target_offers: Target offer IDs
            start_date: Campaign start date
            end_date: Campaign end date
            
        Returns:
            Created campaign
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "benefits": benefits,
            "targetOffers": [{"id": offer_id} for offer_id in target_offers],
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }
        
        return self.client.post("/sale/loyalty/promotion-campaigns", json_data=data)
    
    def get_promotion_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get promotion campaign details.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/loyalty/promotion-campaigns/{campaign_id}")
    
    def update_promotion_campaign(
        self,
        campaign_id: str,
        name: Optional[str] = None,
        benefits: Optional[List[Dict[str, Any]]] = None,
        target_offers: Optional[List[str]] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Update promotion campaign.
        
        Args:
            campaign_id: Campaign ID
            name: Updated name
            benefits: Updated benefits
            target_offers: Updated target offers
            end_date: Updated end date
            
        Returns:
            Updated campaign
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if benefits:
            data["benefits"] = benefits
        if target_offers:
            data["targetOffers"] = [{"id": offer_id} for offer_id in target_offers]
        if end_date:
            data["endDate"] = end_date.isoformat()
        
        return self.client.put(
            f"/sale/loyalty/promotion-campaigns/{campaign_id}",
            json_data=data,
        )
    
    def delete_promotion_campaign(self, campaign_id: str) -> None:
        """
        Delete promotion campaign.
        
        Args:
            campaign_id: Campaign ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/loyalty/promotion-campaigns/{campaign_id}")
    
    # Badge Campaigns
    def get_badge_campaigns(
        self,
        offer_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get badge campaigns.
        
        Args:
            offer_id: Offer ID filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Badge campaigns response
        """
        self._ensure_authenticated()
        
        params = {
            "offer.id": offer_id,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/badge-campaigns", params=params)
    
    def get_badge_applications(
        self,
        campaign_id: Optional[str] = None,
        offer_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get badge applications.
        
        Args:
            campaign_id: Campaign ID filter
            offer_id: Offer ID filter
            status: Status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Badge applications response
        """
        self._ensure_authenticated()
        
        params = {
            "campaign.id": campaign_id,
            "offer.id": offer_id,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/badge-applications", params=params)
    
    def create_badge_application(
        self,
        campaign_id: str,
        offer_id: str,
        prices: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create badge application.
        
        Args:
            campaign_id: Campaign ID
            offer_id: Offer ID
            prices: Price information
            
        Returns:
            Created application
        """
        self._ensure_authenticated()
        
        data = {
            "campaign": {"id": campaign_id},
            "offer": {"id": offer_id},
        }
        
        if prices:
            data["prices"] = prices
        
        return self.client.post("/sale/badge-applications", json_data=data)
    
    def get_badge_application(self, application_id: str) -> Dict[str, Any]:
        """
        Get badge application details.
        
        Args:
            application_id: Application ID
            
        Returns:
            Application details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/badge-applications/{application_id}")
    
    def update_badge_application(
        self,
        application_id: str,
        prices: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update badge application.
        
        Args:
            application_id: Application ID
            prices: Updated prices
            
        Returns:
            Updated application
        """
        self._ensure_authenticated()
        
        return self.client.patch(
            f"/sale/badge-applications/{application_id}",
            json_data={"prices": prices},
        )
    
    def delete_badge_application(self, application_id: str) -> None:
        """
        Delete badge application.
        
        Args:
            application_id: Application ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/badge-applications/{application_id}")
    
    # Allegro Prices
    def get_allegro_prices_eligibility(self, offer_id: str) -> Dict[str, Any]:
        """
        Check offer eligibility for Allegro Prices.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Eligibility information
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/allegro-prices-offer-eligibility/{offer_id}")
    
    def get_allegro_prices_consent(self) -> Dict[str, Any]:
        """
        Get Allegro Prices consent status.
        
        Returns:
            Consent information
        """
        self._ensure_authenticated()
        return self.client.get("/sale/allegro-prices-eligibility")
    
    def update_allegro_prices_consent(self, consent: bool) -> Dict[str, Any]:
        """
        Update Allegro Prices consent.
        
        Args:
            consent: Consent status
            
        Returns:
            Updated consent
        """
        self._ensure_authenticated()
        
        return self.client.put(
            "/sale/allegro-prices-eligibility",
            json_data={"consent": consent},
        )
    
    # AlleDiscount
    def get_discounts(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get AlleDiscount campaigns.
        
        Args:
            user_id: User ID filter
            status: Status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Discounts response
        """
        params = {
            "user.id": user_id,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/discounts", params=params)
    
    # Offer Bundles
    def get_bundles(
        self,
        publication_status: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get offer bundles.
        
        Args:
            publication_status: Publication status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Bundles response
        """
        self._ensure_authenticated()
        
        params = {
            "publication.status": publication_status,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/offer-bundles", params=params)
    
    def create_bundle(
        self,
        name: str,
        offers: List[Dict[str, Any]],
        discount: Dict[str, Any],
        publication_status: str = "ACTIVE",
    ) -> Dict[str, Any]:
        """
        Create offer bundle.
        
        Args:
            name: Bundle name
            offers: List of offers in bundle
            discount: Discount information
            publication_status: Publication status
            
        Returns:
            Created bundle
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "offers": offers,
            "discount": discount,
            "publication": {"status": publication_status},
        }
        
        return self.client.post("/sale/offer-bundles", json_data=data)
    
    def get_bundle(self, bundle_id: str) -> Dict[str, Any]:
        """
        Get bundle details.
        
        Args:
            bundle_id: Bundle ID
            
        Returns:
            Bundle details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/offer-bundles/{bundle_id}")
    
    def update_bundle(
        self,
        bundle_id: str,
        name: Optional[str] = None,
        offers: Optional[List[Dict[str, Any]]] = None,
        discount: Optional[Dict[str, Any]] = None,
        publication_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update offer bundle.
        
        Args:
            bundle_id: Bundle ID
            name: Updated name
            offers: Updated offers
            discount: Updated discount
            publication_status: Updated status
            
        Returns:
            Updated bundle
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if offers:
            data["offers"] = offers
        if discount:
            data["discount"] = discount
        if publication_status:
            data["publication"] = {"status": publication_status}
        
        return self.client.put(f"/sale/offer-bundles/{bundle_id}", json_data=data)
    
    def delete_bundle(self, bundle_id: str) -> None:
        """
        Delete offer bundle.
        
        Args:
            bundle_id: Bundle ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/offer-bundles/{bundle_id}")