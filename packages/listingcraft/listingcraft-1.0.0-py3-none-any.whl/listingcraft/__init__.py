"""
ListingCraft - AI-powered product listing generation

A Python library for generating optimized product listings from images
using advanced AI models and marketplace integrations.
"""

from .core.listing_generator import ListingGenerator
from .core.models import ListingRequest, ListingResponse, MarketplaceType
from .utils.config import ListingCraftConfig

__version__ = "1.0.0"
__author__ = "ListingCraft Team"
__email__ = "hello@listingcraft.com"

__all__ = [
    "ListingGenerator",
    "ListingRequest", 
    "ListingResponse",
    "MarketplaceType",
    "ListingCraftConfig"
]

# Simple one-line usage
def generate_listing(image_url: str, **kwargs) -> dict:
    """Generate a product listing from an image URL
    
    Args:
        image_url: URL of the product image
        **kwargs: Additional configuration options
        
    Returns:
        Dictionary containing title, description, and metadata
    """
    generator = ListingGenerator()
    response = generator.generate(image_url, **kwargs)
    return response.to_dict()