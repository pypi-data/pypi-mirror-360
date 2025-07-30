"""Core data models for ListingCraft"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field


class MarketplaceType(str, Enum):
    """Supported marketplace types"""
    EBAY = "ebay"
    POSHMARK = "poshmark"
    MERCARI = "mercari"
    FACEBOOK = "facebook"
    AMAZON = "amazon"


class ListingStyle(str, Enum):
    """Listing generation styles"""
    DESCRIPTIVE = "descriptive"
    FACTS = "facts"
    PREMIUM = "premium"
    MINIMAL = "minimal"


@dataclass
class ListingContext:
    """Context for listing generation"""
    style: ListingStyle = ListingStyle.DESCRIPTIVE
    condition: Optional[str] = None
    brand: Optional[str] = None
    other_info: Optional[str] = None
    target_marketplace: MarketplaceType = MarketplaceType.EBAY


class ListingRequest(BaseModel):
    """Request model for listing generation"""
    image_url: str = Field(..., description="URL of the product image")
    tag_image_urls: List[str] = Field(default=[], description="Additional product images")
    context: Optional[ListingContext] = Field(default=None, description="Generation context")
    marketplace: MarketplaceType = Field(default=MarketplaceType.EBAY, description="Target marketplace")
    user_id: Optional[str] = Field(default=None, description="User identifier")


class ListingResponse(BaseModel):
    """Response model for generated listing"""
    title: str = Field(..., description="Generated product title")
    description: str = Field(..., description="Generated product description")
    price_suggestion: Optional[float] = Field(default=None, description="Suggested price")
    category: Optional[str] = Field(default=None, description="Product category")
    tags: List[str] = Field(default=[], description="Product tags/keywords")
    marketplace_specific: Dict[str, Any] = Field(default={}, description="Marketplace-specific data")
    confidence_score: float = Field(default=0.0, description="Generation confidence (0-1)")
    processing_time: float = Field(default=0.0, description="Processing time in seconds")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy usage"""
        return self.model_dump()


class SimilarProduct(BaseModel):
    """Model for similar product search results"""
    title: str
    price: Optional[str] = None
    image_url: Optional[str] = None
    source: str
    similarity_score: float = 0.0