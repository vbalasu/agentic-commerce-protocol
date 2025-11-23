"""
ACP Checkout API Endpoints
"""
from fastapi import APIRouter, HTTPException, Header, status
from typing import Optional

from models.checkout import (
    CheckoutSession,
    CheckoutSessionWithOrder,
    CheckoutSessionCreateRequest,
    CheckoutSessionUpdateRequest,
    CheckoutSessionCompleteRequest,
    Error,
    ErrorType,
)
from services.checkout_service import (
    create_checkout_session,
    update_checkout_session,
    get_checkout_session,
    complete_checkout_session,
    cancel_checkout_session,
)
from config import settings

router = APIRouter(prefix="/checkout_sessions", tags=["CheckoutSessions"])


def _validate_api_version(api_version: Optional[str]) -> None:
    """Validate API version header"""
    if not api_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API-Version header is required"
        )
    if api_version != settings.api_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported API version: {api_version}. Expected: {settings.api_version}"
        )


def _validate_authorization(authorization: Optional[str]) -> None:
    """Validate authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required"
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must start with 'Bearer '"
        )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CheckoutSession,
    responses={
        201: {"description": "Created"},
        400: {"model": Error, "description": "Client error"},
        500: {"model": Error, "description": "Server error"},
    }
)
async def create_checkout_session_endpoint(
    request: CheckoutSessionCreateRequest,
    authorization: str = Header(..., alias="Authorization"),
    api_version: str = Header(..., alias="API-Version"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: Optional[str] = Header(None, alias="Request-Id"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language"),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
):
    """
    Create a new checkout session
    
    Initializes a new checkout session from items and (optionally) buyer and fulfillment info.
    MUST return 201 with a rich, authoritative cart state.
    """
    _validate_authorization(authorization)
    _validate_api_version(api_version)
    
    try:
        session = create_checkout_session(request)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/{checkout_session_id}",
    status_code=status.HTTP_200_OK,
    response_model=CheckoutSession,
    responses={
        200: {"description": "Updated session"},
        400: {"model": Error, "description": "Client error"},
        404: {"model": Error, "description": "Session not found"},
        500: {"model": Error, "description": "Server error"},
    }
)
async def update_checkout_session_endpoint(
    checkout_session_id: str,
    request: CheckoutSessionUpdateRequest,
    authorization: str = Header(..., alias="Authorization"),
    api_version: str = Header(..., alias="API-Version"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: Optional[str] = Header(None, alias="Request-Id"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language"),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
):
    """
    Update a checkout session
    
    Applies changes (items, fulfillment address, fulfillment option) and returns an updated authoritative cart state.
    """
    _validate_authorization(authorization)
    _validate_api_version(api_version)
    
    try:
        session = update_checkout_session(checkout_session_id, request)
        return session
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/{checkout_session_id}",
    status_code=status.HTTP_200_OK,
    response_model=CheckoutSession,
    responses={
        200: {"description": "Current session"},
        404: {"model": Error, "description": "Session not found"},
    }
)
async def get_checkout_session_endpoint(
    checkout_session_id: str,
    authorization: str = Header(..., alias="Authorization"),
    api_version: str = Header(..., alias="API-Version"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language"),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
):
    """
    Retrieve a checkout session
    
    Returns the latest authoritative state for the checkout session.
    """
    _validate_authorization(authorization)
    _validate_api_version(api_version)
    
    session = get_checkout_session(checkout_session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checkout session {checkout_session_id} not found"
        )
    
    return session


@router.post(
    "/{checkout_session_id}/complete",
    status_code=status.HTTP_200_OK,
    response_model=CheckoutSessionWithOrder,
    responses={
        200: {"description": "Completed session with order"},
        400: {"model": Error, "description": "Client error"},
        402: {"model": Error, "description": "Payment required"},
        404: {"model": Error, "description": "Session not found"},
        500: {"model": Error, "description": "Server error"},
    }
)
async def complete_checkout_session_endpoint(
    checkout_session_id: str,
    request: CheckoutSessionCompleteRequest,
    authorization: str = Header(..., alias="Authorization"),
    api_version: str = Header(..., alias="API-Version"),
    content_type: str = Header("application/json", alias="Content-Type"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: Optional[str] = Header(None, alias="Request-Id"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language"),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
):
    """
    Complete a checkout session
    
    Finalizes the checkout by applying a payment method. MUST create an order and return completed state on success.
    """
    _validate_authorization(authorization)
    _validate_api_version(api_version)
    
    try:
        session_with_order = complete_checkout_session(checkout_session_id, request)
        return session_with_order
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "payment" in error_msg or "verification" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/{checkout_session_id}/cancel",
    status_code=status.HTTP_200_OK,
    response_model=CheckoutSession,
    responses={
        200: {"description": "Canceled session"},
        400: {"model": Error, "description": "Client error"},
        404: {"model": Error, "description": "Session not found"},
        405: {"model": Error, "description": "Not cancelable (already completed/canceled)"},
    }
)
async def cancel_checkout_session_endpoint(
    checkout_session_id: str,
    authorization: str = Header(..., alias="Authorization"),
    api_version: str = Header(..., alias="API-Version"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language"),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: Optional[str] = Header(None, alias="Request-Id"),
):
    """
    Cancel a checkout session
    
    Cancels a session if not already completed or canceled.
    """
    _validate_authorization(authorization)
    _validate_api_version(api_version)
    
    try:
        session = cancel_checkout_session(checkout_session_id)
        return session
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "cannot cancel" in error_msg or "already completed" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

