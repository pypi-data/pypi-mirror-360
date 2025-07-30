"""Command-line interface for ListingCraft"""

import argparse
import json
import sys
from typing import Optional

from .core.listing_generator import ListingGenerator
from .utils.config import ListingCraftConfig


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ListingCraft - AI-powered product listing generation"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a listing")
    generate_parser.add_argument("image_url", help="Product image URL")
    generate_parser.add_argument("--marketplace", default="ebay", help="Target marketplace")
    generate_parser.add_argument("--style", default="descriptive", help="Listing style")
    generate_parser.add_argument("--brand", help="Product brand")
    generate_parser.add_argument("--condition", help="Product condition")
    generate_parser.add_argument("--output", help="Output file (JSON)")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start API server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Server host")
    server_parser.add_argument("--port", type=int, default=8000, help="Server port")
    
    # Version command
    subparsers.add_parser("version", help="Show version")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "version":
        from . import __version__
        print(f"ListingCraft {__version__}")
        return
    
    if args.command == "generate":
        generate_listing_cli(args)
    elif args.command == "server":
        start_server_cli(args)


def generate_listing_cli(args):
    """Handle generate command"""
    try:
        generator = ListingGenerator()
        
        listing = generator.generate(
            image_url=args.image_url,
            marketplace=args.marketplace,
            style=args.style,
            brand=args.brand,
            condition=args.condition
        )
        
        result = listing.to_dict()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Listing saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def start_server_cli(args):
    """Handle server command"""
    try:
        from .integrations.fastapi_integration import run_server
        print(f"🚀 Starting ListingCraft server on {args.host}:{args.port}")
        run_server(host=args.host, port=args.port)
    except Exception as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()