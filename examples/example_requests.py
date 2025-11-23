"""
Example requests for ACP Checkout API
These match the ACP specification examples
"""
from typing import Dict, Any

# Example 1: Create checkout session - minimal (single item, no fulfillment address)
CREATE_MINIMAL: Dict[str, Any] = {
    "items": [
        {
            "id": "item_123",
            "quantity": 1
        }
    ]
}

# Example 2: Create checkout session - with address
CREATE_WITH_ADDRESS: Dict[str, Any] = {
    "items": [
        {
            "id": "item_456",
            "quantity": 1
        }
    ],
    "fulfillment_address": {
        "name": "test",
        "line_one": "555 Golden Gate Avenue",
        "line_two": "Apt 401",
        "city": "San Francisco",
        "state": "CA",
        "country": "US",
        "postal_code": "94102"
    }
}

# Example 3: Create checkout session - with buyer info
CREATE_WITH_BUYER: Dict[str, Any] = {
    "items": [
        {
            "id": "item_001",
            "quantity": 1
        }
    ],
    "buyer": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1-555-123-4567"
    },
    "fulfillment_address": {
        "name": "John Doe",
        "line_one": "555 Golden Gate Avenue",
        "line_two": "Apt 401",
        "city": "San Francisco",
        "state": "CA",
        "country": "US",
        "postal_code": "94102"
    }
}

# Example 4: Update checkout session - set fulfillment option
UPDATE_FULFILLMENT_OPTION: Dict[str, Any] = {
    "fulfillment_option_id": "fulfillment_option_456"
}

# Example 5: Update checkout session - update items
UPDATE_ITEMS: Dict[str, Any] = {
    "items": [
        {
            "id": "item_001",
            "quantity": 2
        },
        {
            "id": "item_002",
            "quantity": 1
        }
    ]
}

# Example 6: Complete checkout session - with stablecoin payment
COMPLETE_WITH_PAYMENT: Dict[str, Any] = {
    "payment_data": {
        "token": "0x1234567890abcdef1234567890abcdef12345678",  # Transaction hash
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
    },
    "buyer": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1-555-123-4567"
    }
}

# Example 7: Complete checkout session - minimal (just payment)
COMPLETE_MINIMAL: Dict[str, Any] = {
    "payment_data": {
        "token": "0xabcdef1234567890abcdef1234567890abcdef12",
        "provider": "usdc",
        "billing_address": {
            "name": "Jane Smith",
            "line_one": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "country": "US",
            "postal_code": "10001"
        }
    }
}

