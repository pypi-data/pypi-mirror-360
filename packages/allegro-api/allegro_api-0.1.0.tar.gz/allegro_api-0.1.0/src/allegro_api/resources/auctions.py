"""
Auctions and bidding resources for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class AuctionsResource(BaseResource):
    """Resource for auction and bidding operations."""
    
    def get_my_bids(
        self,
        auction_id: Optional[str] = None,
        status: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get user's bids.
        
        Args:
            auction_id: Auction ID filter
            status: Bid status filter
            sort: Sort order
            limit: Number of results
            offset: Results offset
            
        Returns:
            Bids response
        """
        self._ensure_authenticated()
        
        params = {
            "auction.id": auction_id,
            "status": status,
            "sort": sort,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/bidding/my-bids", params=params)
    
    def place_bid(
        self,
        auction_id: str,
        amount: float,
        currency: str = "PLN",
    ) -> Dict[str, Any]:
        """
        Place bid on auction.
        
        Args:
            auction_id: Auction ID
            amount: Bid amount
            currency: Bid currency
            
        Returns:
            Bid response
        """
        self._ensure_authenticated()
        
        data = {
            "auction": {"id": auction_id},
            "bid": {
                "amount": str(amount),
                "currency": currency,
            }
        }
        
        return self.client.post("/bidding/bids", json_data=data)
    
    def get_auction_events(
        self,
        from_id: Optional[str] = None,
        type_: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get auction events.
        
        Args:
            from_id: Event ID to start from
            type_: Event types to filter
            limit: Number of events
            
        Returns:
            Events response
        """
        self._ensure_authenticated()
        
        params = {
            "from": from_id,
            "type": type_,
            "limit": limit,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/bidding/auction-events", params=params)
    
    def get_bidding_history(
        self,
        auction_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get bidding history for auction.
        
        Args:
            auction_id: Auction ID
            limit: Number of results
            offset: Results offset
            
        Returns:
            Bidding history
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        return self.client.get(f"/bidding/auctions/{auction_id}/history", params=params)
    
    def get_won_auctions(
        self,
        payment_status: Optional[str] = None,
        delivery_status: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get won auctions.
        
        Args:
            payment_status: Payment status filter
            delivery_status: Delivery status filter
            sort: Sort order
            limit: Number of results
            offset: Results offset
            
        Returns:
            Won auctions response
        """
        self._ensure_authenticated()
        
        params = {
            "payment.status": payment_status,
            "delivery.status": delivery_status,
            "sort": sort,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/bidding/won-auctions", params=params)
    
    def get_auction_offers(
        self,
        status: Optional[List[str]] = None,
        publication_status: Optional[List[str]] = None,
        ending_at_gte: Optional[datetime] = None,
        ending_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get auction offers.
        
        Args:
            status: Auction status filter
            publication_status: Publication status filter
            ending_at_gte: Filter by ending date (after)
            ending_at_lte: Filter by ending date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Auction offers response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "publication.status": publication_status,
            "limit": limit,
            "offset": offset,
        }
        
        if ending_at_gte:
            params["endingAt.gte"] = ending_at_gte.isoformat()
        if ending_at_lte:
            params["endingAt.lte"] = ending_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/auction-offers", params=params)
    
    def get_watching_auctions(
        self,
        status: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get watched auctions.
        
        Args:
            status: Auction status filter
            sort: Sort order
            limit: Number of results
            offset: Results offset
            
        Returns:
            Watched auctions response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "sort": sort,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/bidding/watching", params=params)
    
    def watch_auction(self, auction_id: str) -> Dict[str, Any]:
        """
        Add auction to watchlist.
        
        Args:
            auction_id: Auction ID
            
        Returns:
            Watch response
        """
        self._ensure_authenticated()
        
        data = {"auction": {"id": auction_id}}
        
        return self.client.post("/bidding/watching", json_data=data)
    
    def unwatch_auction(self, auction_id: str) -> None:
        """
        Remove auction from watchlist.
        
        Args:
            auction_id: Auction ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/bidding/watching/{auction_id}")
    
    def get_bid_info(self, auction_id: str) -> Dict[str, Any]:
        """
        Get bid information for auction.
        
        Args:
            auction_id: Auction ID
            
        Returns:
            Bid information
        """
        self._ensure_authenticated()
        return self.client.get(f"/bidding/auctions/{auction_id}/bid-info")
    
    def cancel_bid(self, bid_id: str, reason: str) -> Dict[str, Any]:
        """
        Cancel bid.
        
        Args:
            bid_id: Bid ID
            reason: Cancellation reason
            
        Returns:
            Cancellation response
        """
        self._ensure_authenticated()
        
        data = {"reason": reason}
        
        return self.client.post(f"/bidding/bids/{bid_id}/cancel", json_data=data)