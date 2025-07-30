"""Basic usage examples for ListingCraft"""

import os
from listingcraft import ListingGenerator, ListingCraftConfig

def basic_example():
    """Basic listing generation example"""
    
    # Method 1: Use environment variables (recommended)
    generator = ListingGenerator()
    
    # Generate a listing
    listing = generator.generate(
        image_url="https://example.com/product.jpg",
        marketplace="ebay",
        style="descriptive"
    )
    
    print(f"Title: {listing.title}")
    print(f"Description: {listing.description}")
    print(f"Suggested Price: ${listing.price_suggestion}")
    print(f"Processing Time: {listing.processing_time:.2f}s")


def custom_config_example():
    """Example with custom configuration"""
    
    # Method 2: Custom configuration
    config = ListingCraftConfig(
        openai_api_key="sk-your-key-here",
        serp_api_key="your-serp-key",
        default_model="gpt-4-1106-preview",
        temperature=0.7,
        cache_enabled=True
    )
    
    generator = ListingGenerator(config)
    
    # Generate with additional context
    listing = generator.generate(
        image_url="https://example.com/vintage-jacket.jpg",
        marketplace="poshmark",
        style="premium",
        brand="Vintage Levi's",
        condition="Excellent",
        other_info="Rare 1980s denim jacket"
    )
    
    print(f"Generated listing: {listing.to_dict()}")


if __name__ == "__main__":
    print("=== ListingCraft Examples ===")
    basic_example()