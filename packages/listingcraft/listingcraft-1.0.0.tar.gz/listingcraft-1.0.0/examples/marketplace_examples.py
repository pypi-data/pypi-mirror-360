"""Marketplace-specific examples for ListingCraft"""

from listingcraft import ListingGenerator

def ebay_example():
    """eBay-optimized listing example"""
    generator = ListingGenerator()
    
    listing = generator.generate(
        image_url="https://example.com/electronics.jpg",
        marketplace="ebay",
        style="descriptive",
        condition="Used - Good"
    )
    
    print("📦 eBay Listing:")
    print(f"Title: {listing.title}")
    print(f"Category: {listing.marketplace_specific.get('category')}")
    print(f"Item Specifics: {listing.marketplace_specific.get('item_specifics')}")

def poshmark_example():
    """Poshmark fashion listing example"""
    generator = ListingGenerator()
    
    listing = generator.generate(
        image_url="https://example.com/dress.jpg",
        marketplace="poshmark",
        style="premium",
        brand="Zara",
        condition="Like New"
    )
    
    print("👗 Poshmark Listing:")
    print(f"Title: {listing.title}")
    print(f"Brand: {listing.marketplace_specific.get('brand_verification')}")
    print(f"Size Info: {listing.marketplace_specific.get('size_chart')}")

def mercari_example():
    """Mercari concise listing example"""
    generator = ListingGenerator()
    
    listing = generator.generate(
        image_url="https://example.com/collectible.jpg",
        marketplace="mercari",
        style="minimal"
    )
    
    print("🎯 Mercari Listing:")
    print(f"Title: {listing.title}")
    print(f"Condition Rating: {listing.marketplace_specific.get('condition_rating')}/5")
    print(f"Shipping: {listing.marketplace_specific.get('shipping_weight')}")

def batch_marketplace_example():
    """Generate for multiple marketplaces"""
    generator = ListingGenerator()
    
    image_url = "https://example.com/sneakers.jpg"
    marketplaces = ["ebay", "poshmark", "mercari"]
    
    print("👟 Multi-Marketplace Listings:")
    
    for marketplace in marketplaces:
        listing = generator.generate(
            image_url=image_url,
            marketplace=marketplace,
            brand="Nike"
        )
        print(f"\n{marketplace.upper()}:")
        print(f"  Title: {listing.title[:50]}...")
        print(f"  Price: ${listing.price_suggestion}")

if __name__ == "__main__":
    print("🏪 Marketplace-Specific Examples")
    print("=" * 40)
    
    ebay_example()
    print()
    poshmark_example()
    print()
    mercari_example()
    print()
    batch_marketplace_example()