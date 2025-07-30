"""Image analysis service for ListingCraft"""

import logging
from typing import List, Dict, Any
from openai import OpenAI

from ...utils.config import ListingCraftConfig


class ImageAnalyzer:
    """Service for analyzing product images"""
    
    def __init__(self, config: ListingCraftConfig):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def analyze(
        self,
        main_image_url: str,
        additional_images: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze product images and extract information
        
        Args:
            main_image_url: URL of the main product image
            additional_images: List of additional image URLs
            
        Returns:
            Dictionary with extracted product information
        """
        if not self.config.enable_vision_analysis:
            return self._fallback_analysis()
        
        try:
            # Analyze main image with GPT-4 Vision
            analysis = self._analyze_with_vision(main_image_url)
            
            # Add analysis from additional images if provided
            if additional_images:
                for img_url in additional_images[:3]:  # Limit to 3 additional images
                    additional_analysis = self._analyze_with_vision(img_url)
                    analysis = self._merge_analysis(analysis, additional_analysis)
            
            return analysis
            
        except Exception as e:
            logging.error(f"Image analysis error: {e}")
            return self._fallback_analysis()
    
    def _analyze_with_vision(self, image_url: str) -> Dict[str, Any]:
        """Analyze single image with GPT-4 Vision"""
        
        response = self.client.chat.completions.create(
            model=self.config.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this product image and provide:
                            1. Product description
                            2. Brand (if visible)
                            3. Key features/attributes
                            4. Condition assessment
                            5. Category suggestion
                            
                            Format as JSON:
                            {
                                "description": "...",
                                "brand": "...",
                                "features": ["feature1", "feature2"],
                                "condition": "...",
                                "category": "..."
                            }"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        return self._parse_vision_response(content)
    
    def _parse_vision_response(self, content: str) -> Dict[str, Any]:
        """Parse vision API response"""
        try:
            import json
            # Extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback parsing
        return {
            "description": content[:200] + "..." if len(content) > 200 else content,
            "brand": "Unknown",
            "features": [],
            "condition": "Good",
            "category": "General"
        }
    
    def _merge_analysis(
        self,
        main_analysis: Dict[str, Any],
        additional_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge analysis from multiple images"""
        
        # Combine features
        main_features = set(main_analysis.get('features', []))
        additional_features = set(additional_analysis.get('features', []))
        combined_features = list(main_features.union(additional_features))
        
        # Use main analysis as base, enhance with additional info
        result = main_analysis.copy()
        result['features'] = combined_features
        
        # Update brand if it was unknown in main analysis
        if result.get('brand') == 'Unknown' and additional_analysis.get('brand') != 'Unknown':
            result['brand'] = additional_analysis.get('brand')
        
        return result
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when vision is disabled or fails"""
        return {
            "description": "Product for sale",
            "brand": "Unknown",
            "features": [],
            "condition": "Good",
            "category": "General"
        }