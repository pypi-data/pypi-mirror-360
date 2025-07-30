#!/usr/bin/env python3
"""
Example: Concurrent API calls using OphelosClient with ThreadPoolExecutor

This example demonstrates:
1. Single OphelosClient instance shared across threads
2. Token fetched once and reused automatically
3. Concurrent API calls using ThreadPoolExecutor
4. Error handling and thread safety
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Tuple

from ophelos_sdk import OphelosClient
from ophelos_sdk.exceptions import OphelosAPIError


def setup_client() -> OphelosClient:
    """Initialize the OphelosClient - this will be shared across all threads."""
    return OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID", "your_client_id"),
        client_secret=os.getenv(
            "OPHELOS_CLIENT_SECRET",
            "your_client_secret",
        ),
        audience=os.getenv("OPHELOS_AUDIENCE", "your_audience"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "development"),  # staging, development, production
        tenant_id=os.getenv("OPHELOS_TENANT_ID"),  # Optional
    )


def fetch_debt_data(client: OphelosClient, debt_id: str) -> Tuple[str, Optional[dict], Optional[str]]:
    """
    Fetch debt data - this function will be called concurrently.

    Returns:
        Tuple of (debt_id, debt_data, error_message)
    """
    try:
        print(f"🔍 Thread {debt_id}: Fetching debt data...")
        debt = client.debts.get(debt_id)
        print(f"✅ Thread {debt_id}: Successfully fetched debt data")
        return debt_id, debt, None
    except OphelosAPIError as e:
        error_msg = f"API Error: {e}"
        print(f"❌ Thread {debt_id}: {error_msg}")
        return debt_id, None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"💥 Thread {debt_id}: {error_msg}")
        return debt_id, None, error_msg


def fetch_customer_data(client: OphelosClient, customer_id: str) -> Tuple[str, Optional[dict], Optional[str]]:
    """
    Fetch customer data - this function will be called concurrently.

    Returns:
        Tuple of (customer_id, customer_data, error_message)
    """
    try:
        print(f"🔍 Thread {customer_id}: Fetching customer data...")
        customer = client.customers.get(customer_id)
        print(f"✅ Thread {customer_id}: Successfully fetched customer data")
        return customer_id, customer, None
    except OphelosAPIError as e:
        error_msg = f"API Error: {e}"
        print(f"❌ Thread {customer_id}: {error_msg}")
        return customer_id, None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"💥 Thread {customer_id}: {error_msg}")
        return customer_id, None, error_msg


def list_resources_concurrently(client: OphelosClient) -> dict:
    """
    Fetch multiple resource lists concurrently.

    Returns:
        Dictionary with results from each resource type
    """

    def fetch_debts():
        print("🔍 Fetching debts list...")
        return "debts", client.debts.list(limit=10)

    def fetch_customers():
        print("🔍 Fetching customers list...")
        return "customers", client.customers.list(limit=10)

    def fetch_payments():
        print("🔍 Fetching payments list...")
        return "payments", client.payments.list(limit=10)

    def fetch_organisations():
        print("🔍 Fetching organisations list...")
        return "organisations", client.organisations.list(limit=10)

    results = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        futures = [
            executor.submit(fetch_debts),
            executor.submit(fetch_customers),
            executor.submit(fetch_payments),
            executor.submit(fetch_organisations),
        ]

        # Collect results
        for future in as_completed(futures):
            try:
                resource_name, data = future.result()
                results[resource_name] = data
                print(f"✅ Successfully fetched {resource_name}")
            except Exception as e:
                print(f"❌ Error fetching resource: {e}")

    return results


def example_concurrent_specific_resources():
    """Example: Fetch specific debts/customers concurrently."""
    print("🚀 Example 1: Concurrent API calls for specific resources")
    print("=" * 60)

    client = setup_client()

    # Force token fetch with first call (optional - will happen automatically anyway)
    print("🔐 Pre-fetching authentication token...")
    try:
        client.test_connection()
        print("✅ Authentication successful - token cached for reuse")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    # Example debt and customer IDs (replace with real ones)
    debt_ids = [
        "deb_6XZpg4wz7D59CD3geK19Ak50",
        "deb_1r9M3yxR7Yw6SKWxaWNXYo6m",
        "deb_v9zy58BlE1WzhrdoeMRdX0jA",
        "deb_6m8kAKdMay0wtWG6e0OJQv4r",
        "deb_1Ly9K5dnemWPh9MlEA0rNQBl",
    ]
    customer_ids = [
        "cus_4kbKdO3WzjoPI7RnB2yAYlvj",
        "cus_VArpk9xPzGnPi8r0QgZyMjGO",
        "cus_K6597AJEQR4rHVRYBOW2v4oj",
    ]

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit debt fetching tasks
        debt_futures = [executor.submit(fetch_debt_data, client, debt_id) for debt_id in debt_ids]

        # Submit customer fetching tasks
        customer_futures = [executor.submit(fetch_customer_data, client, customer_id) for customer_id in customer_ids]

        all_futures = debt_futures + customer_futures

        # Process results as they complete
        results = {"debts": {}, "customers": {}, "errors": []}

        for future in as_completed(all_futures):
            resource_id, data, error = future.result()

            if error:
                results["errors"].append(f"{resource_id}: {error}")
            elif resource_id.startswith("debt_"):
                results["debts"][resource_id] = data
            elif resource_id.startswith("customer_"):
                results["customers"][resource_id] = data

    end_time = time.time()

    print("\n📊 Results Summary:")
    print(f"   ✅ Debts fetched: {len(results['debts'])}")
    print(f"   ✅ Customers fetched: {len(results['customers'])}")
    print(f"   ❌ Errors: {len(results['errors'])}")
    print(f"   ⏱️  Total time: {end_time - start_time:.2f} seconds")

    if results["errors"]:
        print("\n🚨 Errors encountered:")
        for error in results["errors"]:
            print(f"   • {error}")


def example_concurrent_list_operations():
    """Example: Fetch different resource lists concurrently."""
    print("\n🚀 Example 2: Concurrent list operations")
    print("=" * 60)

    client = setup_client()

    start_time = time.time()
    results = list_resources_concurrently(client)
    end_time = time.time()

    print("\n📊 List Results Summary:")
    for resource_name, data in results.items():
        if hasattr(data, "data") and hasattr(data.data, "__len__"):
            print(f"   ✅ {resource_name}: {len(data.data)} items")
        else:
            print(f"   ✅ {resource_name}: Retrieved")

    print(f"   ⏱️  Total time: {end_time - start_time:.2f} seconds")


def example_with_search_operations():
    """Example: Concurrent search operations."""
    print("\n🚀 Example 3: Concurrent search operations")
    print("=" * 60)

    client = setup_client()

    def search_debts_by_status(status: str):
        print(f"🔍 Searching debts with status: {status}")
        return f"debts_{status}", client.debts.search(f"status:{status}")

    def search_customers_by_email(email: str):
        print(f"🔍 Searching customers with email: {email}")
        return f"customers_{email}", client.customers.search(f"email={email}")

    search_tasks = [
        ("debt_status", "initializing"),
        ("debt_status", "paid"),
        ("debt_status", "withdrawn"),
        ("email", "user1@example.com"),
        ("email", "user2@example.com"),
    ]

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []

        for task_type, param in search_tasks:
            if task_type == "debt_status":
                future = executor.submit(search_debts_by_status, param)
            elif task_type == "email":
                future = executor.submit(search_customers_by_email, param)
            futures.append(future)

        # Collect results
        search_results = {}
        for future in as_completed(futures):
            try:
                search_key, data = future.result()
                search_results[search_key] = data
                if hasattr(data, "data"):
                    print(f"✅ {search_key}: {len(data.data)} results")
            except Exception as e:
                print(f"❌ Search error: {e}")

    end_time = time.time()
    print(f"   ⏱️  Search time: {end_time - start_time:.2f} seconds")


def main():
    """Run all concurrent examples."""
    print("🎯 Ophelos SDK - Concurrent Usage Examples")
    print("=" * 60)
    print("This demonstrates sharing a single OphelosClient instance")
    print("across multiple threads with automatic token management.")
    print()

    try:
        # Run examples
        # example_concurrent_specific_resources()
        # example_concurrent_list_operations()
        example_with_search_operations()

        print("\n🎉 All examples completed successfully!")
        print("\n💡 Key Points:")
        print("   • Single OphelosClient instance shared across threads")
        print("   • Authentication token fetched once and reused automatically")
        print("   • Concurrent API calls significantly reduce total time")
        print("   • Thread-safe error handling")
        print("   • Automatic token refresh when needed")

    except KeyboardInterrupt:
        print("\n🛑 Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    main()
