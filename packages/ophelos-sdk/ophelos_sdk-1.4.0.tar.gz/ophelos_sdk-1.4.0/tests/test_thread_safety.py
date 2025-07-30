"""
Thread safety tests for OphelosClient authentication.

Tests verify that the OAuth2Authenticator is thread-safe when used
with ThreadPoolExecutor and multiple concurrent requests.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

from ophelos_sdk import OphelosClient


class TestThreadSafety:
    """Test thread safety of OphelosClient authentication."""

    def test_concurrent_token_access(self):
        """Test that multiple threads can access tokens safely."""

        client = OphelosClient(
            client_id="test_client",
            client_secret="test_secret",
            audience="test_audience",
            environment="development",
        )

        # Mock the token fetching to simulate real behavior
        fetch_count = {"count": 0}
        fetch_lock = threading.Lock()

        def mock_fetch_new_token():
            with fetch_lock:
                fetch_count["count"] += 1
                time.sleep(0.1)  # Simulate network delay

                client.authenticator._access_token = f"mock_token_{fetch_count['count']}"
                client.authenticator._token_expires_at = time.time() + 3600
                return client.authenticator._access_token

        client.authenticator._fetch_new_token = mock_fetch_new_token

        # Function to get auth headers from different threads
        def get_auth_headers(thread_id: int):
            headers = client.authenticator.get_auth_headers()
            return headers

        # Run concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_auth_headers, i) for i in range(10)]
            results = [future.result() for future in futures]

        # Verify results
        assert len(results) == 10, "All threads should complete successfully"

        # All results should have the same token (from first fetch)
        tokens = [result["Authorization"] for result in results]
        unique_tokens = set(tokens)

        # Thread safety assertions
        assert fetch_count["count"] == 1, f"Expected 1 token fetch, got {fetch_count['count']}"
        assert len(unique_tokens) == 1, f"Expected 1 unique token, got {len(unique_tokens)}"

    def test_simple_concurrent_access(self):
        """Test simple concurrent access to verify thread safety works in practice."""
        client = OphelosClient(
            client_id="test_client",
            client_secret="test_secret",
            audience="test_audience",
            environment="development",
        )

        # Override with a simple mock that works with our thread safety
        fetch_count = {"count": 0}

        def simple_mock_fetch():
            # This will be called within the RLock context from get_access_token()
            fetch_count["count"] += 1
            client.authenticator._access_token = f"thread_safe_token_{fetch_count['count']}"
            client.authenticator._token_expires_at = time.time() + 3600  # 1 hour
            return client.authenticator._access_token

        client.authenticator._fetch_new_token = simple_mock_fetch

        def get_token(thread_id: int):
            token = client.authenticator.get_access_token()
            return token

        # Test concurrent access
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(get_token, i) for i in range(8)]
            tokens = [future.result() for future in futures]

        # Thread safety assertions
        assert fetch_count["count"] == 1, f"Expected 1 token fetch, got {fetch_count['count']}"
        assert len(set(tokens)) == 1, f"Expected 1 unique token, got {len(set(tokens))}"
        assert all(tokens), "All threads should receive valid tokens"

    def test_token_expiry_concurrent_refresh(self):
        """Test that token refresh works correctly under concurrent access."""
        client = OphelosClient(
            client_id="test_client",
            client_secret="test_secret",
            audience="test_audience",
            environment="development",
        )

        fetch_count = {"count": 0}

        def mock_fetch_with_expiry():
            fetch_count["count"] += 1
            # First token expires quickly, second token lasts longer
            if fetch_count["count"] == 1:
                client.authenticator._access_token = "short_lived_token"
                client.authenticator._token_expires_at = time.time() + 0.2  # 200ms
            else:
                client.authenticator._access_token = "long_lived_token"
                client.authenticator._token_expires_at = time.time() + 3600  # 1 hour
            return client.authenticator._access_token

        client.authenticator._fetch_new_token = mock_fetch_with_expiry

        # Get initial token
        first_token = client.authenticator.get_access_token()
        assert first_token == "short_lived_token"

        # Wait for token to expire
        time.sleep(0.3)

        def get_token_after_expiry(thread_id: int):
            return client.authenticator.get_access_token()

        # Test concurrent access after expiry
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_token_after_expiry, i) for i in range(5)]
            tokens = [future.result() for future in futures]

        # Should have refreshed exactly once more (total 2 fetches)
        assert fetch_count["count"] == 2, f"Expected 2 token fetches, got {fetch_count['count']}"
        assert all(token == "long_lived_token" for token in tokens), "All threads should get the new token"
        assert len(set(tokens)) == 1, "All threads should get the same refreshed token"

    def test_auth_headers_thread_safety(self):
        """Test that get_auth_headers is thread-safe."""
        client = OphelosClient(
            client_id="test_client",
            client_secret="test_secret",
            audience="test_audience",
            environment="development",
        )

        fetch_count = {"count": 0}

        def mock_fetch():
            fetch_count["count"] += 1
            client.authenticator._access_token = f"bearer_token_{fetch_count['count']}"
            client.authenticator._token_expires_at = time.time() + 3600
            return client.authenticator._access_token

        client.authenticator._fetch_new_token = mock_fetch

        def get_headers(thread_id: int):
            return client.authenticator.get_auth_headers()

        # Test concurrent auth header requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_headers, i) for i in range(20)]
            results = [future.result() for future in futures]

        # Verify all threads got valid headers
        assert len(results) == 20, "All threads should complete"
        assert all("Authorization" in headers for headers in results), "All headers should have Authorization"

        # All should have the same token
        auth_values = [headers["Authorization"] for headers in results]
        unique_auth_values = set(auth_values)

        assert fetch_count["count"] == 1, f"Expected 1 token fetch, got {fetch_count['count']}"
        assert len(unique_auth_values) == 1, f"Expected 1 unique auth header, got {len(unique_auth_values)}"
        assert all(auth.startswith("Bearer ") for auth in auth_values), "All should be Bearer tokens"

    def test_invalidate_token_thread_safety(self):
        """Test that token invalidation works correctly with concurrent access."""
        client = OphelosClient(
            client_id="test_client",
            client_secret="test_secret",
            audience="test_audience",
            environment="development",
        )

        fetch_count = {"count": 0}

        def mock_fetch():
            fetch_count["count"] += 1
            client.authenticator._access_token = f"invalidation_token_{fetch_count['count']}"
            client.authenticator._token_expires_at = time.time() + 3600
            return client.authenticator._access_token

        client.authenticator._fetch_new_token = mock_fetch

        # Get initial token
        first_token = client.authenticator.get_access_token()
        assert first_token == "invalidation_token_1"
        assert fetch_count["count"] == 1

        # Invalidate token
        client.authenticator.invalidate_token()

        def get_token_after_invalidation(thread_id: int):
            return client.authenticator.get_access_token()

        # Test concurrent access after invalidation
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_token_after_invalidation, i) for i in range(5)]
            tokens = [future.result() for future in futures]

        # Should have fetched a new token exactly once
        assert fetch_count["count"] == 2, f"Expected 2 total fetches, got {fetch_count['count']}"
        assert all(token == "invalidation_token_2" for token in tokens), "All threads should get the new token"
        assert len(set(tokens)) == 1, "All threads should get the same new token"
