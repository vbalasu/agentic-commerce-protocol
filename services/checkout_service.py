"""
Checkout service with cart calculation logic
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from models.checkout import (
    CheckoutSession,
    CheckoutSessionWithOrder,
    CheckoutSessionCreateRequest,
    CheckoutSessionUpdateRequest,
    CheckoutSessionCompleteRequest,
    LineItem,
    Item,
    Total,
    TotalType,
    FulfillmentOptionShipping,
    FulfillmentOptionDigital,
    FulfillmentOption,
    CheckoutSessionStatus,
    PaymentProvider,
    MessageInfo,
    MessageError,
    Link,
    LinkType,
    Order,
    Error,
    ErrorType,
)
from data.products import get_product, check_product_availability
from config import settings


# In-memory storage for checkout sessions (in production, use database)
_checkout_sessions: dict[str, CheckoutSession] = {}
_orders: dict[str, Order] = {}


def _format_currency(amount_cents: int) -> str:
    """Format amount in cents as currency string"""
    return f"${amount_cents / 100:.2f}"


def _calculate_tax(subtotal_cents: int, tax_rate: float = 0.08) -> int:
    """Calculate tax (8% default)"""
    return int(subtotal_cents * tax_rate)


def _calculate_line_items(
    items: list[dict],
    currency: str = "USD"
) -> tuple[list[LineItem], list[MessageError]]:
    """Calculate line items from product items"""
    line_items = []
    errors = []
    
    items_base_amount = 0
    
    for item_data in items:
        product_id = item_data["id"]
        quantity = item_data["quantity"]
        
        product = get_product(product_id)
        if not product:
            errors.append(MessageError(
                code="invalid",
                param=f"$.items[?(@.id=='{product_id}')]",
                content_type="plain",
                content=f"Product '{product_id}' not found"
            ))
            continue
        
        if not check_product_availability(product_id, quantity):
            errors.append(MessageError(
                code="out_of_stock",
                param=f"$.items[?(@.id=='{product_id}')]",
                content_type="plain",
                content=f"Product '{product_id}' is out of stock"
            ))
            continue
        
        base_amount = product.price_cents * quantity
        discount = 0  # No discount for now
        subtotal = base_amount - discount
        tax = _calculate_tax(subtotal)
        total = subtotal + tax
        
        items_base_amount += base_amount
        
        line_items.append(LineItem(
            id=f"line_{product_id}_{quantity}",
            item=Item(id=product_id, quantity=quantity),
            base_amount=base_amount,
            discount=discount,
            subtotal=subtotal,
            tax=tax,
            total=total
        ))
    
    return line_items, errors


def _calculate_fulfillment_options(
    fulfillment_address: Optional[dict],
    line_items: list[LineItem],
    currency: str = "USD"
) -> list[FulfillmentOption]:
    """Generate fulfillment options based on address and items"""
    options = []
    
    # Check if any items are digital
    has_digital = any(
        get_product(item.item.id) and 
        get_product(item.item.id).category == "digital"
        for item in line_items
    )
    
    # Digital fulfillment option (only if all items are digital)
    all_digital = all(
        get_product(item.item.id) and 
        get_product(item.item.id).category == "digital"
        for item in line_items
    )
    
    if all_digital:
        subtotal_cents = sum(item.subtotal for item in line_items)
        tax_cents = sum(item.tax for item in line_items)
        total_cents = subtotal_cents + tax_cents
        
        options.append(FulfillmentOptionDigital(
            id="fulfillment_digital_001",
            title="Digital Delivery",
            subtitle="Instant download",
            subtotal=_format_currency(subtotal_cents),
            tax=_format_currency(tax_cents),
            total=_format_currency(total_cents)
        ))
    
    # Shipping options (if address provided)
    if fulfillment_address:
        subtotal_cents = sum(item.subtotal for item in line_items)
        tax_cents = sum(item.tax for item in line_items)
        
        # Standard shipping
        shipping_cost_cents = 500  # $5.00
        total_cents = subtotal_cents + tax_cents + shipping_cost_cents
        
        options.append(FulfillmentOptionShipping(
            id="fulfillment_shipping_standard",
            title="Standard Shipping",
            subtitle="5-7 business days",
            carrier="USPS",
            earliest_delivery_time=(datetime.utcnow() + timedelta(days=5)).isoformat() + "Z",
            latest_delivery_time=(datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            subtotal=_format_currency(subtotal_cents),
            tax=_format_currency(tax_cents),
            total=_format_currency(total_cents)
        ))
        
        # Express shipping
        express_shipping_cents = 1500  # $15.00
        express_total_cents = subtotal_cents + tax_cents + express_shipping_cents
        
        options.append(FulfillmentOptionShipping(
            id="fulfillment_shipping_express",
            title="Express Shipping",
            subtitle="2-3 business days",
            carrier="FedEx",
            earliest_delivery_time=(datetime.utcnow() + timedelta(days=2)).isoformat() + "Z",
            latest_delivery_time=(datetime.utcnow() + timedelta(days=3)).isoformat() + "Z",
            subtotal=_format_currency(subtotal_cents),
            tax=_format_currency(tax_cents),
            total=_format_currency(express_total_cents)
        ))
    
    return options


def _calculate_totals(
    line_items: list[LineItem],
    fulfillment_option: Optional[FulfillmentOption] = None
) -> list[Total]:
    """Calculate totals breakdown"""
    items_base_amount = sum(item.base_amount for item in line_items)
    items_discount = sum(item.discount for item in line_items)
    subtotal = sum(item.subtotal for item in line_items)
    tax = sum(item.tax for item in line_items)
    
    fulfillment_cost = 0
    if fulfillment_option:
        # Extract fulfillment cost from option total
        if isinstance(fulfillment_option, FulfillmentOptionShipping):
            # Parse total to get fulfillment cost
            option_total = float(fulfillment_option.total.replace("$", "")) * 100
            fulfillment_cost = int(option_total - subtotal - tax)
    
    total = subtotal + tax + fulfillment_cost
    
    totals = [
        Total(
            type=TotalType.ITEMS_BASE_AMOUNT,
            display_text="Items",
            amount=items_base_amount
        ),
    ]
    
    if items_discount > 0:
        totals.append(Total(
            type=TotalType.ITEMS_DISCOUNT,
            display_text="Discount",
            amount=-items_discount
        ))
    
    totals.append(Total(
        type=TotalType.SUBTOTAL,
        display_text="Subtotal",
        amount=subtotal
    ))
    
    if fulfillment_cost > 0:
        totals.append(Total(
            type=TotalType.FULFILLMENT,
            display_text="Shipping",
            amount=fulfillment_cost
        ))
    
    totals.append(Total(
        type=TotalType.TAX,
        display_text="Tax",
        amount=tax
    ))
    
    totals.append(Total(
        type=TotalType.TOTAL,
        display_text="Total",
        amount=total
    ))
    
    return totals


def _determine_status(
    line_items: list[LineItem],
    fulfillment_address: Optional[dict],
    fulfillment_option_id: Optional[str],
    errors: list[MessageError]
) -> CheckoutSessionStatus:
    """Determine checkout session status"""
    if errors:
        return CheckoutSessionStatus.NOT_READY_FOR_PAYMENT
    
    if not line_items:
        return CheckoutSessionStatus.NOT_READY_FOR_PAYMENT
    
    # Check if fulfillment is required and selected
    has_physical_items = any(
        get_product(item.item.id) and 
        get_product(item.item.id).category != "digital"
        for item in line_items
    )
    
    if has_physical_items:
        if not fulfillment_address or not fulfillment_option_id:
            return CheckoutSessionStatus.NOT_READY_FOR_PAYMENT
    
    return CheckoutSessionStatus.READY_FOR_PAYMENT


def create_checkout_session(
    request: CheckoutSessionCreateRequest
) -> CheckoutSession:
    """Create a new checkout session"""
    session_id = f"cs_{uuid.uuid4().hex[:12]}"
    
    # Calculate line items
    items_data = [{"id": item.id, "quantity": item.quantity} for item in request.items]
    line_items, errors = _calculate_line_items(items_data, settings.default_currency)
    
    # Generate fulfillment options
    fulfillment_address_dict = request.fulfillment_address.model_dump() if request.fulfillment_address else None
    fulfillment_options = _calculate_fulfillment_options(
        fulfillment_address_dict,
        line_items,
        settings.default_currency
    )
    
    # Determine selected fulfillment option
    fulfillment_option = None
    fulfillment_option_id = None
    if fulfillment_options:
        # Auto-select first option if address provided
        if fulfillment_address_dict:
            fulfillment_option = fulfillment_options[0]
            fulfillment_option_id = fulfillment_option.id
    
    # Calculate totals
    totals = _calculate_totals(line_items, fulfillment_option)
    
    # Determine status
    status = _determine_status(
        line_items,
        fulfillment_address_dict,
        fulfillment_option_id,
        errors
    )
    
    # Create messages
    messages = errors.copy()
    if not errors and status == CheckoutSessionStatus.NOT_READY_FOR_PAYMENT:
        messages.append(MessageInfo(
            param="$.fulfillment_address",
            content_type="plain",
            content="Please provide a shipping address to continue"
        ))
    
    # Create links
    links = [
        Link(
            type=LinkType.TERMS_OF_USE,
            url="https://merchant.example.com/terms"
        ),
        Link(
            type=LinkType.PRIVACY_POLICY,
            url="https://merchant.example.com/privacy"
        ),
    ]
    
    # Create payment provider
    payment_provider = PaymentProvider(
        provider=settings.payment_provider,
        supported_payment_methods=settings.supported_payment_methods
    )
    
    session = CheckoutSession(
        id=session_id,
        buyer=request.buyer,
        payment_provider=payment_provider,
        status=status,
        currency=settings.default_currency,
        line_items=line_items,
        fulfillment_address=request.fulfillment_address,
        fulfillment_options=fulfillment_options,
        fulfillment_option_id=fulfillment_option_id,
        totals=totals,
        messages=messages,
        links=links
    )
    
    _checkout_sessions[session_id] = session
    return session


def update_checkout_session(
    session_id: str,
    request: CheckoutSessionUpdateRequest
) -> CheckoutSession:
    """Update an existing checkout session"""
    if session_id not in _checkout_sessions:
        raise ValueError(f"Checkout session {session_id} not found")
    
    existing_session = _checkout_sessions[session_id]
    
    # Update buyer if provided
    buyer = request.buyer if request.buyer else existing_session.buyer
    
    # Update items if provided
    if request.items:
        items_data = [{"id": item.id, "quantity": item.quantity} for item in request.items]
    else:
        items_data = [{"id": item.item.id, "quantity": item.item.quantity} for item in existing_session.line_items]
    
    # Update fulfillment address if provided
    fulfillment_address = request.fulfillment_address if request.fulfillment_address else existing_session.fulfillment_address
    fulfillment_address_dict = fulfillment_address.dict() if fulfillment_address else None
    
    # Recalculate line items
    line_items, errors = _calculate_line_items(items_data, existing_session.currency)
    
    # Regenerate fulfillment options
    fulfillment_options = _calculate_fulfillment_options(
        fulfillment_address_dict,
        line_items,
        existing_session.currency
    )
    
    # Update fulfillment option
    fulfillment_option_id = request.fulfillment_option_id if request.fulfillment_option_id else existing_session.fulfillment_option_id
    fulfillment_option = None
    if fulfillment_option_id:
        fulfillment_option = next(
            (opt for opt in fulfillment_options if opt.id == fulfillment_option_id),
            None
        )
    
    # Recalculate totals
    totals = _calculate_totals(line_items, fulfillment_option)
    
    # Determine status
    status = _determine_status(
        line_items,
        fulfillment_address_dict,
        fulfillment_option_id,
        errors
    )
    
    # Create messages
    messages = errors.copy()
    if not errors and status == CheckoutSessionStatus.NOT_READY_FOR_PAYMENT:
        messages.append(MessageInfo(
            param="$.fulfillment_address",
            content_type="plain",
            content="Please provide a shipping address to continue"
        ))
    
    # Update session
    updated_session = CheckoutSession(
        id=session_id,
        buyer=buyer,
        payment_provider=existing_session.payment_provider,
        status=status,
        currency=existing_session.currency,
        line_items=line_items,
        fulfillment_address=fulfillment_address,
        fulfillment_options=fulfillment_options,
        fulfillment_option_id=fulfillment_option_id,
        totals=totals,
        messages=messages,
        links=existing_session.links
    )
    
    _checkout_sessions[session_id] = updated_session
    return updated_session


def get_checkout_session(session_id: str) -> Optional[CheckoutSession]:
    """Get checkout session by ID"""
    return _checkout_sessions.get(session_id)


def complete_checkout_session(
    session_id: str,
    request: CheckoutSessionCompleteRequest
) -> CheckoutSessionWithOrder:
    """Complete checkout session with payment"""
    session = get_checkout_session(session_id)
    if not session:
        raise ValueError(f"Checkout session {session_id} not found")
    
    if session.status == CheckoutSessionStatus.COMPLETED:
        raise ValueError("Checkout session already completed")
    
    if session.status == CheckoutSessionStatus.CANCELED:
        raise ValueError("Cannot complete canceled checkout session")
    
    if session.status != CheckoutSessionStatus.READY_FOR_PAYMENT:
        raise ValueError(f"Checkout session is not ready for payment (status: {session.status})")
    
    # Verify payment (mock or real)
    payment_verified = _verify_payment(request.payment_data)
    if not payment_verified:
        raise ValueError("Payment verification failed")
    
    # Create order
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    order = Order(
        id=order_id,
        checkout_session_id=session_id,
        permalink_url=f"https://merchant.example.com/orders/{order_id}"
    )
    _orders[order_id] = order
    
    # Update session status
    session.status = CheckoutSessionStatus.COMPLETED
    _checkout_sessions[session_id] = session
    
    # Return session with order
    return CheckoutSessionWithOrder(
        **session.model_dump(),
        order=order
    )


def cancel_checkout_session(session_id: str) -> CheckoutSession:
    """Cancel a checkout session"""
    session = get_checkout_session(session_id)
    if not session:
        raise ValueError(f"Checkout session {session_id} not found")
    
    if session.status == CheckoutSessionStatus.COMPLETED:
        raise ValueError("Cannot cancel completed checkout session")
    
    if session.status == CheckoutSessionStatus.CANCELED:
        return session
    
    session.status = CheckoutSessionStatus.CANCELED
    _checkout_sessions[session_id] = session
    return session


def _verify_payment(payment_data) -> bool:
    """Verify payment transaction (mock or real blockchain verification)"""
    if settings.mock_payment_verification:
        # Mock verification - accept any token that looks valid
        return len(payment_data.token) > 0
    else:
        # Real blockchain verification would go here
        # For now, return True for demo
        return True

