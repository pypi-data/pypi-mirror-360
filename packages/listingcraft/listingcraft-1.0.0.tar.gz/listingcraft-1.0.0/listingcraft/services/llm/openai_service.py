"""OpenAI service for ListingCraft"""

import logging
from typing import Dict, Any, Optional
from openai import OpenAI

from ...utils.config import ListingCraftConfig
from ...core.models import ListingContext


class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self, config: ListingCraftConfig):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        
    def generate_listing(
        self,
        image_analysis: Dict[str, Any],
        context: Optional[ListingContext] = None
    ) -> Dict[str, Any]:
        """Generate listing content using OpenAI"""
        
        try:
            # Build prompt based on image analysis and context
            prompt = self._build_prompt(image_analysis, context)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.config.default_model,
                messages=[
                    {"role": "system", "content": "You are an expert product listing writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            return self._parse_listing_response(content)
            
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return {
                "title": "Product Listing",
                "description": "Unable to generate description",
                "tags": [],
                "confidence": 0.0
            }
    
    def _build_prompt(
        self,
        image_analysis: Dict[str, Any],
        context: Optional[ListingContext]
    ) -> str:
        """Build prompt for listing generation"""
        
        base_prompt = f"""
        Generate a product listing based on this image analysis:
        
        Product Details: {image_analysis.get('description', 'N/A')}
        Brand: {image_analysis.get('brand', 'Unknown')}
        Key Features: {', '.join(image_analysis.get('features', []))}
        """
        
        if context:
            base_prompt += f"""
            
            Style: {context.style.value}
            Target Marketplace: {context.target_marketplace.value}
            """
            
            if context.condition:
                base_prompt += f"Condition: {context.condition}\n"
            if context.other_info:
                base_prompt += f"Additional Info: {context.other_info}\n"
        
        base_prompt += """
        
        Please provide:
        1. A compelling title (max 80 characters)
        2. A detailed description
        3. Relevant tags/keywords
        
        Format as JSON:
        {
            "title": "...",
            "description": "...",
            "tags": ["tag1", "tag2", ...]
        }
        """
        
        return base_prompt
    
    def _parse_listing_response(self, content: str) -> Dict[str, Any]:
        """Parse OpenAI response into structured data"""
        try:
            import json
            # Try to extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                parsed = json.loads(json_str)
                parsed['confidence'] = 0.9  # High confidence for successful parse
                return parsed
        except:
            pass
        
        # Fallback parsing
        lines = content.strip().split('\n')
        return {
            "title": lines[0] if lines else "Product Listing",
            "description": content,
            "tags": [],
            "confidence": 0.5
        }