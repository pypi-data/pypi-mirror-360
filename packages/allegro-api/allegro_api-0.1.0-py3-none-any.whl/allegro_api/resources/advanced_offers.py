"""
Advanced offer features for Allegro API.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseResource


class AdvancedOffersResource(BaseResource):
    """Resource for advanced offer features."""
    
    # Offer Variants
    def get_offer_variants(self, offer_id: str) -> Dict[str, Any]:
        """
        Get offer variants.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Variants information
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/offers/{offer_id}/variants")
    
    def create_variant_set(
        self,
        name: str,
        parameters: List[Dict[str, Any]],
        offers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create variant set.
        
        Args:
            name: Variant set name
            parameters: Variant parameters
            offers: Offers in set
            
        Returns:
            Created variant set
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "parameters": parameters,
            "offers": offers,
        }
        
        return self.client.post("/sale/variant-sets", json_data=data)
    
    def get_variant_sets(
        self,
        offer_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get variant sets.
        
        Args:
            offer_id: Offer ID filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Variant sets response
        """
        self._ensure_authenticated()
        
        params = {
            "offer.id": offer_id,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/variant-sets", params=params)
    
    def get_variant_set(self, set_id: str) -> Dict[str, Any]:
        """
        Get variant set details.
        
        Args:
            set_id: Set ID
            
        Returns:
            Set details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/variant-sets/{set_id}")
    
    def update_variant_set(
        self,
        set_id: str,
        name: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        offers: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update variant set.
        
        Args:
            set_id: Set ID
            name: Updated name
            parameters: Updated parameters
            offers: Updated offers
            
        Returns:
            Updated set
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if parameters:
            data["parameters"] = parameters
        if offers:
            data["offers"] = offers
        
        return self.client.put(f"/sale/variant-sets/{set_id}", json_data=data)
    
    def delete_variant_set(self, set_id: str) -> None:
        """
        Delete variant set.
        
        Args:
            set_id: Set ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/variant-sets/{set_id}")
    
    # Offer Translations
    def get_offer_translations(
        self,
        offer_id: str,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get offer translations.
        
        Args:
            offer_id: Offer ID
            language: Target language (if not specified, returns all translations)
            
        Returns:
            Translations response
        """
        self._ensure_authenticated()
        
        params = {}
        if language:
            params["language"] = language
        
        return self.client.get(f"/sale/offers/{offer_id}/translations", params=params)
    
    def update_offer_translation(
        self,
        offer_id: str,
        language: str,
        title: Optional[str] = None,
        description: Optional[Dict[str, Any]] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update offer translation.
        
        Args:
            offer_id: Offer ID
            language: Target language
            title: Translated title
            description: Translated description
            parameters: Translated parameters
            
        Returns:
            Updated translation
        """
        self._ensure_authenticated()
        
        data = {"language": language}
        
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if parameters:
            data["parameters"] = parameters
        
        return self.client.patch(
            f"/sale/offers/{offer_id}/translations/{language}",
            json_data=data,
        )
    
    def delete_offer_translation(
        self,
        offer_id: str,
        language: str,
        element: Optional[List[str]] = None,
        product_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Delete offer translation.
        
        Args:
            offer_id: Offer ID
            language: Language to delete
            element: Specific elements to delete (title, description, safety_information)
            product_ids: Product IDs for safety information deletion
        """
        self._ensure_authenticated()
        
        params = {}
        if element:
            params["element"] = element
        if product_ids:
            params["products.id"] = product_ids
        
        self.client.delete(
            f"/sale/offers/{offer_id}/translations/{language}",
            params=params if params else None,
        )
    
    # Additional Services Translations
    def get_additional_services_translations(
        self,
        group_id: str,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get additional services group translations.
        
        Args:
            group_id: Group ID
            language: Target language (if not specified, returns all translations)
            
        Returns:
            Translations response
        """
        self._ensure_authenticated()
        
        params = {}
        if language:
            params["language"] = language
        
        return self.client.get(
            f"/sale/offer-additional-services/groups/{group_id}/translations",
            params=params,
        )
    
    def update_additional_services_translation(
        self,
        group_id: str,
        language: str,
        name: Optional[str] = None,
        services: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update additional services group translation.
        
        Args:
            group_id: Group ID
            language: Target language
            name: Translated group name
            services: Translated services
            
        Returns:
            Updated translation
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if services:
            data["services"] = services
        
        return self.client.patch(
            f"/sale/offer-additional-services/groups/{group_id}/translations/{language}",
            json_data=data,
        )
    
    def delete_additional_services_translation(
        self,
        group_id: str,
        language: str,
    ) -> None:
        """
        Delete additional services group translation.
        
        Args:
            group_id: Group ID
            language: Language to delete
        """
        self._ensure_authenticated()
        self.client.delete(
            f"/sale/offer-additional-services/groups/{group_id}/translations/{language}"
        )
    
    # Automatic Pricing
    def get_price_automation_rules(
        self,
        offer_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get price automation rules.
        
        Args:
            offer_id: Offer ID filter
            status: Status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Rules response
        """
        self._ensure_authenticated()
        
        params = {
            "offer.id": offer_id,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/price-automation/rules", params=params)
    
    def create_price_automation_rule(
        self,
        name: str,
        offers: List[str],
        conditions: Dict[str, Any],
        actions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create price automation rule.
        
        Args:
            name: Rule name
            offers: Target offer IDs
            conditions: Rule conditions
            actions: Rule actions
            
        Returns:
            Created rule
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "offers": [{"id": offer_id} for offer_id in offers],
            "conditions": conditions,
            "actions": actions,
        }
        
        return self.client.post("/sale/price-automation/rules", json_data=data)
    
    def get_price_automation_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        Get price automation rule details.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Rule details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/price-automation/rules/{rule_id}")
    
    def update_price_automation_rule(
        self,
        rule_id: str,
        name: Optional[str] = None,
        offers: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        actions: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update price automation rule.
        
        Args:
            rule_id: Rule ID
            name: Updated name
            offers: Updated offers
            conditions: Updated conditions
            actions: Updated actions
            enabled: Enable/disable rule
            
        Returns:
            Updated rule
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if offers:
            data["offers"] = [{"id": offer_id} for offer_id in offers]
        if conditions:
            data["conditions"] = conditions
        if actions:
            data["actions"] = actions
        if enabled is not None:
            data["enabled"] = enabled
        
        return self.client.put(
            f"/sale/price-automation/rules/{rule_id}",
            json_data=data,
        )
    
    def delete_price_automation_rule(self, rule_id: str) -> None:
        """
        Delete price automation rule.
        
        Args:
            rule_id: Rule ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/price-automation/rules/{rule_id}")
    
    # Compatibility Lists
    def get_compatibility_lists(
        self,
        type_: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get compatibility lists.
        
        Args:
            type_: List type filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Lists response
        """
        self._ensure_authenticated()
        
        params = {
            "type": type_,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/compatibility-lists", params=params)
    
    def create_compatibility_list(
        self,
        name: str,
        type_: str,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create compatibility list.
        
        Args:
            name: List name
            type_: List type
            items: List items
            
        Returns:
            Created list
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "type": type_,
            "items": items,
        }
        
        return self.client.post("/sale/compatibility-lists", json_data=data)
    
    def get_compatibility_list(self, list_id: str) -> Dict[str, Any]:
        """
        Get compatibility list details.
        
        Args:
            list_id: List ID
            
        Returns:
            List details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/compatibility-lists/{list_id}")
    
    def update_compatibility_list(
        self,
        list_id: str,
        name: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update compatibility list.
        
        Args:
            list_id: List ID
            name: Updated name
            items: Updated items
            
        Returns:
            Updated list
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if items:
            data["items"] = items
        
        return self.client.put(
            f"/sale/compatibility-lists/{list_id}",
            json_data=data,
        )
    
    def delete_compatibility_list(self, list_id: str) -> None:
        """
        Delete compatibility list.
        
        Args:
            list_id: List ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/compatibility-lists/{list_id}")
    
    # Size Tables
    def get_size_tables(self) -> Dict[str, Any]:
        """
        Get size tables.
        
        Returns:
            Size tables response
        """
        self._ensure_authenticated()
        return self.client.get("/sale/size-tables")
    
    def create_size_table(
        self,
        name: str,
        type_: str,
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create size table.
        
        Args:
            name: Table name
            type_: Table type
            content: Table content
            
        Returns:
            Created table
        """
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "type": type_,
            "content": content,
        }
        
        return self.client.post("/sale/size-tables", json_data=data)
    
    def get_size_table(self, table_id: str) -> Dict[str, Any]:
        """
        Get size table details.
        
        Args:
            table_id: Table ID
            
        Returns:
            Table details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/size-tables/{table_id}")
    
    def update_size_table(
        self,
        table_id: str,
        name: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update size table.
        
        Args:
            table_id: Table ID
            name: Updated name
            content: Updated content
            
        Returns:
            Updated table
        """
        self._ensure_authenticated()
        
        data = {}
        if name:
            data["name"] = name
        if content:
            data["content"] = content
        
        return self.client.put(f"/sale/size-tables/{table_id}", json_data=data)
    
    def delete_size_table(self, table_id: str) -> None:
        """
        Delete size table.
        
        Args:
            table_id: Table ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/size-tables/{table_id}")