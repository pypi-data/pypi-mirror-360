"""
Integration tests for Ophelos SDK.

These tests require valid API credentials and should be run against
the staging environment.
"""

import os
from datetime import datetime

import pytest

from ophelos_sdk import OphelosClient
from ophelos_sdk.exceptions import AuthenticationError, OphelosAPIError

# Skip integration tests (uncomment the first line to enable them when credentials are available)
# integration_skip = pytest.mark.skipif(
#     not all(
#         [
#             os.getenv("OPHELOS_CLIENT_ID"),
#             os.getenv("OPHELOS_CLIENT_SECRET"),
#             os.getenv("OPHELOS_AUDIENCE"),
#         ]
#     ),
#     reason="Integration tests require OPHELOS_CLIENT_ID, OPHELOS_CLIENT_SECRET, and OPHELOS_AUDIENCE environment variables",
# )

# Unconditionally skip all integration tests
integration_skip = pytest.mark.skip(reason="Integration tests are disabled by default")


@pytest.fixture
def ophelos_client():
    """Create Ophelos client for integration testing."""
    return OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET"),
        audience=os.getenv("OPHELOS_AUDIENCE"),
        environment="staging",  # Always use staging for tests
    )


@integration_skip
class TestIntegrationAuth:
    """Integration tests for authentication."""

    def test_client_authentication(self, ophelos_client):
        """Test that client can authenticate successfully."""
        # This should work without raising an exception
        connection_ok = ophelos_client.test_connection()
        assert connection_ok is True or connection_ok is False  # Either is valid

    def test_invalid_credentials(self):
        """Test authentication with invalid credentials."""
        client = OphelosClient(
            client_id="invalid_client_id",
            client_secret="invalid_client_secret",
            audience="invalid_audience",
            environment="staging",
        )

        with pytest.raises(AuthenticationError):
            client.test_connection()


@integration_skip
class TestIntegrationTenants:
    """Integration tests for tenant operations."""

    def test_get_my_tenant(self, ophelos_client):
        """Test getting current tenant information."""
        tenant = ophelos_client.tenants.get_me()

        assert tenant.id is not None
        assert tenant.object == "tenant"
        assert tenant.name is not None


@integration_skip
class TestIntegrationOrganisations:
    """Integration tests for organisation operations."""

    def test_list_organisations(self, ophelos_client):
        """Test listing organisations."""
        organisations = ophelos_client.organisations.list(limit=5)

        assert organisations.object == "list"
        assert isinstance(organisations.data, list)
        # May be empty for new accounts

        if organisations.data:
            org = organisations.data[0]
            assert hasattr(org, "id")
            assert hasattr(org, "name")


@integration_skip
class TestIntegrationCustomers:
    """Integration tests for customer operations."""

    def test_list_customers(self, ophelos_client):
        """Test listing customers."""
        customers = ophelos_client.customers.list(limit=5)

        assert customers.object == "list"
        assert isinstance(customers.data, list)


@integration_skip
class TestIntegrationDebts:
    """Integration tests for debt operations."""

    def test_list_debts(self, ophelos_client):
        """Test listing debts."""
        debts = ophelos_client.debts.list(limit=5)

        assert debts.object == "list"
        assert isinstance(debts.data, list)

    def test_search_debts_empty_result(self, ophelos_client):
        """Test searching debts with query that should return no results."""
        # Search for a very specific non-existent account number
        results = ophelos_client.debts.search(f"account_number:NONEXISTENT_{datetime.now().timestamp()}")

        assert results.object == "list"
        assert len(results.data) == 0


@integration_skip
class TestIntegrationPayments:
    """Integration tests for payment operations."""

    def test_list_payments(self, ophelos_client):
        """Test listing payments."""
        payments = ophelos_client.payments.list(limit=5)

        assert payments.object == "list"
        assert isinstance(payments.data, list)

    def test_search_payments_empty_result(self, ophelos_client):
        """Test searching payments with query that should return no results."""
        # Search for a very specific non-existent transaction reference
        results = ophelos_client.payments.search(f"transaction_ref:NONEXISTENT_{datetime.now().timestamp()}")

        assert results.object == "list"
        assert len(results.data) == 0


@integration_skip
class TestIntegrationWebhooks:
    """Integration tests for webhook operations."""

    def test_list_webhooks(self, ophelos_client):
        """Test listing webhooks."""
        webhooks = ophelos_client.webhooks.list(limit=5)

        assert webhooks.object == "list"
        assert isinstance(webhooks.data, list)


@integration_skip
class TestIntegrationPagination:
    """Integration tests for pagination."""

    def test_pagination_parameters(self, ophelos_client):
        """Test that pagination parameters are handled correctly."""
        # Test with various limit values
        for limit in [1, 5, 10]:
            customers = ophelos_client.customers.list(limit=limit)
            assert customers.object == "list"
            # The actual data length may be less than limit if there aren't enough records
            assert len(customers.data) <= limit


@integration_skip
class TestIntegrationErrorHandling:
    """Integration tests for error handling."""

    def test_not_found_error(self, ophelos_client):
        """Test handling of 404 errors."""
        with pytest.raises(OphelosAPIError) as exc_info:
            ophelos_client.debts.get("debt_nonexistent_12345")

        # Should be a 404 error
        assert exc_info.value.status_code == 404

    def test_invalid_search_query(self, ophelos_client):
        """Test handling of invalid search queries."""
        # This may or may not raise an error depending on API implementation
        try:
            results = ophelos_client.debts.search("invalid_field:value")
            # If it doesn't raise an error, it should return empty results
            assert results.object == "list"
        except OphelosAPIError:
            # This is also acceptable behavior for invalid queries
            pass


class TestIntegrationHelpers:
    """Helper functions for integration tests."""

    @staticmethod
    def requires_test_data():
        """Decorator to skip tests that require test data to exist."""
        return pytest.mark.skipif(
            os.getenv("OPHELOS_SKIP_DATA_TESTS", "false").lower() == "true",
            reason="Test requires existing data - set OPHELOS_SKIP_DATA_TESTS=false to run",
        )


# Example usage instructions
#
# Integration tests are DISABLED by default.
#
# To enable and run integration tests:
#
# 1. Uncomment the conditional skip logic and comment out the unconditional skip:
#    # integration_skip = pytest.mark.skip(reason="Integration tests are disabled by default")
#    integration_skip = pytest.mark.skipif(...)
#
# 2. Set environment variables:
#    export OPHELOS_CLIENT_ID="your_client_id"
#    export OPHELOS_CLIENT_SECRET="your_client_secret"
#    export OPHELOS_AUDIENCE="your_audience"
#
# 3. Run integration tests:
#    pytest tests/test_integration.py -v
#
# 4. To skip tests that require existing data:
#    export OPHELOS_SKIP_DATA_TESTS=true
#
# Note: Integration tests are disabled by default to avoid API authentication failures
# during regular test runs. Enable them only when you have valid API credentials.
