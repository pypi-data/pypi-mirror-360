"""
Unit tests for Ophelos SDK resource managers.
"""

from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.models import ContactDetail, Customer, Debt, PaginatedResponse, Payment
from ophelos_sdk.resources import ContactDetailsResource, CustomersResource, DebtsResource, PaymentsResource


class TestBaseResource:
    """Test cases for base resource functionality."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def debts_resource(self, mock_http_client):
        """Create debts resource for testing."""
        return DebtsResource(mock_http_client)

    def test_build_expand_params(self, debts_resource):
        """Test building expand parameters."""
        # No expand fields
        params = debts_resource._build_expand_params()
        assert params == {}

        # Single expand field
        params = debts_resource._build_expand_params(["customer"])
        assert params == {"expand[]": ["customer"]}

        # Multiple expand fields
        params = debts_resource._build_expand_params(["customer", "payments"])
        assert params == {"expand[]": ["customer", "payments"]}

    def test_build_list_params(self, debts_resource):
        """Test building list parameters."""
        params = debts_resource._build_list_params(
            limit=10, after="debt_123", before="debt_456", expand=["customer"], extra_param="value"
        )

        expected = {
            "limit": 10,
            "after": "debt_123",
            "before": "debt_456",
            "expand[]": ["customer"],
            "extra_param": "value",
        }
        assert params == expected

    def test_build_search_params(self, debts_resource):
        """Test building search parameters."""
        params = debts_resource._build_search_params(
            query="status:paying", limit=5, expand=["customer"], org_id="org_123"
        )

        expected = {
            "query": "status:paying",
            "limit": 5,
            "expand[]": ["customer"],
            "org_id": "org_123",
        }
        assert params == expected


class TestDebtsResource:
    """Test cases for debts resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def debts_resource(self, mock_http_client):
        """Create debts resource for testing."""
        return DebtsResource(mock_http_client)

    def test_list_debts(self, debts_resource, mock_http_client, sample_debt_data, sample_paginated_response):
        """Test listing debts."""
        # Mock response - keep data as raw dicts, not parsed objects
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_debt_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = debts_resource.list(limit=10, expand=["customer"])

        mock_http_client.get.assert_called_once_with(
            "debts", params={"limit": 10, "expand[]": ["customer"]}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        # First item should be parsed as Debt
        assert isinstance(result.data[0], Debt)

    def test_search_debts(self, debts_resource, mock_http_client, sample_debt_data, sample_paginated_response):
        """Test searching debts."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_debt_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = debts_resource.search("status:paying", limit=5)

        mock_http_client.get.assert_called_once_with(
            "debts/search", params={"query": "status:paying", "limit": 5}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Debt)

    def test_get_debt(self, debts_resource, mock_http_client, sample_debt_data):
        """Test getting a specific debt."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (sample_debt_data, mock_response)

        result = debts_resource.get("debt_123", expand=["customer"])

        mock_http_client.get.assert_called_once_with(
            "debts/debt_123", params={"expand[]": ["customer"]}, return_response=True
        )
        assert isinstance(result, Debt)
        assert result.id == sample_debt_data["id"]

    def test_create_debt(self, debts_resource, mock_http_client, sample_debt_data):
        """Test creating a debt."""
        create_data = {
            "customer_id": "cust_123",
            "organisation_id": "org_123",
            "total_amount": 10000,
        }
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_debt_data, mock_response)

        result = debts_resource.create(create_data)

        mock_http_client.post.assert_called_once_with("debts", data=create_data, return_response=True)
        assert isinstance(result, Debt)

    def test_update_debt(self, debts_resource, mock_http_client, sample_debt_data):
        """Test updating a debt."""
        update_data = {"metadata": {"updated": True}}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_debt_data, mock_response)

        result = debts_resource.update("debt_123", update_data)

        mock_http_client.put.assert_called_once_with("debts/debt_123", data=update_data, return_response=True)
        assert isinstance(result, Debt)

    def test_delete_debt(self, debts_resource, mock_http_client):
        """Test deleting a debt."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.delete.return_value = ({"deleted": True}, mock_response)

        result = debts_resource.delete("debt_123")

        mock_http_client.delete.assert_called_once_with("debts/debt_123", return_response=True)
        assert result == {"deleted": True}

    def test_debt_lifecycle_operations(self, debts_resource, mock_http_client, sample_debt_data):
        """Test debt lifecycle operations."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.post.return_value = (sample_debt_data, mock_response)

        # Test ready operation
        result = debts_resource.ready("debt_123")
        mock_http_client.post.assert_called_with("debts/debt_123/ready", data={}, return_response=True)
        assert isinstance(result, Debt)

        # Test pause operation
        pause_data = {"reason": "customer request"}
        result = debts_resource.pause("debt_123", pause_data)
        mock_http_client.post.assert_called_with("debts/debt_123/pause", data=pause_data, return_response=True)

        # Test resume operation
        result = debts_resource.resume("debt_123")
        mock_http_client.post.assert_called_with("debts/debt_123/resume", data={}, return_response=True)

        # Test withdraw operation
        withdraw_data = {"reason": "fraud"}
        result = debts_resource.withdraw("debt_123", withdraw_data)
        mock_http_client.post.assert_called_with("debts/debt_123/withdraw", data=withdraw_data, return_response=True)

        # Test dispute operation
        dispute_data = {"reason": "amount disputed", "details": "Customer claims incorrect amount"}
        result = debts_resource.dispute("debt_123", dispute_data)
        mock_http_client.post.assert_called_with("debts/debt_123/dispute", data=dispute_data, return_response=True)

    def test_debt_payments_operations(
        self, debts_resource, mock_http_client, sample_payment_data, sample_paginated_response
    ):
        """Test debt payment operations."""
        # Test list payments
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_payment_data]
        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response_obj)

        result = debts_resource.list_payments("debt_123", limit=5)
        mock_http_client.get.assert_called_with("debts/debt_123/payments", params={"limit": 5}, return_response=True)
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Payment)

        # Test create payment
        payment_data = {"amount": 5000, "transaction_at": "2024-01-15T10:00:00Z"}
        mock_http_client.post.return_value = (sample_payment_data, mock_response_obj)

        result = debts_resource.create_payment("debt_123", payment_data)
        mock_http_client.post.assert_called_with("debts/debt_123/payments", data=payment_data, return_response=True)
        assert isinstance(result, Payment)

        # Test get payment
        mock_http_client.get.return_value = (sample_payment_data, mock_response_obj)
        result = debts_resource.get_payment("debt_123", "pay_456")
        mock_http_client.get.assert_called_with("debts/debt_123/payments/pay_456", return_response=True)
        assert isinstance(result, Payment)

    def test_get_debt_summary(self, debts_resource, mock_http_client):
        """Test getting debt summary."""
        summary_data = {"total_amount": 10000, "paid_amount": 3000, "remaining": 7000}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (summary_data, mock_response)

        result = debts_resource.get_summary("debt_123")

        mock_http_client.get.assert_called_once_with("debts/debt_123/summary", return_response=True)
        assert result == summary_data


class TestCustomersResource:
    """Test cases for customers resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def customers_resource(self, mock_http_client):
        """Create customers resource for testing."""
        return CustomersResource(mock_http_client)

    def test_list_customers(
        self, customers_resource, mock_http_client, sample_customer_data, sample_paginated_response
    ):
        """Test listing customers."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_customer_data]
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 200

        # Configure mock to return tuple when return_response=True
        def mock_get_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return mock_response_data, mock_response
            return mock_response_data

        mock_http_client.get.side_effect = mock_get_side_effect

        result = customers_resource.list(limit=10)

        mock_http_client.get.assert_called_once_with("customers", params={"limit": 10}, return_response=True)
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Customer)

    def test_search_customers(
        self, customers_resource, mock_http_client, sample_customer_data, sample_paginated_response
    ):
        """Test searching customers."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_customer_data]
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 200

        # Configure mock to return tuple when return_response=True
        def mock_get_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return mock_response_data, mock_response
            return mock_response_data

        mock_http_client.get.side_effect = mock_get_side_effect

        result = customers_resource.search("email:john@example.com")

        mock_http_client.get.assert_called_once_with(
            "customers/search", params={"query": "email:john@example.com"}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Customer)

    def test_get_customer(self, customers_resource, mock_http_client, sample_customer_data):
        """Test getting a specific customer."""
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 200

        # Configure mock to return tuple when return_response=True
        def mock_get_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return sample_customer_data, mock_response
            return sample_customer_data

        mock_http_client.get.side_effect = mock_get_side_effect

        result = customers_resource.get("cust_123")

        mock_http_client.get.assert_called_once_with("customers/cust_123", params={}, return_response=True)
        assert isinstance(result, Customer)
        assert result.id == sample_customer_data["id"]

    def test_create_customer(self, customers_resource, mock_http_client, sample_customer_data):
        """Test creating a customer."""
        create_data = {"first_name": "John", "last_name": "Doe", "organisation_id": "org_123"}
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 201

        # Configure mock to return tuple when return_response=True
        def mock_post_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return sample_customer_data, mock_response
            return sample_customer_data

        mock_http_client.post.side_effect = mock_post_side_effect

        result = customers_resource.create(create_data)

        mock_http_client.post.assert_called_once_with("customers", data=create_data, return_response=True)
        assert isinstance(result, Customer)

    def test_update_customer(self, customers_resource, mock_http_client, sample_customer_data):
        """Test updating a customer."""
        update_data = {"phone": "+447700900123"}
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 200

        # Configure mock to return tuple when return_response=True
        def mock_put_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return sample_customer_data, mock_response
            return sample_customer_data

        mock_http_client.put.side_effect = mock_put_side_effect

        result = customers_resource.update("cust_123", update_data)

        mock_http_client.put.assert_called_once_with("customers/cust_123", data=update_data, return_response=True)
        assert isinstance(result, Customer)


class TestContactDetailsResource:
    """Test cases for contact details resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def contact_details_resource(self, mock_http_client):
        """Create contact details resource for testing."""
        return ContactDetailsResource(mock_http_client)

    @pytest.fixture
    def sample_contact_detail_data(self):
        """Sample contact detail data for testing."""
        return {
            "id": "cd_123456789",
            "object": "contact_detail",
            "type": "email",
            "value": "test@example.com",
            "primary": True,
            "usage": "permanent",
            "source": "client",
            "status": "active",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
            "metadata": {"verified": True},
        }

    def test_create_contact_detail(self, contact_details_resource, mock_http_client, sample_contact_detail_data):
        """Test creating a contact detail."""
        create_data = {
            "type": "email",
            "value": "test@example.com",
            "primary": True,
            "usage": "permanent",
            "source": "client",
        }
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.create("cust_123", create_data)

        mock_http_client.post.assert_called_once_with(
            "customers/cust_123/contact_details", data=create_data, return_response=True
        )
        assert isinstance(result, ContactDetail)
        assert result.id == sample_contact_detail_data["id"]

    def test_create_contact_detail_with_expand(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test creating a contact detail with expand parameters."""
        create_data = {"type": "phone_number", "value": "+44123456789"}
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.create("cust_123", create_data, expand=["customer"])

        mock_http_client.post.assert_called_once_with(
            "customers/cust_123/contact_details",
            data=create_data,
            params={"expand[]": ["customer"]},
            return_response=True,
        )
        assert isinstance(result, ContactDetail)

    def test_create_contact_detail_with_model(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test creating a contact detail using ContactDetail model instance."""
        contact_detail = ContactDetail(type="email", value="model@example.com", primary=True, usage="permanent")
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.create("cust_123", contact_detail)

        # Should call to_api_body() on the model
        expected_data = contact_detail.to_api_body()
        mock_http_client.post.assert_called_once_with(
            "customers/cust_123/contact_details", data=expected_data, return_response=True
        )
        assert isinstance(result, ContactDetail)

    def test_update_contact_detail(self, contact_details_resource, mock_http_client, sample_contact_detail_data):
        """Test updating a contact detail."""
        update_data = {"status": "verified", "primary": False}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.update("cust_123", "cd_123456789", update_data)

        mock_http_client.put.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", data=update_data, return_response=True
        )
        assert isinstance(result, ContactDetail)
        assert result.id == sample_contact_detail_data["id"]

    def test_update_contact_detail_with_expand(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test updating a contact detail with expand parameters."""
        update_data = {"status": "inactive"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.update("cust_123", "cd_123456789", update_data, expand=["customer"])

        mock_http_client.put.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789",
            data=update_data,
            params={"expand[]": ["customer"]},
            return_response=True,
        )
        assert isinstance(result, ContactDetail)

    def test_update_contact_detail_with_model(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test updating a contact detail using ContactDetail model instance."""
        contact_detail = ContactDetail(type="email", value="updated@example.com", primary=False, status="verified")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.update("cust_123", "cd_123456789", contact_detail)

        # Should call to_api_body() on the model
        expected_data = contact_detail.to_api_body()
        mock_http_client.put.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", data=expected_data, return_response=True
        )
        assert isinstance(result, ContactDetail)

    def test_get_contact_detail(self, contact_details_resource, mock_http_client, sample_contact_detail_data):
        """Test getting a specific contact detail."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.get("cust_123", "cd_123456789")

        mock_http_client.get.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", params={}, return_response=True
        )
        assert isinstance(result, ContactDetail)
        assert result.id == sample_contact_detail_data["id"]

    def test_get_contact_detail_with_expand(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test getting a contact detail with expand parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.get("cust_123", "cd_123456789", expand=["customer"])

        mock_http_client.get.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", params={"expand[]": ["customer"]}, return_response=True
        )
        assert isinstance(result, ContactDetail)

    def test_delete_contact_detail(self, contact_details_resource, mock_http_client, sample_contact_detail_data):
        """Test deleting (soft delete) a contact detail."""
        # Mock response with status "deleted"
        deleted_data = sample_contact_detail_data.copy()
        deleted_data["status"] = "deleted"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.delete.return_value = (deleted_data, mock_response)

        result = contact_details_resource.delete("cust_123", "cd_123456789")

        mock_http_client.delete.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", return_response=True
        )
        assert isinstance(result, ContactDetail)
        assert result.status == "deleted"

    def test_list_contact_details(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data, sample_paginated_response
    ):
        """Test listing contact details for a customer."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_contact_detail_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = contact_details_resource.list("cust_123", limit=20)

        mock_http_client.get.assert_called_once_with(
            "customers/cust_123/contact_details", params={"limit": 20}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], ContactDetail)

    def test_list_contact_details_with_pagination(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data, sample_paginated_response
    ):
        """Test listing contact details with pagination parameters."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_contact_detail_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = contact_details_resource.list("cust_123", limit=10, after="cd_after_123", expand=["customer"])

        mock_http_client.get.assert_called_once_with(
            "customers/cust_123/contact_details",
            params={"limit": 10, "after": "cd_after_123", "expand[]": ["customer"]},
            return_response=True,
        )
        assert isinstance(result, PaginatedResponse)


class TestPaymentsResource:
    """Test cases for payments resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def payments_resource(self, mock_http_client):
        """Create payments resource for testing."""
        return PaymentsResource(mock_http_client)

    def test_list_payments(self, payments_resource, mock_http_client, sample_payment_data, sample_paginated_response):
        """Test listing payments."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_payment_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = payments_resource.list(limit=20)

        mock_http_client.get.assert_called_once_with("payments", params={"limit": 20}, return_response=True)
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Payment)

    def test_search_payments(self, payments_resource, mock_http_client, sample_payment_data, sample_paginated_response):
        """Test searching payments."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_payment_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = payments_resource.search("status:succeeded")

        mock_http_client.get.assert_called_once_with(
            "payments/search", params={"query": "status:succeeded"}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Payment)

    def test_get_payment(self, payments_resource, mock_http_client, sample_payment_data):
        """Test getting a specific payment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (sample_payment_data, mock_response)

        result = payments_resource.get("pay_123")

        mock_http_client.get.assert_called_once_with("payments/pay_123", params={}, return_response=True)
        assert isinstance(result, Payment)
        assert result.id == sample_payment_data["id"]


class TestResourceErrorHandling:
    """Test error handling in resource managers."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def debts_resource(self, mock_http_client):
        """Create debts resource for testing."""
        return DebtsResource(mock_http_client)

    def test_parsing_fallback_on_error(self, debts_resource, mock_http_client):
        """Test that parsing falls back to raw data on error."""
        # Return invalid data that can't be parsed into a Debt model
        invalid_debt_data = {"invalid": "data", "missing_required_fields": True}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (invalid_debt_data, mock_response)

        result = debts_resource.get("debt_123")

        # Should return raw data instead of raising an error
        assert result == invalid_debt_data

    def test_list_parsing_fallback(self, debts_resource, mock_http_client):
        """Test that list parsing falls back to raw data on individual item errors."""
        # Mix of valid and invalid data
        response_data = {
            "object": "list",
            "data": [
                {  # Valid debt data
                    "id": "debt_123",
                    "object": "debt",
                    "status": {
                        "value": "prepared",
                        "whodunnit": "system",
                        "context": None,
                        "reason": None,
                        "updated_at": "2024-01-15T10:00:00Z",
                    },
                    "customer": "cust_123",
                    "organisation": "org_123",
                    "customer_id": "cust_123",
                    "organisation_id": "org_123",
                    "summary": {"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
                    "created_at": "2024-01-15T10:00:00Z",
                    "updated_at": "2024-01-15T10:00:00Z",
                },
                {"invalid": "data"},  # Invalid debt data
            ],
            "has_more": False,
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (response_data, mock_response)

        result = debts_resource.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        # First item should be parsed as Debt
        assert isinstance(result.data[0], Debt)
        # Second item should remain as raw dict
        assert isinstance(result.data[1], dict)
        assert result.data[1] == {"invalid": "data"}

    def test_parse_error_debugging_interface(self, debts_resource):
        """Test that ParseError provides request/response debugging information."""
        from unittest.mock import Mock

        import requests

        from ophelos_sdk.exceptions import ParseError

        # Create a mock response object
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.url = "https://api.test.com/debts"
        mock_response.reason = "OK"
        mock_response.encoding = "utf-8"

        # Mock the elapsed attribute
        mock_elapsed = Mock()
        mock_elapsed.total_seconds.return_value = 0.123
        mock_response.elapsed = mock_elapsed

        # Create a mock request
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = "https://api.test.com/debts"
        mock_request.headers = {"Authorization": "Bearer token"}
        mock_request.body = None
        mock_response.request = mock_request

        # Test ParseError with response object
        try:
            raise ParseError("Test parse error", response=mock_response)
        except ParseError as e:
            # Should have debugging interface
            assert e.request_info is not None
            assert e.request_info["method"] == "GET"
            assert e.request_info["url"] == "https://api.test.com/debts"
            assert e.request_info["headers"]["Authorization"] == "Bearer token"
            assert e.request_info["body"] is None

            assert e.response_info is not None
            assert e.response_info["status_code"] == 200
            assert e.response_info["headers"]["content-type"] == "application/json"
            assert e.response_info["url"] == "https://api.test.com/debts"
            assert e.response_info["reason"] == "OK"
            assert e.response_info["encoding"] == "utf-8"
            assert e.response_info["elapsed_ms"] == 123.0

            assert e.response_raw is mock_response

        # Test ParseError without response object (should be None)
        try:
            raise ParseError("Test parse error without response")
        except ParseError as e:
            assert e.request_info is None
            assert e.response_info is None
            assert e.response_raw is None

    def test_general_exception_handling_gap(self, debts_resource, mock_http_client):
        """Test what happens with general code processing errors (currently not handled)."""
        from unittest.mock import Mock

        import requests

        # Create a mock response object for context
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.url = "https://api.test.com/debts"
        mock_response.reason = "OK"
        mock_response.encoding = "utf-8"

        mock_elapsed = Mock()
        mock_elapsed.total_seconds.return_value = 0.123
        mock_response.elapsed = mock_elapsed

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = "https://api.test.com/debts"
        mock_request.headers = {"Authorization": "Bearer token"}
        mock_request.body = None
        mock_response.request = mock_request

        # Simulate a general code error that occurs during request processing
        # This could be a programming error, unexpected network issue, etc.
        mock_http_client.get.side_effect = ValueError("Some unexpected error")

        # Currently, this will bubble up as a regular ValueError without debugging info
        try:
            debts_resource.get("debt_123")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            # This is the current behavior - no debugging interface
            assert str(e) == "Some unexpected error"
            # These would fail because ValueError doesn't have debugging interface
            assert not hasattr(e, "request_info")
            assert not hasattr(e, "response_info")
            assert not hasattr(e, "response_raw")

            # This shows the gap - we have no access to request/response context
            # that could help debug what went wrong

    def test_unexpected_error_debugging_interface(self):
        """Test that UnexpectedError provides request/response debugging information."""
        from unittest.mock import Mock, patch

        from ophelos_sdk.auth import StaticTokenAuthenticator
        from ophelos_sdk.exceptions import UnexpectedError
        from ophelos_sdk.http_client import HTTPClient

        # Create real HTTP client with mock authenticator
        auth = Mock(spec=StaticTokenAuthenticator)
        auth.get_auth_headers.return_value = {"Authorization": "Bearer test_token"}

        http_client = HTTPClient(
            authenticator=auth,
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3,
        )

        # Mock the session.request method to raise an unexpected error
        with patch("ophelos_sdk.http_client.HTTPClient._get_session") as mock_get_session:
            mock_session = Mock()
            mock_session.request.side_effect = ValueError("Some unexpected error")
            mock_get_session.return_value = mock_session

            # Now this should be wrapped in UnexpectedError with debugging info
            try:
                http_client.get("/debts/debt_123")
                assert False, "Expected UnexpectedError to be raised"
            except UnexpectedError as e:
                # Should have debugging interface
                assert e.request_info is not None
                assert e.request_info["method"] == "GET"
                assert e.request_info["url"] == "https://api.test.com/debts/debt_123"
                assert "Authorization" in e.request_info["headers"]
                assert e.request_info["body"] is None

                # Should have original error
                assert e.original_error is not None
                assert isinstance(e.original_error, ValueError)
                assert str(e.original_error) == "Some unexpected error"

                # Response info should be None for pre-request errors
                assert e.response_info is None
                assert e.response_raw is None

    def test_unexpected_error_response_processing(self):
        """Test that UnexpectedError handles response processing errors."""
        from unittest.mock import Mock, patch

        import requests

        from ophelos_sdk.auth import StaticTokenAuthenticator
        from ophelos_sdk.exceptions import UnexpectedError
        from ophelos_sdk.http_client import HTTPClient

        # Create real HTTP client with mock authenticator
        auth = Mock(spec=StaticTokenAuthenticator)
        auth.get_auth_headers.return_value = {"Authorization": "Bearer test_token"}

        http_client = HTTPClient(
            authenticator=auth,
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3,
        )

        # Mock successful request but error in response processing
        with patch("ophelos_sdk.http_client.HTTPClient._get_session") as mock_get_session:
            mock_session = Mock()
            mock_response = Mock(spec=requests.Response)
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.url = "https://api.test.com/debts/debt_123"
            mock_response.reason = "OK"
            mock_response.encoding = "utf-8"

            mock_elapsed = Mock()
            mock_elapsed.total_seconds.return_value = 0.123
            mock_response.elapsed = mock_elapsed

            mock_request = Mock()
            mock_request.method = "GET"
            mock_request.url = "https://api.test.com/debts/debt_123"
            mock_request.headers = {"Authorization": "Bearer test_token"}
            mock_request.body = None
            mock_response.request = mock_request

            # Simulate successful request
            mock_session.request.return_value = mock_response
            mock_get_session.return_value = mock_session

            # Mock response processing to raise an error
            with patch.object(http_client, "_handle_response") as mock_handle_response:
                mock_handle_response.side_effect = ValueError("Response processing error")

                try:
                    http_client.get("/debts/debt_123")
                    assert False, "Expected UnexpectedError to be raised"
                except UnexpectedError as e:
                    # Should have debugging interface with response info
                    assert e.request_info is not None
                    assert e.request_info["method"] == "GET"
                    assert e.request_info["url"] == "https://api.test.com/debts/debt_123"

                    # Should have response info since request succeeded
                    assert e.response_info is not None
                    assert e.response_info["status_code"] == 200
                    assert e.response_info["url"] == "https://api.test.com/debts/debt_123"
                    assert e.response_raw is mock_response

                    # Should have original error
                    assert e.original_error is not None
                    assert isinstance(e.original_error, ValueError)
                    assert str(e.original_error) == "Response processing error"
