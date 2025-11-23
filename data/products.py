"""
Mock product catalog for demonstration
In production, this would query a Delta table in Unity Catalog
"""
from typing import Optional
from dataclasses import dataclass


@dataclass
class Product:
    """Product information"""
    id: str
    name: str
    description: str
    price_cents: int  # Price in cents
    currency: str = "USD"
    category: Optional[str] = None
    in_stock: bool = True
    image_url: Optional[str] = None


# Mock product catalog
PRODUCTS = {
    "item_001": Product(
        id="item_001",
        name="Deluxe Shirt",
        description="Premium quality cotton shirt",
        price_cents=2600,  # $26.00
        category="apparel",
        in_stock=True,
        image_url="https://example.com/images/deluxe-shirt.jpg"
    ),
    "item_002": Product(
        id="item_002",
        name="Heavyweight",
        description="Durable heavyweight t-shirt",
        price_cents=2600,  # $26.00
        category="apparel",
        in_stock=True,
        image_url="https://example.com/images/heavyweight.jpg"
    ),
    "item_003": Product(
        id="item_003",
        name="Vintage Tee",
        description="Classic vintage style t-shirt",
        price_cents=2600,  # $26.00
        category="apparel",
        in_stock=True,
        image_url="https://example.com/images/vintage-tee.jpg"
    ),
    "item_004": Product(
        id="item_004",
        name="Black Hoodie",
        description="Comfortable black hoodie",
        price_cents=4500,  # $45.00
        category="apparel",
        in_stock=True,
        image_url="https://example.com/images/black-hoodie.jpg"
    ),
    "item_005": Product(
        id="item_005",
        name="Digital Product",
        description="Digital download product",
        price_cents=1000,  # $10.00
        category="digital",
        in_stock=True,
        image_url="https://example.com/images/digital.jpg"
    ),
}


def get_product(product_id: str) -> Optional[Product]:
    """Get product by ID"""
    return PRODUCTS.get(product_id)


def get_products() -> dict[str, Product]:
    """Get all products"""
    return PRODUCTS


def check_product_availability(product_id: str, quantity: int) -> bool:
    """Check if product is available in requested quantity"""
    product = get_product(product_id)
    if not product:
        return False
    if not product.in_stock:
        return False
    # In a real system, check actual inventory
    return True

