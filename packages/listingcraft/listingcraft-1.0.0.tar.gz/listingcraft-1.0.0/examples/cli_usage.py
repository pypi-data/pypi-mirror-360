"""CLI usage examples for ListingCraft"""

import subprocess
import os

def run_cli_examples():
    """Examples of using ListingCraft CLI"""
    
    print("🖥️  ListingCraft CLI Examples")
    print("=" * 40)
    
    # Set environment variables for examples
    os.environ["OPENAI_API_KEY"] = "your-key-here"
    
    examples = [
        {
            "name": "Basic listing generation",
            "command": [
                "listingcraft", "generate", 
                "https://example.com/product.jpg"
            ]
        },
        {
            "name": "Generate for specific marketplace",
            "command": [
                "listingcraft", "generate",
                "https://example.com/product.jpg",
                "--marketplace", "poshmark",
                "--style", "premium"
            ]
        },
        {
            "name": "Generate with brand and condition",
            "command": [
                "listingcraft", "generate",
                "https://example.com/vintage-jacket.jpg",
                "--brand", "Levi's",
                "--condition", "Excellent",
                "--output", "listing.json"
            ]
        },
        {
            "name": "Start API server",
            "command": [
                "listingcraft", "server",
                "--host", "localhost",
                "--port", "8080"
            ]
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['name']}:")
        print(f"   {' '.join(example['command'])}")
    
    print("\n💡 Tips:")
    print("   • Set OPENAI_API_KEY environment variable")
    print("   • Use --output to save results to file")
    print("   • Server mode provides REST API endpoints")

if __name__ == "__main__":
    run_cli_examples()