"""
Categories resource for Allegro API.
"""

from typing import Dict, Any, List, Optional

from .base import BaseResource


class CategoriesResource(BaseResource):
    """Resource for working with categories."""
    
    def list(self, parent_id: str = None) -> Dict[str, Any]:
        """
        List categories.
        
        Args:
            parent_id: Parent category ID (None for root categories)
            
        Returns:
            Categories list
        """
        params = {}
        if parent_id:
            params["parent.id"] = parent_id
        
        return self.client.get("/sale/categories", params=params)
    
    def get(self, category_id: str) -> Dict[str, Any]:
        """
        Get category details.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category details
        """
        return self.client.get(f"/sale/categories/{category_id}")
    
    def get_parameters(self, category_id: str) -> Dict[str, Any]:
        """
        Get category parameters.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category parameters
        """
        return self.client.get(f"/sale/categories/{category_id}/parameters")
    
    def get_tree(self) -> List[Dict[str, Any]]:
        """
        Get full category tree.
        
        Returns:
            Category tree
        """
        def fetch_subcategories(parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
            """Recursively fetch subcategories."""
            response = self.list(parent_id)
            categories = response.get("categories", [])
            
            result = []
            for category in categories:
                cat_data = {
                    "id": category["id"],
                    "name": category["name"],
                    "leaf": category.get("leaf", False),
                    "parent": category.get("parent"),
                    "children": []
                }
                
                if not cat_data["leaf"]:
                    cat_data["children"] = fetch_subcategories(category["id"])
                
                result.append(cat_data)
            
            return result
        
        return fetch_subcategories()
    
    def search(self, phrase: str, parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search categories by phrase.
        
        Args:
            phrase: Search phrase
            parent_id: Limit search to parent category
            
        Returns:
            Matching categories
        """
        all_categories = []
        
        def search_in_tree(categories: List[Dict[str, Any]], search_phrase: str) -> List[Dict[str, Any]]:
            """Search in category tree."""
            results = []
            
            for category in categories:
                if search_phrase.lower() in category["name"].lower():
                    results.append(category)
                
                if "children" in category:
                    results.extend(search_in_tree(category["children"], search_phrase))
            
            return results
        
        # Get category tree starting from parent
        tree = self.get_tree() if not parent_id else fetch_subcategories(parent_id)
        
        return search_in_tree(tree, phrase)
    
    def get_most_popular(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most popular categories.
        
        Args:
            limit: Number of categories to return
            
        Returns:
            Popular categories
        """
        # This would typically use a specific endpoint, but for now we'll return root categories
        response = self.list()
        categories = response.get("categories", [])
        return categories[:limit]
    
    def suggest(self, name: str) -> List[Dict[str, Any]]:
        """
        Get category suggestions based on offer name.
        
        Args:
            name: Offer name
            
        Returns:
            Suggested categories
        """
        # This endpoint might not be available in all API versions
        try:
            params = {"name": name}
            response = self.client.get("/sale/category-suggestions", params=params)
            return response.get("categories", [])
        except:
            # Fallback to search
            return self.search(name)[:10]