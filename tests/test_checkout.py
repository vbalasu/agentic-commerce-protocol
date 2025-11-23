"""
Tests for checkout API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..examples.example_requests import (
    CREATE_MINIMAL,
    CREATE_WITH_ADDRESS,
    CREATE_WITH_BUYER,
    UPDATE_FULFILLMENT_OPTION,
    COMPLETE_WITH_PAYMENT,
)

client = TestClient(app)

# Test headers
TEST_HEADERS = {
    "Authorization": "Bearer test_api_key",
    "API-Version": "2025-09-29",
    "Content-Type": "application/json",
}


def test_create_checkout_session_minimal():
    """Test creating a checkout session with minimal data"""
    response = client.post(
        "/checkout_sessions",
        json=CREATE_MINIMAL,
        headers=TEST_HEADERS
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] in ["not_ready_for_payment", "ready_for_payment"]
    assert len(data["line_items"]) > 0
    assert len(data["totals"]) > 0
    assert len(data["fulfillment_options"]) >= 0
    assert "currency" in data
    assert "payment_provider" in data


def test_create_checkout_session_with_address():
    """Test creating a checkout session with fulfillment address"""
    response = client.post(
        "/checkout_sessions",
        json=CREATE_WITH_ADDRESS,
        headers=TEST_HEADERS
    )
    assert response.status_code == 201
    data = response.json()
    assert data["fulfillment_address"] is not None
    assert len(data["fulfillment_options"]) > 0  # Should have shipping options


def test_create_checkout_session_with_buyer():
    """Test creating a checkout session with buyer info"""
    response = client.post(
        "/checkout_sessions",
        json=CREATE_WITH_BUYER,
        headers=TEST_HEADERS
    )
    assert response.status_code == 201
    data = response.json()
    assert data["buyer"] is not None
    assert data["buyer"]["email"] == "john.doe@example.com"


def test_get_checkout_session():
    """Test retrieving a checkout session"""
    # First create a session
    create_response = client.post(
        "/checkout_sessions",
        json=CREATE_MINIMAL,
        headers=TEST_HEADERS
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]
    
    # Then retrieve it
    get_response = client.get(
        f"/checkout_sessions/{session_id}",
        headers=TEST_HEADERS
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == session_id


def test_get_checkout_session_not_found():
    """Test retrieving a non-existent checkout session"""
    response = client.get(
        "/checkout_sessions/nonexistent",
        headers=TEST_HEADERS
    )
    assert response.status_code == 404


def test_update_checkout_session():
    """Test updating a checkout session"""
    # First create a session
    create_response = client.post(
        "/checkout_sessions",
        json=CREATE_WITH_ADDRESS,
        headers=TEST_HEADERS
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]
    
    # Update fulfillment option
    update_response = client.post(
        f"/checkout_sessions/{session_id}",
        json=UPDATE_FULFILLMENT_OPTION,
        headers=TEST_HEADERS
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["fulfillment_option_id"] == "fulfillment_option_456"


def test_complete_checkout_session():
    """Test completing a checkout session with payment"""
    # First create a session with address
    create_response = client.post(
        "/checkout_sessions",
        json=CREATE_WITH_ADDRESS,
        headers=TEST_HEADERS
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]
    
    # Select a fulfillment option
    fulfillment_options = create_response.json()["fulfillment_options"]
    if fulfillment_options:
        fulfillment_option_id = fulfillment_options[0]["id"]
        update_response = client.post(
            f"/checkout_sessions/{session_id}",
            json={"fulfillment_option_id": fulfillment_option_id},
            headers=TEST_HEADERS
        )
        assert update_response.status_code == 200
    
    # Complete the checkout
    complete_response = client.post(
        f"/checkout_sessions/{session_id}/complete",
        json=COMPLETE_WITH_PAYMENT,
        headers=TEST_HEADERS
    )
    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["status"] == "completed"
    assert "order" in data
    assert data["order"]["id"] is not None
    assert data["order"]["checkout_session_id"] == session_id


def test_cancel_checkout_session():
    """Test canceling a checkout session"""
    # First create a session
    create_response = client.post(
        "/checkout_sessions",
        json=CREATE_MINIMAL,
        headers=TEST_HEADERS
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]
    
    # Cancel it
    cancel_response = client.post(
        f"/checkout_sessions/{session_id}/cancel",
        headers=TEST_HEADERS
    )
    assert cancel_response.status_code == 200
    data = cancel_response.json()
    assert data["status"] == "canceled"


def test_missing_authorization():
    """Test that missing authorization header returns 401"""
    headers = TEST_HEADERS.copy()
    del headers["Authorization"]
    response = client.post(
        "/checkout_sessions",
        json=CREATE_MINIMAL,
        headers=headers
    )
    assert response.status_code == 401


def test_missing_api_version():
    """Test that missing API version header returns 400"""
    headers = TEST_HEADERS.copy()
    del headers["API-Version"]
    response = client.post(
        "/checkout_sessions",
        json=CREATE_MINIMAL,
        headers=headers
    )
    assert response.status_code == 400


def test_invalid_product():
    """Test creating checkout session with invalid product ID"""
    response = client.post(
        "/checkout_sessions",
        json={
            "items": [
                {
                    "id": "invalid_product_id",
                    "quantity": 1
                }
            ]
        },
        headers=TEST_HEADERS
    )
    assert response.status_code == 201  # Session created but with errors
    data = response.json()
    assert len(data["messages"]) > 0
    assert any(msg["type"] == "error" for msg in data["messages"])


def test_empty_items():
    """Test creating checkout session with empty items"""
    response = client.post(
        "/checkout_sessions",
        json={"items": []},
        headers=TEST_HEADERS
    )
    assert response.status_code == 422  # Validation error


def test_complete_without_payment():
    """Test completing checkout session without payment data"""
    create_response = client.post(
        "/checkout_sessions",
        json=CREATE_WITH_ADDRESS,
        headers=TEST_HEADERS
    )
    session_id = create_response.json()["id"]
    
    response = client.post(
        f"/checkout_sessions/{session_id}/complete",
        json={},
        headers=TEST_HEADERS
    )
    assert response.status_code == 422  # Validation error

