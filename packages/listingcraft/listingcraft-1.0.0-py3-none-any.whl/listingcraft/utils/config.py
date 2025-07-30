"""Configuration management for ListingCraft"""

import os
from typing import Optional, Dict, Any, Protocol
from dataclasses import dataclass, field


class SecretsProvider(Protocol):
    """Protocol for secrets management"""
    def get_secret(self, key: str) -> Optional[str]: ...


class EnvironmentSecrets:
    """Get secrets from environment variables"""
    def get_secret(self, key: str) -> Optional[str]:
        return os.getenv(key)


class DictSecrets:
    """Get secrets from dictionary"""
    def __init__(self, secrets: Dict[str, str]):
        self.secrets = secrets
    
    def get_secret(self, key: str) -> Optional[str]:
        return self.secrets.get(key)


@dataclass
class ListingCraftConfig:
    """Main configuration for ListingCraft"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    serp_api_key: Optional[str] = None
    
    # Model Configuration
    default_model: str = "gpt-4-1106-preview"
    vision_model: str = "gpt-4-vision-preview"
    temperature: float = 0.7
    
    # Performance Settings
    cache_enabled: bool = True
    max_retries: int = 3
    timeout_seconds: int = 60
    
    # Feature Flags
    enable_vision_analysis: bool = True
    enable_price_research: bool = True
    enable_similar_products: bool = True
    
    # Custom Secrets Provider
    secrets_provider: SecretsProvider = field(default_factory=EnvironmentSecrets)
    
    @classmethod
    def from_env(cls) -> 'ListingCraftConfig':
        """Create configuration from environment variables"""
        return cls(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            serp_api_key=os.getenv('SERP_API_KEY'),
            default_model=os.getenv('LISTINGCRAFT_MODEL', 'gpt-4-1106-preview'),
            temperature=float(os.getenv('LISTINGCRAFT_TEMPERATURE', '0.7')),
            cache_enabled=os.getenv('LISTINGCRAFT_CACHE', 'true').lower() == 'true',
        )
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ListingCraftConfig':
        """Create configuration from dictionary"""
        return cls(**{k: v for k, v in config.items() if hasattr(cls, k)})
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret using configured provider"""
        return self.secrets_provider.get_secret(key)
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        return True