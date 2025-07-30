# Ophelos Python SDK

Python SDK for the Ophelos API - a comprehensive debt management and customer communication platform.

## Installation

### From PyPI (when published)

```bash
pip install ophelos-sdk
```

### From Local Distribution

```bash
# Install from wheel (recommended)
pip install dist/ophelos_sdk-1.4.1-py3-none-any.whl

# Or install from source distribution
pip install dist/ophelos-sdk-1.4.1.tar.gz

# Or install in development mode
pip install -e .
```

### Requirements Files

The project includes separate requirements files:

- **`requirements.txt`** - Runtime dependencies only (for end users)
- **`requirements-dev.txt`** - Development dependencies only
- **`pyproject.toml`** - Complete dependency specification (recommended)

```bash
# For end users (runtime only)
pip install -r requirements.txt

# For developers (includes testing, linting, formatting tools)
pip install -r requirements-dev.txt

# Or install everything via pyproject.toml (recommended)
pip install -e ".[dev]"
```

## Quick Start

```python
from ophelos_sdk import OphelosClient
from ophelos_sdk.models import Customer, Debt

# Initialize client with your credentials
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="staging",  # or "production"
    version="2025-04-01"  # API version (default: "2025-04-01")
)

# Option 1: Create using dictionaries (traditional approach)
customer = client.customers.create({
    "first_name": "John",
    "last_name": "Doe",
    "contact_details": [
        {"type": "email", "value": "john.doe@example.com", "primary": True}
    ]
})

# Option 2: Create using model instances (new approach)
from ophelos_sdk.models import Customer, ContactDetail

customer_model = Customer(
    id="temp_cust_123",  # Temporary ID
    first_name="Jane",
    last_name="Smith",
    contact_details=[
        ContactDetail(
            id="temp_cd_123",
            type="email",
            value="jane.smith@example.com",
            primary=True
        )
    ]
)

# Pass model directly to API - automatic conversion to API body
customer = client.customers.create(customer_model)

# Create a debt using model instance
debt_model = Debt(
    id="temp_debt_123",
    customer=customer.id,  # Use real customer ID
    organisation="org_123",
    currency="GBP",
    account_number="ACC-001",
    kind="purchased"
)

debt = client.debts.create(debt_model)

# Prepare the debt for processing
client.debts.ready(debt.id)
```

📋 **For comprehensive usage examples and advanced features, see [USAGE.md](USAGE.md)**

## Key Features

- **Complete API Coverage**: All Ophelos API endpoints with comprehensive test coverage
- **Type Safety**: Full type hints and Pydantic models with automatic API body generation
- **Model-First Approach**: Create and pass Pydantic model instances directly to API calls
- **Request/Response Transparency**: Access complete HTTP request and response details from any model instance
- **Smart Field Management**: Automatic exclusion of server-generated fields and intelligent relationship handling
- **Comprehensive Error Handling**: Full debugging context for all error types (API, timeout, parsing, unexpected)
- **Authentication**: Automatic OAuth2 token management with thread-safe token caching
- **Multi-Tenant Support**: Automatic tenant header injection
- **Pagination**: Built-in pagination support with generators for memory-efficient iteration
- **Webhooks**: Webhook event handling and validation with signature verification
- **Concurrent Safe**: Thread-safe for use with concurrent request patterns

## Request/Response Transparency

Every model instance returned by the SDK includes complete HTTP request and response details:

```python
# Get a customer
customer = client.customers.get('cust_123')

# Access request details
print(customer.request_info)
# Output: {
#   'method': 'GET',
#   'url': 'https://api.ophelos.com/customers/cust_123',
#   'headers': {'Authorization': 'Bearer ...', 'Ophelos-Version': '2025-04-01'},
#   'body': None
# }

# Access response details
print(customer.response_info)
# Output: {
#   'status_code': 200,
#   'headers': {'Content-Type': 'application/json', ...},
#   'url': 'https://api.ophelos.com/customers/cust_123'
# }

# Access raw response object for advanced use cases
response = customer.response_raw
print(f"Response took: {response.elapsed.total_seconds()} seconds")
print(f"Server: {response.headers.get('Server')}")

# Works with all operations - create, update, list, search
debts = client.debts.list(limit=10)
for debt in debts.data:
    print(f"Debt {debt.id} response time: {debt.response_raw.elapsed}")

# Also works with paginated responses
print(f"List request: {debts.request_info}")
print(f"List response status: {debts.response_info['status_code']}")
```

This transparency enables:
- **Request debugging**: See exactly what was sent to the API (works for errors too)
- **Response monitoring**: Track response times, status codes, headers
- **Error diagnosis**: Full request context available even for timeouts and failures
- **Audit trails**: Log complete request/response details for compliance
- **Performance analysis**: Monitor API response times and patterns

## Model-First API Usage

The SDK supports both traditional dictionary-based API calls and a modern model-first approach:

```python
from ophelos_sdk.models import Customer, Debt, ContactDetail

# Create models with type safety and validation
customer = Customer(
    id="temp_123",  # Temporary ID for creation
    first_name="John",
    last_name="Doe",
    contact_details=[
        ContactDetail(
            id="temp_cd_1",
            type="email",
            value="john@example.com",
            primary=True
        )
    ]
)

# Pass model directly to API - automatic conversion
created_customer = client.customers.create(customer)

# Smart API body generation - automatically excludes server-generated fields
api_body = customer.to_api_body()
print(api_body)
# Output: {
#   "first_name": "John",
#   "last_name": "Doe",
#   "contact_details": [
#     {"type": "email", "value": "john@example.com", "primary": True}
#   ]
# }
# Note: id, object, created_at, updated_at are automatically excluded
```

## Authentication

### Option 1: OAuth2 Client Credentials (Recommended)

```python
# OAuth2 authentication (automatic token management)
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="production",  # "development", "staging", or "production"
    version="2025-04-01"  # API version (default: "2025-04-01")
)
```

### Option 2: Direct Access Token

```python
# Direct access token authentication
client = OphelosClient(
    access_token="your_access_token",
    version="2025-04-01"
)
```

### Multi-Tenant Support

```python
# Initialize client with tenant ID
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="production",
    tenant_id="tenant_123"  # Automatically adds OPHELOS_TENANT_ID header
)
```

Contact Ophelos support to obtain credentials.

## Examples

### Working with Debts

```python
from ophelos_sdk.models import Debt

# List debts with pagination
debts = client.debts.list(limit=10, expand=["customer"])

# Access request/response details
print(f"Request URL: {debts.request_info['url']}")
print(f"Response time: {debts.response_raw.elapsed.total_seconds()}s")

# Search debts
results = client.debts.search("status:paying AND updated_at>=2024-01-01")

# Get debt details
debt = client.debts.get("debt_123", expand=["customer", "payments"])

# Create using model instance
debt_model = Debt(
    id="temp_debt",
    customer="cust_123",
    organisation="org_123",
    currency="GBP",
    account_number="ACC-001",
    kind="purchased"
)

created_debt = client.debts.create(debt_model)

# Access creation request details
print(f"Created debt with request: {created_debt.request_info}")
```

### Working with Contact Details

```python
from ophelos_sdk.models import ContactDetail

# Create contact detail for a customer
contact = client.contact_details.create("cust_123", {
    "type": "email",
    "value": "john.doe@example.com",
    "primary": True,
    "usage": "billing"
})

# Get specific contact detail
contact_detail = client.contact_details.get("cust_123", contact.id)

# Update contact detail
updated_contact = client.contact_details.update("cust_123", contact.id, {
    "usage": "notifications"
})

# List all contact details for customer
contacts = client.contact_details.list("cust_123")

# Access request/response details
print(f"Contact creation time: {contact.response_raw.elapsed.total_seconds()}s")
print(f"List request: {contacts.request_info['url']}")
```

### Error Handling with Request/Response Debugging

```python
from ophelos_sdk.exceptions import (
    OphelosAPIError, AuthenticationError, TimeoutError,
    ParseError, UnexpectedError
)

try:
    debt = client.debts.get("invalid_debt_id")
except OphelosAPIError as e:
    print(f"API Error: {e.message} (Status: {e.status_code})")
    print(f"Request: {e.request_info}")  # Full request details
    print(f"Response time: {e.response_raw.elapsed.total_seconds()}s")
except TimeoutError as e:
    print(f"Request timed out: {e.message}")
    print(f"Request details: {e.request_info}")  # Available even for timeouts
except UnexpectedError as e:
    print(f"Unexpected error: {e.message}")
    print(f"Original error: {e.original_error}")
    print(f"Request context: {e.request_info}")
```

### Webhook Handling

```python
from ophelos_sdk.webhooks import WebhookHandler

# Initialize webhook handler
webhook_handler = WebhookHandler("your_webhook_secret")

# Validate and parse webhook
try:
    event = webhook_handler.verify_and_parse(
        payload=request.body,
        signature=request.headers.get("Ophelos-Signature")
    )

    if event.type == "debt.created":
        print(f"New debt created: {event.data.id}")

except Exception as e:
    print(f"Webhook validation failed: {e}")
```

## API Resources

- **Debts**: Create, update, and manage debts with lifecycle operations
- **Customers**: Customer CRUD operations with contact detail management
- **Contact Details**: Manage customer contact information (email, phone, address)
- **Payments**: Payment processing and tracking
- **Organisations**: Organisation setup and configuration
- **Invoices**: Invoice creation and management
- **Communications**: Communication tracking and management
- **Payment Plans**: Payment plan management
- **Webhooks**: Webhook management and validation

## Pagination

```python
# List with automatic pagination
debts = client.debts.list(limit=50)

# Check pagination status
if debts.has_more:
    print(f"Total count: {debts.total_count}")

    # Navigate using cursors
    next_page = client.debts.list(limit=50, after=debts.pagination['next']['after'])

# Memory-efficient iteration
for debt in client.debts.iterate(limit_per_page=100):
    print(f"Processing debt: {debt.id}")
```

## Development

```bash
# Clone and install
git clone https://github.com/ophelos/ophelos-python-sdk.git
cd ophelos-python-sdk
pip install -e ".[dev]"

# Run tests (250+ tests including 143 model tests)
pytest

# Run linting
flake8 ophelos_sdk/
mypy ophelos_sdk/
black ophelos_sdk/ --line-length 120
```

## Support

- **API Reference**: [https://api.ophelos.com](https://api.ophelos.com)
- **Support Email**: support@ophelos.com
- **GitHub Issues**: [GitHub Issues](https://github.com/tomasz-oph/ophelos_python_sdk/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
