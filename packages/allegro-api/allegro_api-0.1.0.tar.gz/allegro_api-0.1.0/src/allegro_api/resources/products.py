"""
Products resource for Allegro API.
"""

from typing import Dict, Any, List, Optional

from .base import BaseResource


class ProductsResource(BaseResource):
    """Resource for product catalog operations."""
    
    def search(
        self,
        phrase: Optional[str] = None,
        mode: str = "REGULAR",
        language: str = "pl-PL",
        category_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_filters: bool = True,
        page_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search products in catalog.
        
        Args:
            phrase: Search phrase
            mode: Search mode (REGULAR, LEVENSHTEIN)
            language: Language for results
            category_id: Category to search in
            filters: Additional filters
            include_filters: Include available filters in response
            page_id: Page ID for pagination
            
        Returns:
            Search results
        """
        params = {
            "phrase": phrase,
            "mode": mode,
            "language": language,
            "category.id": category_id,
            "includeFilters": include_filters,
            "page.id": page_id,
        }
        
        if filters:
            params.update(filters)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/products", params=params)
    
    def get(self, product_id: str, category_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get product details.
        
        Args:
            product_id: Product ID
            category_id: Category ID (for category-specific parameters)
            
        Returns:
            Product details
        """
        params = {}
        if category_id:
            params["category.id"] = category_id
        
        return self.client.get(f"/sale/products/{product_id}", params=params)
    
    def get_proposals(
        self,
        category_id: str,
        name: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        ean: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get product proposals based on parameters.
        
        Args:
            category_id: Category ID
            name: Product name
            parameters: Product parameters
            ean: EAN code
            limit: Number of results
            offset: Results offset
            
        Returns:
            Product proposals
        """
        self._ensure_authenticated()
        
        params = {
            "category.id": category_id,
            "name": name,
            "ean": ean,
            "limit": limit,
            "offset": offset,
        }
        
        if parameters:
            # Convert parameters to query format
            for i, param in enumerate(parameters):
                params[f"parameters[{i}].id"] = param.get("id")
                params[f"parameters[{i}].values"] = param.get("values")
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/product-proposals", params=params)
    
    def create_proposal(
        self,
        category_id: str,
        name: str,
        parameters: List[Dict[str, Any]],
        images: Optional[List[str]] = None,
        description: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create new product proposal.
        
        Args:
            category_id: Category ID
            name: Product name
            parameters: Product parameters
            images: List of image URLs
            description: Product description
            
        Returns:
            Created proposal response
        """
        self._ensure_authenticated()
        
        data = {
            "category": {"id": category_id},
            "name": name,
            "parameters": parameters,
        }
        
        if images:
            data["images"] = [{"url": url} for url in images]
        
        if description:
            data["description"] = description
        
        return self.client.post("/sale/product-proposals", json_data=data)
    
    def get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Get product proposal details.
        
        Args:
            proposal_id: Proposal ID
            
        Returns:
            Proposal details
        """
        self._ensure_authenticated()
        return self.client.get(f"/sale/product-proposals/{proposal_id}")
    
    def delete_proposal(self, proposal_id: str) -> None:
        """
        Delete product proposal.
        
        Args:
            proposal_id: Proposal ID
        """
        self._ensure_authenticated()
        self.client.delete(f"/sale/product-proposals/{proposal_id}")
    
    def get_my_products(
        self,
        phrase: Optional[str] = None,
        language: str = "pl-PL",
        category_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get user's products.
        
        Args:
            phrase: Search phrase
            language: Language for results
            category_id: Category filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            User's products
        """
        self._ensure_authenticated()
        
        params = {
            "phrase": phrase,
            "language": language,
            "category.id": category_id,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/products/my-products", params=params)
    
    def match_product(
        self,
        category_id: str,
        name: str,
        parameters: List[Dict[str, Any]],
        ean: Optional[str] = None,
        upc: Optional[str] = None,
        isbn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Match offer parameters to existing product.
        
        Args:
            category_id: Category ID
            name: Product name
            parameters: Product parameters
            ean: EAN code
            upc: UPC code
            isbn: ISBN code
            
        Returns:
            Matched product or suggestions
        """
        self._ensure_authenticated()
        
        data = {
            "category": {"id": category_id},
            "name": name,
            "parameters": parameters,
        }
        
        if ean:
            data["ean"] = ean
        if upc:
            data["upc"] = upc
        if isbn:
            data["isbn"] = isbn
        
        return self.client.post("/sale/products/match", json_data=data)
    
    def get_compatibility_list(self, product_id: str, category_id: str) -> Dict[str, Any]:
        """
        Get product compatibility list.
        
        Args:
            product_id: Product ID
            category_id: Category ID
            
        Returns:
            Compatibility list
        """
        params = {"category.id": category_id}
        return self.client.get(f"/sale/products/{product_id}/compatibility-list", params=params)
    
    def update_compatibility_list(
        self,
        product_id: str,
        category_id: str,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Update product compatibility list.
        
        Args:
            product_id: Product ID
            category_id: Category ID
            items: Compatibility items
            
        Returns:
            Updated compatibility list
        """
        self._ensure_authenticated()
        
        data = {
            "category": {"id": category_id},
            "items": items,
        }
        
        return self.client.put(
            f"/sale/products/{product_id}/compatibility-list",
            json_data=data,
        )
    
    def get_change_proposals(
        self,
        product_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get product change proposals.
        
        Args:
            product_id: Product ID filter
            status: Status filter
            limit: Number of results
            offset: Results offset
            
        Returns:
            Change proposals
        """
        self._ensure_authenticated()
        
        params = {
            "product.id": product_id,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get("/sale/product-change-proposals", params=params)
    
    def create_change_proposal(
        self,
        product_id: str,
        changes: Dict[str, Any],
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create product change proposal.
        
        Args:
            product_id: Product ID
            changes: Proposed changes
            reason: Reason for changes
            
        Returns:
            Created proposal response
        """
        self._ensure_authenticated()
        
        data = {
            "product": {"id": product_id},
            "changes": changes,
        }
        
        if reason:
            data["reason"] = reason
        
        return self.client.post("/sale/product-change-proposals", json_data=data)