"""Main ListingCraft generator class"""

import time
import logging
from typing import List, Optional, Dict, Any

from .models import ListingRequest, ListingResponse, ListingContext, MarketplaceType, ListingStyle
from ..utils.config import ListingCraftConfig
from ..services.llm.openai_service import OpenAIService
from ..services.vision.image_analyzer import ImageAnalyzer
from ..services.marketplaces.marketplace_service import MarketplaceService


class ListingGenerator:
    """Main class for generating product listings"""
    
    def __init__(self, config: Optional[ListingCraftConfig] = None):
        """Initialize the listing generator
        
        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or ListingCraftConfig.from_env()
        self.config.validate()
        
        # Initialize services
        self._llm_service = OpenAIService(self.config)
        self._image_analyzer = ImageAnalyzer(self.config)
        self._marketplace_service = MarketplaceService(self.config)
        
        logging.info("ListingCraft initialized successfully")
    
    def generate(
        self,
        image_url: str,
        marketplace: str = "ebay",
        style: str = "descriptive",
        **kwargs
    ) -> ListingResponse:
        """Generate a product listing from an image
        
        Args:
            image_url: URL of the product image
            marketplace: Target marketplace (ebay, poshmark, etc.)
            style: Generation style (descriptive, facts, premium, minimal)
            **kwargs: Additional options (brand, condition, etc.)
            
        Returns:
            ListingResponse with generated content
        """
        start_time = time.time()
        
        # Create request object
        context = ListingContext(
            style=ListingStyle(style),
            brand=kwargs.get('brand'),
            condition=kwargs.get('condition'),
            other_info=kwargs.get('other_info'),
            target_marketplace=MarketplaceType(marketplace)
        )
        
        request = ListingRequest(
            image_url=image_url,
            tag_image_urls=kwargs.get('tag_images', []),
            context=context,
            marketplace=MarketplaceType(marketplace),
            user_id=kwargs.get('user_id')
        )
        
        return self._process_request(request, start_time)
    
    def generate_batch(
        self,
        image_urls: List[str],
        **kwargs
    ) -> List[ListingResponse]:
        """Generate multiple listings in batch
        
        Args:
            image_urls: List of image URLs
            **kwargs: Same options as generate()
            
        Returns:
            List of ListingResponse objects
        """
        return [self.generate(url, **kwargs) for url in image_urls]
    
    def get_similar_products(
        self,
        image_url: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar products for pricing research
        
        Args:
            image_url: Product image URL
            max_results: Maximum number of results
            
        Returns:
            List of similar products with pricing info
        """
        if not self.config.enable_similar_products:
            return []
        
        return self._marketplace_service.find_similar_products(image_url, max_results)
    
    def _process_request(self, request: ListingRequest, start_time: float) -> ListingResponse:
        """Process a listing generation request"""
        try:
            # Step 1: Analyze image
            image_analysis = self._image_analyzer.analyze(
                request.image_url,
                request.tag_image_urls
            )
            
            # Step 2: Generate listing content
            listing_content = self._llm_service.generate_listing(
                image_analysis,
                request.context
            )
            
            # Step 3: Get marketplace-specific data
            marketplace_data = self._marketplace_service.get_marketplace_data(
                listing_content,
                request.marketplace
            )
            
            # Step 4: Build response
            processing_time = time.time() - start_time
            
            return ListingResponse(
                title=listing_content.get('title', ''),
                description=listing_content.get('description', ''),
                price_suggestion=marketplace_data.get('price_suggestion'),
                category=marketplace_data.get('category'),
                tags=listing_content.get('tags', []),
                marketplace_specific=marketplace_data,
                confidence_score=listing_content.get('confidence', 0.8),
                processing_time=processing_time
            )
            
        except Exception as e:
            logging.error(f"Error processing listing request: {e}")
            # Return error response
            return ListingResponse(
                title="Error generating listing",
                description=f"An error occurred: {str(e)}",
                processing_time=time.time() - start_time,
                confidence_score=0.0
            )