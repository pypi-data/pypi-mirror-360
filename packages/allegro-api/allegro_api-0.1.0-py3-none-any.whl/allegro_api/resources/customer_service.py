"""
Customer service resources for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class CustomerServiceResource(BaseResource):
    """Resource for customer service operations."""
    
    # Post Purchase Issues
    def get_post_purchase_issues(
        self,
        status: Optional[List[str]] = None,
        order_id: Optional[str] = None,
        buyer_login: Optional[str] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get post purchase issues.
        
        Args:
            status: Status filter
            order_id: Order ID filter
            buyer_login: Buyer login filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Issues response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "order.id": order_id,
            "buyer.login": buyer_login,
            "limit": limit,
            "offset": offset,
        }
        
        if created_at_gte:
            params["createdAt.gte"] = created_at_gte.isoformat()
        if created_at_lte:
            params["createdAt.lte"] = created_at_lte.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/order/issues", params=params)
    
    def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """
        Get issue details.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Issue details
        """
        self._ensure_authenticated()
        return self.client.get(f"/order/issues/{issue_id}")
    
    def get_issue_messages(self, issue_id: str) -> Dict[str, Any]:
        """
        Get issue messages.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Messages response
        """
        self._ensure_authenticated()
        return self.client.get(f"/order/issues/{issue_id}/messages")
    
    def send_issue_message(
        self,
        issue_id: str,
        text: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send message to issue.
        
        Args:
            issue_id: Issue ID
            text: Message text
            attachments: Message attachments
            
        Returns:
            Sent message
        """
        self._ensure_authenticated()
        
        data = {"text": text}
        
        if attachments:
            data["attachments"] = attachments
        
        return self.client.post(
            f"/order/issues/{issue_id}/messages",
            json_data=data,
        )
    
    # Disputes
    def get_disputes(
        self,
        status: Optional[str] = None,
        order_id: Optional[str] = None,
        created_at_gte: Optional[datetime] = None,
        created_at_lte: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get disputes.
        
        Args:
            status: Status filter
            order_id: Order ID filter
            created_at_gte: Filter by creation date (after)
            created_at_lte: Filter by creation date (before)
            limit: Number of results
            offset: Results offset
            
        Returns:
            Disputes response
        """
        self._ensure_authenticated()
        
        params = {
            "status": status,
            "checkoutForm.id": order_id,
            "limit": limit,
            "offset": offset,
        }
        
        if created_at_gte:
            params["createdAt.gte"] = created_at_gte.isoformat()
        if created_at_lte:
            params["createdAt.lte"] = created_at_lte.isoformat()
        
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
    
    def get_dispute_messages(
        self,
        dispute_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get dispute messages.
        
        Args:
            dispute_id: Dispute ID
            limit: Number of results
            offset: Results offset
            
        Returns:
            Messages response
        """
        self._ensure_authenticated()
        
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        return self.client.get(
            f"/sale/disputes/{dispute_id}/messages",
            params=params,
        )
    
    def send_dispute_message(
        self,
        dispute_id: str,
        text: str,
        type_: str = "MESSAGE",
    ) -> Dict[str, Any]:
        """
        Send message to dispute.
        
        Args:
            dispute_id: Dispute ID
            text: Message text
            type_: Message type
            
        Returns:
            Sent message
        """
        self._ensure_authenticated()
        
        data = {
            "text": text,
            "type": type_,
        }
        
        return self.client.post(
            f"/sale/disputes/{dispute_id}/messages",
            json_data=data,
        )
    
    def upload_dispute_attachment(
        self,
        dispute_id: str,
        filename: str,
        content: bytes,
    ) -> Dict[str, Any]:
        """
        Upload attachment to dispute.
        
        Args:
            dispute_id: Dispute ID
            filename: File name
            content: File content
            
        Returns:
            Upload response
        """
        self._ensure_authenticated()
        
        # Note: This is a simplified version
        # Actual implementation would handle multipart upload
        return self.client.post(
            f"/sale/disputes/{dispute_id}/attachments",
            files={"file": (filename, content)},
        )
    
    # Message Center
    def get_threads(
        self,
        read: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get message threads.
        
        Args:
            read: Read status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Threads response
        """
        self._ensure_authenticated()
        
        params = {
            "read": read,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/messaging/threads", params=params)
    
    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """
        Get thread details.
        
        Args:
            thread_id: Thread ID
            
        Returns:
            Thread details
        """
        self._ensure_authenticated()
        return self.client.get(f"/messaging/threads/{thread_id}")
    
    def get_thread_messages(
        self,
        thread_id: str,
        limit: int = 50,
        offset: int = 0,
        before: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get thread messages.
        
        Args:
            thread_id: Thread ID
            limit: Number of results
            offset: Results offset
            before: Get messages before this date
            
        Returns:
            Messages response
        """
        self._ensure_authenticated()
        
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if before:
            params["before"] = before.isoformat()
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get(
            f"/messaging/threads/{thread_id}/messages",
            params=params,
        )
    
    def send_message(
        self,
        thread_id: str,
        text: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send message to thread.
        
        Args:
            thread_id: Thread ID
            text: Message text
            attachments: Message attachments
            
        Returns:
            Sent message
        """
        self._ensure_authenticated()
        
        data = {"text": text}
        
        if attachments:
            data["attachments"] = attachments
        
        return self.client.post(
            f"/messaging/threads/{thread_id}/messages",
            json_data=data,
        )
    
    def mark_thread_as_read(self, thread_id: str) -> None:
        """
        Mark thread as read.
        
        Args:
            thread_id: Thread ID
        """
        self._ensure_authenticated()
        self.client.put(f"/messaging/threads/{thread_id}/read")
    
    def get_message_templates(
        self,
        language: str = "pl-PL",
    ) -> Dict[str, Any]:
        """
        Get message templates.
        
        Args:
            language: Template language
            
        Returns:
            Templates response
        """
        self._ensure_authenticated()
        
        params = {"language": language}
        
        return self.client.get("/messaging/templates", params=params)
    
    # Contacts
    def get_contacts(self) -> Dict[str, Any]:
        """
        Get seller contacts.
        
        Returns:
            Contacts response
        """
        self._ensure_authenticated()
        return self.client.get("/after-sales-service-conditions/contacts")
    
    def create_contact(
        self,
        name: str,
        phones: List[str],
        emails: List[str],
        address: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create contact.
        
        Args:
            name: Contact name
            phones: Phone numbers
            emails: Email addresses
            address: Contact address
            
        Returns:
            Created contact
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "phones": phones,
            "emails": emails,
            "address": address,
        }
        
        return self.client.post(
            "/after-sales-service-conditions/contacts",
            json_data=data,
        )
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Get contact details.
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Contact details
        """
        self._ensure_authenticated()
        return self.client.get(f"/after-sales-service-conditions/contacts/{contact_id}")
    
    def update_contact(
        self,
        contact_id: str,
        name: Optional[str] = None,
        phones: Optional[List[str]] = None,
        emails: Optional[List[str]] = None,
        address: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update contact.
        
        Args:
            contact_id: Contact ID
            name: Updated name
            phones: Updated phones
            emails: Updated emails
            address: Updated address
            
        Returns:
            Updated contact
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if phones:
            data["phones"] = phones
        if emails:
            data["emails"] = emails
        if address:
            data["address"] = address
        
        return self.client.put(
            f"/after-sales-service-conditions/contacts/{contact_id}",
            json_data=data,
        )