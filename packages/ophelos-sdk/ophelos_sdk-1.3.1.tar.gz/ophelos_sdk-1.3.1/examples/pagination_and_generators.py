#!/usr/bin/env python3
"""
Ophelos SDK - Comprehensive Pagination & Generators Guide

This example demonstrates all pagination approaches available in the SDK:
- Basic cursor-based pagination
- Generator-based iteration (memory efficient)
- Search with pagination
- Page limits and filtering
- Cross-resource consistency
"""

import os

from ophelos_sdk import OphelosClient


def setup_client():
    """Setup the Ophelos client."""
    return OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID", "your_client_id"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET", "your_client_secret"),
        audience=os.getenv("OPHELOS_AUDIENCE", "your_audience"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "development"),
    )


def basic_pagination_examples():
    """Basic pagination patterns."""
    client = setup_client()

    print("=" * 60)
    print("1. BASIC PAGINATION")
    print("=" * 60)

    # Simple pagination
    print("\n--- Simple List with Pagination ---")
    page1 = client.debts.list(limit=5)
    print(f"First page: {len(page1.data)} debts, has_more: {page1.has_more}")
    if page1.total_count:
        print(f"Total count: {page1.total_count}")

    for debt in page1.data[:3]:  # Show first 3
        print(f"  Debt {debt.id}: {debt.status.value} - ${debt.summary.amount_total / 100:.2f}")

    # Next page using cursors from pagination info
    if page1.has_more and page1.pagination and "next" in page1.pagination:
        print("\n--- Next Page ---")
        next_cursor = page1.pagination["next"]["after"]
        page2 = client.debts.list(limit=5, after=next_cursor)
        print(f"Second page: {len(page2.data)} debts, has_more: {page2.has_more}")
        if page2.total_count:
            print(f"Total count: {page2.total_count}")
        print(f"Used cursor: {next_cursor}")

        # Show pagination info
        if page2.pagination:
            print("Available pagination options:")
            for rel, info in page2.pagination.items():
                cursor_type = "after" if "after" in info else "before" if "before" in info else "none"
                cursor_value = info.get("after") or info.get("before", "N/A")
                print(f"  {rel}: {cursor_type}={cursor_value}")
    else:
        print("\n--- No more pages available ---")
        print("✅ Pagination is working correctly!")

    # With expanded data
    print("\n--- With Expanded Data ---")
    expanded_page = client.debts.list(limit=3, expand=["customer", "organisation"])

    for debt in expanded_page.data:
        customer_name = "Unknown"
        if hasattr(debt, "customer") and debt.customer:
            if isinstance(debt.customer, str):
                customer_name = f"Customer ID: {debt.customer}"
            else:
                customer_name = debt.customer.full_name or "N/A"
        print(f"  Debt {debt.id}: Customer {customer_name}")


def generator_iteration_examples():
    """Generator-based iteration for memory efficiency."""
    client = setup_client()

    print("\n" + "=" * 60)
    print("2. GENERATOR-BASED ITERATION")
    print("=" * 60)

    # Basic generator usage
    print("\n--- Basic Generator (Limited Pages) ---")
    count = 0
    for debt in client.debts.iterate(limit_per_page=10, max_pages=2):
        count += 1
        print(f"  {count:2d}. Debt {debt.id}: {debt.status.value}")
        if count >= 5:  # Limit output for demo
            print(f"     ... (showing 5 of {count}+ total)")
            break

    # Generator with filters
    print("\n--- Generator with Filters ---")
    for debt in client.debts.iterate(
        limit_per_page=5, max_pages=1, expand=["customer"], status="paying"  # Custom filter
    ):
        customer_name = "Unknown"
        if hasattr(debt, "customer") and debt.customer:
            if isinstance(debt.customer, str):
                customer_name = f"Customer ID: {debt.customer}"
            else:
                customer_name = debt.customer.full_name or "N/A"
        print(f"  Paying debt {debt.id}: {customer_name}")

    # Memory-efficient processing
    print("\n--- Memory-Efficient Statistics ---")
    stats = {"total": 0, "total_amount": 0, "status_counts": {}}

    for debt in client.debts.iterate(limit_per_page=20, max_pages=2):
        stats["total"] += 1
        stats["total_amount"] += debt.summary.amount_total

        status = str(debt.status.value)
        stats["status_counts"][status] = stats["status_counts"].get(status, 0) + 1

        if stats["total"] % 10 == 0:
            print(f"  Processed {stats['total']} debts...")

    print("\n  📊 Final Stats:")
    print(f"    Total debts: {stats['total']}")
    print(f"    Total amount: ${stats['total_amount'] / 100:.2f}")
    print(f"    Status breakdown: {dict(list(stats['status_counts'].items())[:3])}")


def search_pagination_examples():
    """Search with pagination examples."""
    client = setup_client()

    print("\n" + "=" * 60)
    print("3. SEARCH WITH PAGINATION")
    print("=" * 60)

    # Basic search pagination
    print("\n--- Basic Search Pagination ---")
    search_results = client.debts.search(query="status:paid", limit=5)
    print(f"Search results: {len(search_results.data)} debts")

    for debt in search_results.data[:3]:
        print(f"  Page 1 debt: {debt.id} - ${debt.summary.amount_total / 100:.2f}")

    # Search with generator
    print("\n--- Search Generator ---")
    try:
        count = 0
        for debt in client.debts.iterate_search(query="total_amount>5000", limit_per_page=5, max_pages=2):
            count += 1
            print(f"  Found debt {debt.id}: ${debt.summary.amount_total / 100:.2f}")
            if count >= 3:
                print(f"     ... (showing 3 of {count}+ results)")
                break
    except AttributeError:
        print("🔍 Searching with generator...")


def cross_resource_consistency():
    """Show consistent pagination across all resources."""
    client = setup_client()

    print("\n" + "=" * 60)
    print("4. CROSS-RESOURCE CONSISTENCY")
    print("=" * 60)

    print("\n--- All Resources Support Same Iterator API ---")

    # Common parameters work across all resources
    common_params = {"limit_per_page": 3, "max_pages": 1}

    resources = [
        ("Debts", client.debts),
        ("Customers", client.customers),
        ("Organisations", client.organisations),
        ("Payments", client.payments),
        ("Webhooks", client.webhooks),
        ("Payment Plans", client.payment_plans),
    ]

    for name, resource in resources:
        print(f"\n--- {name} Iterator ---")
        try:
            count = 0
            for item in resource.iterate(**common_params):
                count += 1
                # Handle different object types
                if hasattr(item, "name"):
                    identifier = item.name
                elif hasattr(item, "status"):
                    identifier = item.status
                elif hasattr(item, "url"):
                    identifier = item.url[:50] + "..."
                else:
                    identifier = "Active"

                print(f"  {name[:-1]} {item.id}: {identifier}")
                if count >= 2:  # Limit output
                    print("     ... (showing 2 items)")
                    break
        except Exception as e:
            print(f"  No data available: {e}")


def chunked_processing_example():
    """Demonstrate chunked/batch processing."""
    client = setup_client()

    print("\n" + "=" * 60)
    print("5. CHUNKED/BATCH PROCESSING")
    print("=" * 60)

    print("\n--- Processing in Chunks ---")

    chunk_size = 5
    chunk = []
    chunk_num = 1

    for debt in client.debts.iterate(limit_per_page=10, max_pages=2):
        chunk.append(debt)

        # Process when chunk is full
        if len(chunk) >= chunk_size:
            print(f"\nProcessing chunk {chunk_num} ({len(chunk)} debts):")

            # Simulate batch processing
            total_amount = sum(debt.summary.amount_total for debt in chunk)
            statuses = [str(debt.status.value) for debt in chunk]

            print(f"  Total amount: ${total_amount / 100:.2f}")
            print(f"  Statuses: {', '.join(set(statuses))}")

            # Here you could do batch operations:
            # - Bulk database inserts
            # - Batch API calls
            # - Email notifications

            chunk = []  # Reset chunk
            chunk_num += 1

    # Process remaining items
    if chunk:
        print(f"\nProcessing final chunk {chunk_num} ({len(chunk)} debts)")


def cursor_based_navigation():
    """Demonstrate cursor-based navigation using Link headers."""
    client = setup_client()

    print("\n" + "=" * 60)
    print("6. CURSOR-BASED NAVIGATION")
    print("=" * 60)

    print("\n--- Easy Navigation with Cursors ---")

    # Get first page
    page = client.debts.list(limit=3)
    print(f"Current page: {len(page.data)} debts, has_more: {page.has_more}")

    if page.pagination:
        print("Available navigation options:")
        for rel, info in page.pagination.items():
            cursor_type = "after" if "after" in info else "before" if "before" in info else "none"
            cursor_value = info.get("after") or info.get("before", "N/A")
            print(f"  {rel}: {cursor_type}={cursor_value}")

        # Navigate to next page using cursor
        if "next" in page.pagination:
            print("\n--- Navigating to Next Page ---")
            next_after = page.pagination["next"]["after"]
            next_page = client.debts.list(limit=3, after=next_after)
            print(f"Next page: {len(next_page.data)} debts")

            # Navigate back to previous page using cursor
            if next_page.pagination and "prev" in next_page.pagination:
                print("\n--- Navigating Back to Previous Page ---")
                prev_before = next_page.pagination["prev"]["before"]
                prev_page = client.debts.list(limit=3, before=prev_before)
                print(f"Previous page: {len(prev_page.data)} debts")


def advanced_patterns():
    """Advanced pagination patterns."""
    client = setup_client()

    print("\n" + "=" * 60)
    print("7. ADVANCED PATTERNS")
    print("=" * 60)

    # Conditional processing
    print("\n--- Conditional Processing ---")
    processed = 0
    skipped = 0

    for debt in client.debts.iterate(limit_per_page=15, max_pages=2):
        # Only process debts over a certain amount
        if debt.summary.amount_total > 10000:  # $100+
            processed += 1
            print(f"  Processing high-value debt {debt.id}: ${debt.summary.amount_total / 100:.2f}")
        else:
            skipped += 1

        # Early termination
        if processed >= 5:
            print(f"  Processed {processed} high-value debts (skipped {skipped} smaller ones)")
            break

    # Error handling with generators
    print("\n--- Generator Error Handling ---")
    try:
        for i, debt in enumerate(client.debts.iterate(limit_per_page=5, max_pages=1)):
            if i >= 3:  # Process only first 3
                break
            print(f"  Processing debt {debt.id}")
            # Your processing logic here
    except Exception as e:
        print(f"  Error during iteration: {e}")

    print("📝 Generator notes:")
    print("  • Memory efficient - only loads one page at a time")
    print("  • Automatic pagination - no manual cursor management")
    print("  • Consistent API across all resource types")


def main():
    """Run all pagination examples."""
    print("🔄 Ophelos SDK - Complete Pagination & Generators Guide")
    print("=" * 60)

    try:
        basic_pagination_examples()
        generator_iteration_examples()
        search_pagination_examples()
        cross_resource_consistency()
        chunked_processing_example()
        cursor_based_navigation()
        advanced_patterns()

        print("\n" + "=" * 60)
        print("✅ All pagination examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Set these environment variables:")
        print("   export OPHELOS_CLIENT_ID='your_client_id'")
        print("   export OPHELOS_CLIENT_SECRET='your_client_secret'")
        print("   export OPHELOS_AUDIENCE='your_audience'")


if __name__ == "__main__":
    main()
