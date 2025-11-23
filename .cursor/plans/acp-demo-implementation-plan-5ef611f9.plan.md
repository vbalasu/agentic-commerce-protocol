<!-- 5ef611f9-395d-435d-94bd-a9c9835c5cda 7df358d3-e05d-4f97-a94c-c43c99ba4827 -->
# ACP Demo Implementation Plan

## Overview

Implement the critical Agentic Commerce Protocol (ACP) features for a stablecoin-based e-commerce demo. The demo will run on Databricks and demonstrate autonomous AI agent transactions using USDC.

The core UI will be implemented as a Databricks App. The app will display products from a product catalog, implemented as a Delta table in Unity Catalog.

## Key Features to Implement

### 1. Checkout Session Management (Core Flow)

- **POST /checkout_sessions** - Create a new checkout session
- Accept items, optional buyer info, optional fulfillment address
- Return authoritative cart state with line items, totals, fulfillment options
- Status: `not_ready_for_payment` or `ready_for_payment`

- **POST /checkout_sessions/{id}** - Update checkout session
- Update items, fulfillment address, or fulfillment option
- Return updated authoritative cart state
- Recalculate totals based on changes

- **GET /checkout_sessions/{id}** - Retrieve checkout session
- Return current authoritative state
- Include all cart details, status, messages

- **POST /checkout_sessions/{id}/complete** - Complete checkout
- Accept payment_data with stablecoin transaction details
- Create order on success
- Return completed session with order information
- Status: `completed`

### 2. Data Models

- **CheckoutSession**: id, status, currency, line_items, totals, fulfillment_options, fulfillment_address, buyer, payment_provider, messages, links
- **LineItem**: item details with pricing breakdown (base_amount, discount, subtotal, tax, total)
- **FulfillmentOption**: shipping or digital options with pricing
- **PaymentData**: adapted for stablecoin (token/transaction_hash, provider, billing_address)
- **Order**: id, checkout_session_id, permalink_url

### 3. Stablecoin Payment Integration

- Adapt PaymentData schema for stablecoin transactions
- Support USDC payment method
- Generate or accept stablecoin transaction details
- Verify on-chain transaction before order confirmation

### 4. Implementation Structure

- Databricks Model Serving endpoint or Notebook-based API
- REST API endpoints matching ACP OpenAPI spec
- Mock product catalog for demonstration
- Basic stablecoin payment simulation (or integration with wallet provider)

## Files to Create/Modify

1. **API Endpoints** (`api/checkout.py` or similar)

- Implement all 4 core endpoints
- Request/response validation
- Business logic for cart calculations

2. **Data Models** (`models/checkout.py`)

- Pydantic models matching ACP schemas
- Stablecoin-specific payment models

3. **Service Layer** (`services/checkout_service.py`)

- Cart calculation logic
- Fulfillment option generation
- Order creation
- Stablecoin payment processing

4. **Configuration** (`config.py`)

- API version
- Currency settings
- Payment provider config

5. **Demo Product Catalog** (`data/products.py` or database)

- Sample products for testing
- Product metadata

## Technical Considerations

- Use OpenAPI 3.1.0 spec as reference
- Implement proper error handling (4XX, 5XX responses), including x402 for payment required
- Support required headers: Authorization, API-Version, Idempotency-Key
- Return authoritative cart state on all operations
- Handle status transitions: not_ready_for_payment → ready_for_payment → completed
- Support both shipping and digital fulfillment options

## Stablecoin-Specific Adaptations

- PaymentData.token can represent transaction hash or payment address
- Payment provider enum may include "stablecoin" or "usdc" 
- Payment verification may require blockchain interaction or mock verification
- Billing address still required for compliance

## Testing Strategy

- Unit tests for cart calculations
- Integration tests for API endpoints
- Example requests matching ACP examples
- Test stablecoin payment flow end-to-end
- Use Phantom wallet for testing stablecoin transactions

### To-dos

- [ ] Create project directory structure (api/, models/, services/, config.py) and set up Databricks-compatible Python environment
- [ ] Create Pydantic models for CheckoutSession, LineItem, FulfillmentOption, PaymentData (stablecoin-adapted), Order, and request/response schemas matching ACP spec
- [ ] Implement checkout service with cart calculation logic, fulfillment option generation, totals calculation, and order creation
- [ ] Create REST API endpoints: POST /checkout_sessions (create), POST /checkout_sessions/{id} (update), GET /checkout_sessions/{id} (retrieve), POST /checkout_sessions/{id}/complete (complete with stablecoin payment)
- [ ] Integrate stablecoin payment processing - accept payment_data, verify transaction (mock or real), create order on success
- [ ] Create mock product catalog with sample products (e.g., hoodies, t-shirts) for demonstration purposes
- [ ] Implement proper error responses (4XX, 5XX) with ACP-compliant Error schema and appropriate status codes
- [ ] Create example requests/responses and basic tests to validate the implementation matches ACP spec