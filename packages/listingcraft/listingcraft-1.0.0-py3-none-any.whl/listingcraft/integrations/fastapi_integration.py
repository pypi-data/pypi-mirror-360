"""FastAPI integration for ListingCraft"""

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from ..core.listing_generator import ListingGenerator
from ..core.models import ListingResponse, MarketplaceType
from ..utils.config import ListingCraftConfig


class GenerateListingRequest(BaseModel):
  """Request model for FastAPI endpoint"""
  image_url: str
  marketplace: str = "ebay"
  style: str = "descriptive"
  brand: Optional[str] = None
  condition: Optional[str] = None
  tag_images: List[str] = []


class BatchGenerateRequest(BaseModel):
  """Request model for batch generation"""
  image_urls: List[str]
  marketplace: str = "ebay"
  style: str = "descriptive"


def create_listingcraft_app(config: Optional[ListingCraftConfig] = None) -> FastAPI:
  """Create a FastAPI app with ListingCraft endpoints

  Args:
      config: ListingCraft configuration

  Returns:
      Configured FastAPI application
  """

  app = FastAPI(
      title="ListingCraft API",
      description="AI-powered product listing generation",
      version="1.0.0"
  )

  # Initialize ListingCraft
  generator = ListingGenerator(config)

  @app.get("/health")
  async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ListingCraft"}

  @app.post("/generate", response_model=ListingResponse)
  async def generate_listing(request: GenerateListingRequest):
    """Generate a single product listing"""
    try:
      response = generator.generate(
          image_url=request.image_url,
          marketplace=request.marketplace,
          style=request.style,
          brand=request.brand,
          condition=request.condition,
          tag_images=request.tag_images
      )
      return response

    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

  @app.post("/generate/batch", response_model=List[ListingResponse])
  async def generate_batch(request: BatchGenerateRequest):
    """Generate multiple listings in batch"""
    try:
      responses = generator.generate_batch(
          image_urls=request.image_urls,
          marketplace=request.marketplace,
          style=request.style
      )
      return responses

    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

  @app.get("/similar/{image_url:path}")
  async def find_similar_products(image_url: str, max_results: int = 10):
    """Find similar products for pricing research"""
    try:
      similar_products = generator.get_similar_products(
          image_url=image_url,
          max_results=max_results
      )
      return {"similar_products": similar_products}

    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

  @app.get("/marketplaces")
  async def get_supported_marketplaces():
    """Get list of supported marketplaces"""
    return {
        "marketplaces": [marketplace.value for marketplace in MarketplaceType]
    }

  return app


# Convenience function for quick setup
def run_server(
    config: Optional[ListingCraftConfig] = None,
    host: str = "0.0.0.0",
    port: int = 8000
):
  """Run ListingCraft server

  Args:
      config: ListingCraft configuration
      host: Server host
      port: Server port
  """
  import uvicorn

  app = create_listingcraft_app(config)
  uvicorn.run(app, host=host, port=port)
