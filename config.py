"""
Configuration for ACP Demo
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_version: str = "2025-09-29"
    api_title: str = "Agentic Checkout API"
    
    # Currency
    default_currency: str = "USD"
    
    # Payment Provider
    payment_provider: str = "usdc"  # stablecoin provider
    supported_payment_methods: list[str] = ["usdc"]
    
    # Databricks Configuration
    databricks_workspace_url: Optional[str] = None
    databricks_catalog: str = "main"
    databricks_schema: str = "acp_demo"
    products_table: str = "products"
    
    # Stablecoin Configuration
    stablecoin_network: str = "solana"  # or "ethereum", "polygon", etc.
    stablecoin_contract_address: Optional[str] = None  # USDC contract address
    mock_payment_verification: bool = True  # Set to False for real blockchain verification
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

