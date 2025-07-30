#!/usr/bin/env python3
"""
Asyncio Usage Example with Ophelos SDK

This example demonstrates how to use the synchronous Ophelos SDK
in asynchronous applications using asyncio patterns.

Since the SDK uses the synchronous requests library, we use
asyncio.to_thread() and other async patterns to integrate it
into async applications without blocking the event loop.
"""

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any, Optional

from ophelos_sdk import OphelosClient


@dataclass
class AsyncResult:
    """Result wrapper for async operations."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration: float = 0.0


def setup_client() -> OphelosClient:
    """Initialize the Ophelos client with environment variables."""
    return OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID", "your_client_id"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET", "your_client_secret"),
        audience=os.getenv("OPHELOS_AUDIENCE", "your_audience"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "development"),
    )


async def async_fetch_debts(client: OphelosClient, limit: int = 10) -> AsyncResult:
    """Fetch debts asynchronously using asyncio.to_thread()."""
    start_time = time.time()

    try:
        # Run the synchronous operation in a thread pool
        debts = await asyncio.to_thread(client.debts.list, limit=limit, expand=["customer", "organisation"])

        duration = time.time() - start_time
        return AsyncResult(success=True, data=debts, duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        return AsyncResult(success=False, error=str(e), duration=duration)


async def async_fetch_customers(client: OphelosClient, limit: int = 10) -> AsyncResult:
    """Fetch customers asynchronously."""
    start_time = time.time()

    try:
        customers = await asyncio.to_thread(client.customers.list, limit=limit, expand=["contact_details"])

        duration = time.time() - start_time
        return AsyncResult(success=True, data=customers, duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        return AsyncResult(success=False, error=str(e), duration=duration)


async def async_fetch_payments(client: OphelosClient, limit: int = 10) -> AsyncResult:
    """Fetch payments asynchronously."""
    start_time = time.time()

    try:
        payments = await asyncio.to_thread(client.payments.list, limit=limit)

        duration = time.time() - start_time
        return AsyncResult(success=True, data=payments, duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        return AsyncResult(success=False, error=str(e), duration=duration)


async def async_fetch_organisations(client: OphelosClient, limit: int = 10) -> AsyncResult:
    """Fetch organisations asynchronously."""
    start_time = time.time()

    try:
        organisations = await asyncio.to_thread(client.organisations.list, limit=limit)

        duration = time.time() - start_time
        return AsyncResult(success=True, data=organisations, duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        return AsyncResult(success=False, error=str(e), duration=duration)


async def example_concurrent_fetch():
    """Example: Fetch multiple resources concurrently with asyncio.gather()."""
    print("🚀 Asyncio Example 1: Concurrent Resource Fetching")
    print("=" * 60)

    client = setup_client()

    # Pre-authenticate to avoid race conditions
    print("🔐 Pre-authenticating...")
    try:
        await asyncio.to_thread(client.test_connection)
        print("✅ Authentication successful - token cached")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    print("\n🔄 Fetching multiple resources concurrently...")
    start_time = time.time()

    # Run all async operations concurrently
    results = await asyncio.gather(
        async_fetch_debts(client, limit=5),
        async_fetch_customers(client, limit=5),
        async_fetch_payments(client, limit=5),
        async_fetch_organisations(client, limit=5),
        return_exceptions=True,
    )

    total_time = time.time() - start_time

    # Process results
    resource_names = ["Debts", "Customers", "Payments", "Organisations"]

    print("\n📊 Results Summary:")
    for i, (name, result) in enumerate(zip(resource_names, results)):
        if isinstance(result, Exception):
            print(f"   ❌ {name}: Error - {result}")
        elif result.success:
            data_count = len(result.data.data) if hasattr(result.data, "data") else 0
            print(f"   ✅ {name}: {data_count} items ({result.duration:.2f}s)")
        else:
            print(f"   ❌ {name}: {result.error} ({result.duration:.2f}s)")

    print(f"   ⏱️  Total concurrent time: {total_time:.2f}s")


async def example_async_iteration():
    """Example: Async iteration over paginated results."""
    print("\n🚀 Asyncio Example 2: Async Pagination")
    print("=" * 60)

    client = setup_client()

    async def async_iterate_debts(max_items: int = 20):
        """Async generator-like iteration over debts."""
        items_processed = 0
        offset = 0
        limit = 5

        while items_processed < max_items:
            try:
                # Fetch next page asynchronously
                page = await asyncio.to_thread(client.debts.list, limit=limit, offset=offset, expand=["customer"])

                if not page.data:
                    break

                for debt in page.data:
                    if items_processed >= max_items:
                        break

                    yield debt
                    items_processed += 1

                offset += limit

                # Don't hammer the API - small delay between pages
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"Error fetching page: {e}")
                break

    print("📄 Async iteration over debts...")
    count = 0

    async for debt in async_iterate_debts(max_items=10):
        count += 1
        amount = debt.summary.amount_total / 100 if hasattr(debt, "summary") else 0
        print(f"  {count}. Debt {debt.id}: ${amount:.2f} ({debt.status.value})")

        # Simulate some async processing
        await asyncio.sleep(0.05)

    print(f"✅ Processed {count} debts asynchronously")


async def example_async_batch_processing():
    """Example: Batch processing with async semaphore for rate limiting."""
    print("\n🚀 Asyncio Example 3: Rate-Limited Batch Processing")
    print("=" * 60)

    client = setup_client()

    # Semaphore to limit concurrent operations
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent operations

    async def process_debt_with_limit(debt_id: str) -> AsyncResult:
        """Process a single debt with rate limiting."""
        async with semaphore:
            start_time = time.time()
            try:
                debt = await asyncio.to_thread(client.debts.get, debt_id, expand=["customer", "payments"])

                # Simulate processing time
                await asyncio.sleep(0.1)

                duration = time.time() - start_time
                return AsyncResult(success=True, data=debt, duration=duration)
            except Exception as e:
                duration = time.time() - start_time
                return AsyncResult(success=False, error=str(e), duration=duration)

    # Get some debt IDs first
    try:
        debts_list = await asyncio.to_thread(client.debts.list, limit=5)
        debt_ids = [debt.id for debt in debts_list.data]
    except Exception as e:
        print(f"❌ Failed to get debt IDs: {e}")
        return

    if not debt_ids:
        print("No debts found for batch processing")
        return

    print(f"🔄 Processing {len(debt_ids)} debts with rate limiting...")
    start_time = time.time()

    # Process all debts concurrently but rate-limited
    tasks = [process_debt_with_limit(debt_id) for debt_id in debt_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time

    # Analyze results
    successful = sum(1 for r in results if isinstance(r, AsyncResult) and r.success)
    failed = len(results) - successful

    print("\n📊 Batch Processing Results:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏱️  Total time: {total_time:.2f}s")
    print(f"   📈 Average time per item: {total_time / len(results):.2f}s")


async def example_async_search_operations():
    """Example: Async search operations with timeout handling."""
    print("\n🚀 Asyncio Example 4: Async Search with Timeouts")
    print("=" * 60)

    client = setup_client()

    async def search_with_timeout(query: str, timeout: float = 5.0) -> AsyncResult:
        """Search with timeout protection."""
        try:
            result = await asyncio.wait_for(asyncio.to_thread(client.debts.search, query, limit=10), timeout=timeout)
            return AsyncResult(success=True, data=result)
        except asyncio.TimeoutError:
            return AsyncResult(success=False, error=f"Search timed out after {timeout}s")
        except Exception as e:
            return AsyncResult(success=False, error=str(e))

    # Multiple search queries
    search_queries = [
        "status:paid",
        "status:paying",
        "status:withdrawn",
        "amount_total>10000",
    ]

    print("🔍 Running multiple searches concurrently...")

    search_tasks = [search_with_timeout(query, timeout=10.0) for query in search_queries]

    results = await asyncio.gather(*search_tasks)

    print("\n📊 Search Results:")
    for query, result in zip(search_queries, results):
        if result.success:
            count = len(result.data.data) if hasattr(result.data, "data") else 0
            print(f"   ✅ '{query}': {count} results")
        else:
            print(f"   ❌ '{query}': {result.error}")


async def example_async_with_progress():
    """Example: Async operations with progress tracking."""
    print("\n🚀 Asyncio Example 5: Progress Tracking")
    print("=" * 60)

    client = setup_client()

    async def fetch_with_progress(resource_name: str, fetch_func) -> AsyncResult:
        """Fetch data with progress updates."""
        print(f"   🔄 Starting {resource_name}...")

        result = await fetch_func()

        if result.success:
            count = len(result.data.data) if hasattr(result.data, "data") else 0
            print(f"   ✅ {resource_name} completed: {count} items ({result.duration:.2f}s)")
        else:
            print(f"   ❌ {resource_name} failed: {result.error}")

        return result

    # Create tasks with progress tracking
    tasks = [
        fetch_with_progress("Debts", lambda: async_fetch_debts(client, 8)),
        fetch_with_progress("Customers", lambda: async_fetch_customers(client, 6)),
        fetch_with_progress("Payments", lambda: async_fetch_payments(client, 4)),
    ]

    print("🚀 Starting async operations with progress tracking...")

    # Use asyncio.as_completed to show progress as tasks complete
    for completed_task in asyncio.as_completed(tasks):
        await completed_task

    print("✅ All operations completed!")


async def main():
    """Run all asyncio examples."""
    print("⚡ Ophelos SDK - Asyncio Usage Examples")
    print("=" * 60)
    print("This demonstrates using the synchronous SDK in async applications")
    print("using asyncio.to_thread() and other async patterns.")
    print()

    try:
        await example_concurrent_fetch()
        await example_async_iteration()
        await example_async_batch_processing()
        await example_async_search_operations()
        await example_async_with_progress()

        print("\n" + "=" * 60)
        print("🎉 All asyncio examples completed successfully!")
        print("\n💡 Key Techniques Demonstrated:")
        print("   • asyncio.to_thread() for sync-to-async conversion")
        print("   • asyncio.gather() for concurrent operations")
        print("   • Async generators for pagination")
        print("   • Semaphores for rate limiting")
        print("   • Timeout handling with asyncio.wait_for()")
        print("   • Progress tracking with asyncio.as_completed()")
        print("   • Proper error handling in async context")

    except KeyboardInterrupt:
        print("\n🛑 Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
