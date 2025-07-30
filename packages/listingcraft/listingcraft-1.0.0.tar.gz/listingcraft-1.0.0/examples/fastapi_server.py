"""FastAPI server example for ListingCraft"""

from listingcraft.integrations.fastapi_integration import create_listingcraft_app, run_server
from listingcraft import ListingCraftConfig

def main():
    """Run ListingCraft as a FastAPI server"""
    
    # Option 1: Quick start with environment variables
    # run_server()
    
    # Option 2: Custom configuration
    config = ListingCraftConfig.from_env()
    
    app = create_listingcraft_app(config)
    
    # Add custom endpoints if needed
    @app.get("/custom")
    async def custom_endpoint():
        return {"message": "Custom ListingCraft endpoint"}
    
    # Run server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()