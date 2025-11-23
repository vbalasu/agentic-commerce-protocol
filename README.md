# Agentic Commerce Protocol: Stablecoin Demo on Databricks

This project demonstrates how to build an AI Agent capable of autonomously executing e-commerce transactions using the **Agentic Commerce Protocol (ACP)** and **Stablecoins** (e.g., USDC).

Built on the **Databricks Data Intelligence Platform**, this demo highlights the intersection of Generative AI, open commerce standards, and decentralized finance.

## 🚀 Overview

The [Agentic Commerce Protocol](https://www.agenticcommerce.dev/) is an open standard that enables AI agents to discover products and transact with businesses programmatically.

This implementation extends the standard flow by utilizing **Stablecoins** for settlement, offering a fast, low-fee, and borderless payment method ideal for autonomous agents.

### Key Features
* **ACP Compliant:** Implements the core ACP specification (`/manage_checkout`, etc.) for standardization.
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

* **Databricks Workspace:** Access to a workspace with compute enabled.
* **LLM Endpoint:** Access to a foundational model (e.g., DBRX, Llama 3) via Databricks Model Serving.
* **Wallet/Payment Provider:** A configured wallet (e.g., Coinbase Developer Platform, Stripe Crypto) or mock environment for handling stablecoin flows.
* **ACP API Keys:** (If connecting to a live ACP merchant)

## ⚡ Quick Start

### 1. Setup Environment
Cloning this repository into your Databricks workspace (if not already done).

### 2. Configure Secrets
Securely store your API keys and wallet private keys using Databricks Secrets.
```bash
databricks secrets create-scope --scope acp_demo
databricks secrets put --scope acp_demo --key wallet_private_key


#### References

- https://www.agenticcommerce.dev/