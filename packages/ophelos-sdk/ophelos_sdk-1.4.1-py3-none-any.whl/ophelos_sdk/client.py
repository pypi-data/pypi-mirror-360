"""
Main Ophelos API client.
"""

from typing import Optional, Union

from .auth import OAuth2Authenticator, StaticTokenAuthenticator
from .http_client import HTTPClient
from .resources import (
    CommunicationsResource,
    ContactDetailsResource,
    CustomersResource,
    DebtsResource,
    InvoicesResource,
    LineItemsResource,
    OrganisationsResource,
    PaymentPlansResource,
    PaymentsResource,
    PayoutsResource,
    TenantsResource,
    WebhooksResource,
)


class OphelosClient:
    """
    Main client for the Ophelos API.

    This client provides access to all Ophelos API resources and handles
    authentication, HTTP requests, and response parsing.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        audience: Optional[str] = None,
        environment: str = "development",
        timeout: int = 30,
        max_retries: int = 3,
        tenant_id: Optional[str] = None,
        access_token: Optional[str] = None,
        version: Optional[str] = "2025-04-01",
    ):
        """
        Initialize the Ophelos API client.

        Args:
            client_id: OAuth2 client ID (required if access_token not provided)
            client_secret: OAuth2 client secret (required if access_token not provided)
            audience: API audience/identifier (required if access_token not provided)
            environment: "development", "staging", or "production"
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            tenant_id: Optional tenant ID to include in all requests as OPHELOS_TENANT_ID header
            access_token: Optional pre-obtained access token (bypasses OAuth2 flow)
            version: API version to use (defaults to '2025-04-01', set to None to omit header)

        Note:
            Retry requests automatically use exponential backoff with jitter (0-1.5s randomness)
            to prevent thundering herd problems when multiple clients retry simultaneously.

        Example:
            ```python
            # OAuth2 flow (default)
            client = OphelosClient(
                client_id="your_client_id",
                client_secret="your_client_secret",
                audience="your_audience",
                environment="development",
                tenant_id="your_tenant_id"  # Optional: adds OPHELOS_TENANT_ID header
            )

            # Direct access token
            client = OphelosClient(
                access_token="your_access_token",
                environment="development",
                tenant_id="your_tenant_id"  # Optional: adds OPHELOS_TENANT_ID header
            )

            # Custom API version
            client = OphelosClient(
                access_token="your_access_token",
                environment="development",
                version="2024-12-01"
            )
            ```
        """
        if environment == "production":
            base_url = "https://api.ophelos.com"
        elif environment == "development":
            base_url = "http://api.localhost:3000"
        else:  # staging (default)
            base_url = "https://api.ophelos.dev"

        # Choose authenticator based on provided parameters
        self.authenticator: Union[OAuth2Authenticator, StaticTokenAuthenticator]
        if access_token:
            self.authenticator = StaticTokenAuthenticator(access_token=access_token)
        else:
            if not all([client_id, client_secret, audience]):
                raise ValueError(
                    "client_id, client_secret, and audience are required when access_token is not provided"
                )
            # mypy: At this point we know these are not None due to the check above
            assert client_id is not None
            assert client_secret is not None
            assert audience is not None
            self.authenticator = OAuth2Authenticator(
                client_id=client_id,
                client_secret=client_secret,
                audience=audience,
                environment=environment,
            )

        self.http_client = HTTPClient(
            authenticator=self.authenticator,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            tenant_id=tenant_id,
            version=version,
        )
        self.debts = DebtsResource(self.http_client)
        self.customers = CustomersResource(self.http_client)
        self.contact_details = ContactDetailsResource(self.http_client)
        self.organisations = OrganisationsResource(self.http_client)
        self.payments = PaymentsResource(self.http_client)
        self.invoices = InvoicesResource(self.http_client)
        self.line_items = LineItemsResource(self.http_client)
        self.webhooks = WebhooksResource(self.http_client)
        self.payment_plans = PaymentPlansResource(self.http_client)
        self.communications = CommunicationsResource(self.http_client)
        self.payouts = PayoutsResource(self.http_client)
        self.tenants = TenantsResource(self.http_client)

    def test_connection(self) -> bool:
        """
        Test the API connection by making a simple authenticated request.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.tenants.get_me()
            return True
        except Exception:
            return False
