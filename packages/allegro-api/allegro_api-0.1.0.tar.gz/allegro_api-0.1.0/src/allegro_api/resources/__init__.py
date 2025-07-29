"""
API resources for Allegro API client.
"""

from .base import BaseResource
from .offers import OffersResource
from .categories import CategoriesResource
from .orders import OrdersResource
from .user import UserResource
from .payments import PaymentsResource
from .billing import BillingResource
from .products import ProductsResource
from .fulfillment import FulfillmentResource
from .promotions import PromotionsResource
from .customer_service import CustomerServiceResource
from .advanced_offers import AdvancedOffersResource
from .auctions import AuctionsResource
from .misc import MiscResource

__all__ = [
    "BaseResource",
    "OffersResource",
    "CategoriesResource",
    "OrdersResource",
    "UserResource",
    "PaymentsResource",
    "BillingResource",
    "ProductsResource",
    "FulfillmentResource",
    "PromotionsResource",
    "CustomerServiceResource",
    "AdvancedOffersResource",
    "AuctionsResource",
    "MiscResource",
]