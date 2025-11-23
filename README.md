# Agentic Commerce Protocol: Stablecoin Demo on Databricks

This project demonstrates how to build an AI Agent capable of autonomously executing e-commerce transactions using the **Agentic Commerce Protocol (ACP)** and **Stablecoins** (e.g., USDC).

Built on the **Databricks Data Intelligence Platform**, this demo highlights the intersection of Generative AI, open commerce standards, and decentralized finance.

## 🚀 Overview

The [Agentic Commerce Protocol](https://www.agenticcommerce.dev/) is an open standard that enables AI agents to discover products and transact with businesses programmatically.

This implementation extends the standard flow by utilizing **Stablecoins** for settlement, offering a fast, low-fee, and borderless payment method ideal for autonomous agents.

### Key Features
* **ACP Compliant:** Implements the core ACP specification (`/checkout_sessions`, etc.) for standardization.
* **Databricks Backend:** Leverages Databricks Model Serving or Notebook jobs to host the agent logic and commerce endpoints.
* **Stablecoin Native:** Completes purchases using crypto (USDC) rather than traditional credit card rails, demonstrating modern agent-to-business settlement.

## 🛠️ Architecture

The flow of a transaction in this demo is as follows:

1.  **User Intent:** User asks the Agent (hosted on Databricks) to buy a specific item (e.g., *"Buy me the black hoodie using USDC"*).
2.  **Discovery:** The Agent queries the ACP-enabled product catalog.
3.  **Checkout Negotiation:** The Agent utilizes the ACP endpoints to create a cart and update shipping details.
4.  **Payment Generation:** instead of a credit card token, the Agent generates a signed stablecoin transaction (or requests a payment address).
5.  **Settlement:** The transaction is verified on-chain, and the order is confirmed.

## 📋 Prerequisites

Before running this demo, ensure you have:

* **Python 3.9+:** Python runtime environment
* **Databricks Workspace:** Access to a workspace with compute enabled (optional for local development).
* **LLM Endpoint:** Access to a foundational model (e.g., DBRX, Llama 3) via Databricks Model Serving (optional).
* **Wallet/Payment Provider:** A configured wallet (e.g., Coinbase Developer Platform, Stripe Crypto) or mock environment for handling stablecoin flows.

## ⚡ Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd agentic-commerce-protocol

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file (optional, defaults are provided):

```bash
# API Configuration
API_VERSION=2025-09-29

# Currency
DEFAULT_CURRENCY=USD

# Payment Provider
PAYMENT_PROVIDER=usdc
SUPPORTED_PAYMENT_METHODS=["usdc"]

# Stablecoin Configuration
STABLECOIN_NETWORK=ethereum
MOCK_PAYMENT_VERIFICATION=true  # Set to false for real blockchain verification
```

### 3. Run the API Server

```bash
# Run with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python main.py
```

The API will be available at `http://localhost:8000`

### 4. API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📚 API Endpoints

### Create Checkout Session
```bash
POST /checkout_sessions
Headers:
  Authorization: Bearer <api_key>
  API-Version: 2025-09-29
  Content-Type: application/json

Body:
{
  "items": [
    {
      "id": "item_001",
      "quantity": 1
    }
  ],
  "fulfillment_address": {
    "name": "John Doe",
    "line_one": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "country": "US",
    "postal_code": "94102"
  }
}
```

### Update Checkout Session
```bash
POST /checkout_sessions/{checkout_session_id}
Headers:
  Authorization: Bearer <api_key>
  API-Version: 2025-09-29

Body:
{
  "fulfillment_option_id": "fulfillment_shipping_standard"
}
```

### Get Checkout Session
```bash
GET /checkout_sessions/{checkout_session_id}
Headers:
  Authorization: Bearer <api_key>
  API-Version: 2025-09-29
```

### Complete Checkout Session
```bash
POST /checkout_sessions/{checkout_session_id}/complete
Headers:
  Authorization: Bearer <api_key>
  API-Version: 2025-09-29
  Content-Type: application/json

Body:
{
  "payment_data": {
    "token": "0x1234567890abcdef...",  # Transaction hash
    "provider": "usdc",
    "billing_address": {
      "name": "John Doe",
      "line_one": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "country": "US",
      "postal_code": "94102"
    }
  }
}
```

### Cancel Checkout Session
```bash
POST /checkout_sessions/{checkout_session_id}/cancel
Headers:
  Authorization: Bearer <api_key>
  API-Version: 2025-09-29
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_checkout.py
```

## 📁 Project Structure

```
agentic-commerce-protocol/
├── api/
│   ├── __init__.py
│   └── checkout.py          # API endpoints
├── models/
│   ├── __init__.py
│   └── checkout.py          # Pydantic data models
├── services/
│   ├── __init__.py
│   └── checkout_service.py  # Business logic
├── data/
│   ├── __init__.py
│   └── products.py          # Product catalog
├── examples/
│   ├── __init__.py
│   └── example_requests.py # Example API requests
├── tests/
│   ├── __init__.py
│   ├── test_checkout.py     # API endpoint tests
│   └── test_checkout_service.py  # Service logic tests
├── config.py                # Configuration
├── main.py                  # FastAPI application
├── requirements.txt         # Python dependencies
└── README.md
```

## 🔧 Configuration

See `config.py` for all configuration options. Key settings:

- `api_version`: ACP API version (default: "2025-09-29")
- `default_currency`: Default currency (default: "USD")
- `payment_provider`: Payment provider (default: "usdc")
- `mock_payment_verification`: Use mock payment verification (default: True)

## 🎯 Example Usage

See `examples/example_requests.py` for complete example requests matching the ACP specification.

## 📖 References

- [Agentic Commerce Protocol](https://www.agenticcommerce.dev/)
- [ACP Specification](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol)
- [OpenAI ACP Documentation](https://developers.openai.com/commerce/)
- [Stripe Agentic Commerce Documentation](https://docs.stripe.com/agentic-commerce)

## 📝 License

This project is licensed under the Apache 2.0 License.
