# ListingCraft Quick Start Guide

## Installation

```bash
pip install listingcraft
```

## Basic Setup

1. **Get API Keys**
   ```bash
   # Required: OpenAI API key
   export OPENAI_API_KEY="sk-your-openai-key"
   
   # Optional: For price research
   export SERP_API_KEY="your-serpapi-key"
   ```

2. **First Listing**
   ```python
   from listingcraft import ListingGenerator
   
   generator = ListingGenerator()
   listing = generator.generate("https://example.com/product.jpg")
   
   print(listing.title)
   print(listing.description)
   ```

## Usage Patterns

### Python Library
```python
from listingcraft import ListingGenerator, ListingCraftConfig

# Method 1: Environment variables
generator = ListingGenerator()

# Method 2: Custom config
config = ListingCraftConfig(
    openai_api_key="sk-...",
    temperature=0.7
)
generator = ListingGenerator(config)

# Generate listing
listing = generator.generate(
    image_url="https://example.com/product.jpg",
    marketplace="ebay",
    style="descriptive",
    brand="Nike"
)
```

### Command Line
```bash
# Basic generation
listingcraft generate https://example.com/product.jpg

# With options
listingcraft generate https://example.com/product.jpg \
  --marketplace poshmark \
  --style premium \
  --brand "Vintage Levi's" \
  --output listing.json

# Start API server
listingcraft server --port 8000
```

### API Server
```python
from listingcraft.integrations.fastapi_integration import run_server

# Start server
run_server(host="0.0.0.0", port=8000)
```

Then use REST API:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/product.jpg",
    "marketplace": "ebay",
    "style": "descriptive"
  }'
```

## Marketplace Options

- **ebay** - eBay optimized listings
- **poshmark** - Fashion-focused descriptions
- **mercari** - Concise, mobile-friendly
- **facebook** - Local marketplace style
- **amazon** - SEO-optimized format

## Style Options

- **descriptive** - Detailed, engaging descriptions
- **facts** - Bullet-point facts only
- **premium** - Luxury, high-end tone
- **minimal** - Short, concise listings