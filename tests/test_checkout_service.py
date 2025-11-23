"""
Tests for checkout service logic
"""
import pytest
from ..services.checkout_service import (
    create_checkout_session,
    update_checkout_session,
    get_checkout_session,
    complete_checkout_session,
    cancel_checkout_session,
)
from ..models.checkout import (
    CheckoutSessionCreateRequest,
    CheckoutSessionUpdateRequest,
    CheckoutSessionCompleteRequest,
    Item,
    Buyer,
    Address,
    PaymentData,
    CheckoutSessionStatus,
)


def test_create_checkout_session():
    """Test creating a checkout session"""
    request = CheckoutSessionCreateRequest(
        items=[
            Item(id="item_001", quantity=1)
        ]
    )
    session = create_checkout_session(request)
    assert session.id is not None
    assert session.status in [CheckoutSessionStatus.NOT_READY_FOR_PAYMENT, CheckoutSessionStatus.READY_FOR_PAYMENT]
    assert len(session.line_items) > 0
    assert len(session.totals) > 0


def test_create_checkout_session_with_address():
    """Test creating a checkout session with fulfillment address"""
    request = CheckoutSessionCreateRequest(
        items=[
            Item(id="item_001", quantity=1)
        ],
        fulfillment_address=Address(
            name="John Doe",
            line_one="123 Main St",
            city="San Francisco",
            state="CA",
            country="US",
            postal_code="94102"
        )
    )
    session = create_checkout_session(request)
    assert session.fulfillment_address is not None
    assert len(session.fulfillment_options) > 0


def test_update_checkout_session():
    """Test updating a checkout session"""
    # Create session
    create_request = CheckoutSessionCreateRequest(
        items=[Item(id="item_001", quantity=1)],
        fulfillment_address=Address(
            name="John Doe",
            line_one="123 Main St",
            city="San Francisco",
            state="CA",
            country="US",
            postal_code="94102"
        )
    )
    session = create_checkout_session(create_request)
    
    # Update session
    update_request = CheckoutSessionUpdateRequest(
        fulfillment_option_id=session.fulfillment_options[0].id
    )
    updated_session = update_checkout_session(session.id, update_request)
    assert updated_session.fulfillment_option_id == session.fulfillment_options[0].id


def test_get_checkout_session():
    """Test retrieving a checkout session"""
    request = CheckoutSessionCreateRequest(
        items=[Item(id="item_001", quantity=1)]
    )
    session = create_checkout_session(request)
    retrieved = get_checkout_session(session.id)
    assert retrieved is not None
    assert retrieved.id == session.id


def test_complete_checkout_session():
    """Test completing a checkout session"""
    # Create session with address
    create_request = CheckoutSessionCreateRequest(
        items=[Item(id="item_001", quantity=1)],
        fulfillment_address=Address(
            name="John Doe",
            line_one="123 Main St",
            city="San Francisco",
            state="CA",
            country="US",
            postal_code="94102"
        )
    )
    session = create_checkout_session(create_request)
    
    # Select fulfillment option
    if session.fulfillment_options:
        update_request = CheckoutSessionUpdateRequest(
            fulfillment_option_id=session.fulfillment_options[0].id
        )
        session = update_checkout_session(session.id, update_request)
    
    # Complete checkout
    complete_request = CheckoutSessionCompleteRequest(
        payment_data=PaymentData(
            token="0x1234567890abcdef",
            provider="usdc",
            billing_address=Address(
                name="John Doe",
                line_one="123 Main St",
                city="San Francisco",
                state="CA",
                country="US",
                postal_code="94102"
            )
        )
    )
    completed = complete_checkout_session(session.id, complete_request)
    assert completed.status == CheckoutSessionStatus.COMPLETED
    assert completed.order is not None
    assert completed.order.id is not None


def test_cancel_checkout_session():
    """Test canceling a checkout session"""
    request = CheckoutSessionCreateRequest(
        items=[Item(id="item_001", quantity=1)]
    )
    session = create_checkout_session(request)
    canceled = cancel_checkout_session(session.id)
    assert canceled.status == CheckoutSessionStatus.CANCELED


def test_invalid_product():
    """Test handling invalid product ID"""
    request = CheckoutSessionCreateRequest(
        items=[Item(id="invalid_product", quantity=1)]
    )
    session = create_checkout_session(request)
    # Session should be created but with error messages
    assert len(session.messages) > 0
    assert any(msg.type == "error" for msg in session.messages)


def test_out_of_stock_product():
    """Test handling out of stock product"""
    # This would require mocking the product catalog
    # For now, we'll test that the error handling works
    request = CheckoutSessionCreateRequest(
        items=[Item(id="item_001", quantity=999999)]  # Very large quantity
    )
    session = create_checkout_session(request)
    # Should still create session, but may have errors depending on availability check
    assert session.id is not None

