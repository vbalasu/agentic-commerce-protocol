"""
ACP Checkout Data Models
Based on the ACP OpenAPI specification
"""
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class Address(BaseModel):
    """Shipping or billing address"""
    name: str
    line_one: str
    line_two: Optional[str] = None
    city: str
    state: str
    country: str
    postal_code: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "line_one": "555 Golden Gate Avenue",
                "line_two": "Apt 401",
                "city": "San Francisco",
                "state": "CA",
                "country": "US",
                "postal_code": "94102"
            }
        }


class Buyer(BaseModel):
    """Buyer information"""
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "+1-555-123-4567"
            }
        }


class Item(BaseModel):
    """Product item in cart"""
    id: str
    quantity: int = Field(ge=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "item_123",
                "quantity": 1
            }
        }


class PaymentProvider(BaseModel):
    """Payment provider information"""
    provider: Literal["stripe", "usdc", "stablecoin"]
    supported_payment_methods: list[Literal["card", "usdc"]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "usdc",
                "supported_payment_methods": ["usdc"]
            }
        }


class LineItem(BaseModel):
    """Line item with pricing breakdown"""
    id: str
    item: Item
    base_amount: int  # in cents
    discount: int = 0  # in cents
    subtotal: int  # in cents
    tax: int = 0  # in cents
    total: int  # in cents


class TotalType(str, Enum):
    """Total line item types"""
    ITEMS_BASE_AMOUNT = "items_base_amount"
    ITEMS_DISCOUNT = "items_discount"
    SUBTOTAL = "subtotal"
    DISCOUNT = "discount"
    FULFILLMENT = "fulfillment"
    TAX = "tax"
    FEE = "fee"
    TOTAL = "total"


class Total(BaseModel):
    """Total line in checkout"""
    type: TotalType
    display_text: str
    amount: int  # in cents


class FulfillmentOptionShipping(BaseModel):
    """Shipping fulfillment option"""
    type: Literal["shipping"] = "shipping"
    id: str
    title: str
    subtitle: Optional[str] = None
    carrier: Optional[str] = None
    earliest_delivery_time: Optional[str] = None  # ISO 8601 datetime
    latest_delivery_time: Optional[str] = None  # ISO 8601 datetime
    subtotal: str  # formatted string
    tax: str  # formatted string
    total: str  # formatted string


class FulfillmentOptionDigital(BaseModel):
    """Digital fulfillment option"""
    type: Literal["digital"] = "digital"
    id: str
    title: str
    subtitle: Optional[str] = None
    subtotal: str  # formatted string
    tax: str  # formatted string
    total: str  # formatted string


FulfillmentOption = Union[FulfillmentOptionShipping, FulfillmentOptionDigital]


class MessageInfo(BaseModel):
    """Informational message"""
    type: Literal["info"] = "info"
    param: Optional[str] = None  # RFC 9535 JSONPath
    content_type: Literal["plain", "markdown"] = "plain"
    content: str


class MessageError(BaseModel):
    """Error message"""
    type: Literal["error"] = "error"
    code: Literal[
        "missing",
        "invalid",
        "out_of_stock",
        "payment_declined",
        "requires_sign_in",
        "requires_3ds"
    ]
    param: Optional[str] = None  # RFC 9535 JSONPath
    content_type: Literal["plain", "markdown"] = "plain"
    content: str


Message = Union[MessageInfo, MessageError]


class LinkType(str, Enum):
    """Link types"""
    TERMS_OF_USE = "terms_of_use"
    PRIVACY_POLICY = "privacy_policy"
    SELLER_SHOP_POLICIES = "seller_shop_policies"


class Link(BaseModel):
    """Link to policy or terms"""
    type: LinkType
    url: str


class PaymentData(BaseModel):
    """Payment data - adapted for stablecoin"""
    token: str  # transaction hash or payment address for stablecoin
    provider: Literal["stripe", "usdc", "stablecoin"]
    billing_address: Address
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "0x1234567890abcdef...",  # transaction hash
                "provider": "usdc",
                "billing_address": {
                    "name": "John Doe",
                    "line_one": "555 Golden Gate Avenue",
                    "line_two": "Apt 401",
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "US",
                    "postal_code": "94102"
                }
            }
        }


class Order(BaseModel):
    """Order information"""
    id: str
    checkout_session_id: str
    permalink_url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "order_123",
                "checkout_session_id": "cs_123",
                "permalink_url": "https://merchant.example.com/orders/order_123"
            }
        }


class CheckoutSessionStatus(str, Enum):
    """Checkout session status"""
    NOT_READY_FOR_PAYMENT = "not_ready_for_payment"
    READY_FOR_PAYMENT = "ready_for_payment"
    COMPLETED = "completed"
    CANCELED = "canceled"
    IN_PROGRESS = "in_progress"


class CheckoutSessionBase(BaseModel):
    """Base checkout session"""
    id: str
    buyer: Optional[Buyer] = None
    payment_provider: PaymentProvider
    status: CheckoutSessionStatus
    currency: str
    line_items: list[LineItem]
    fulfillment_address: Optional[Address] = None
    fulfillment_options: list[FulfillmentOption]
    fulfillment_option_id: Optional[str] = None
    totals: list[Total]
    messages: list[Message]
    links: list[Link]


class CheckoutSession(CheckoutSessionBase):
    """Checkout session response"""
    pass


class CheckoutSessionWithOrder(CheckoutSessionBase):
    """Checkout session with order (after completion)"""
    order: Order


class CheckoutSessionCreateRequest(BaseModel):
    """Request to create checkout session"""
    buyer: Optional[Buyer] = None
    items: list[Item] = Field(min_length=1)
    fulfillment_address: Optional[Address] = None


class CheckoutSessionUpdateRequest(BaseModel):
    """Request to update checkout session"""
    buyer: Optional[Buyer] = None
    items: Optional[list[Item]] = None
    fulfillment_address: Optional[Address] = None
    fulfillment_option_id: Optional[str] = None


class CheckoutSessionCompleteRequest(BaseModel):
    """Request to complete checkout session"""
    buyer: Optional[Buyer] = None
    payment_data: PaymentData


class ErrorType(str, Enum):
    """Error types"""
    INVALID_REQUEST = "invalid_request"
    REQUEST_NOT_IDEMPOTENT = "request_not_idempotent"
    PROCESSING_ERROR = "processing_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


class Error(BaseModel):
    """Error response"""
    type: ErrorType
    code: str  # Implementation-defined error code
    message: str
    param: Optional[str] = None  # RFC 9535 JSONPath
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "invalid_request",
                "code": "missing_required_field",
                "message": "The field 'items' is required",
                "param": "$.items"
            }
        }

