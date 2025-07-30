#!/usr/bin/env python3
"""
Enhanced Pagination Demo - Shows the improved cursor-based navigation

This demonstrates the enhanced pagination functionality that extracts cursor values
from Link headers, making pagination much easier to use.
"""

import os

from ophelos_sdk import OphelosClient


def demonstrate_enhanced_pagination():
    """Demonstrate the enhanced pagination with cursor extraction."""

    client = OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID", "demo_client_id"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET", "demo_client_secret"),
        audience=os.getenv("OPHELOS_AUDIENCE", "demo_audience"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "development"),
    )

    print("🔄 Enhanced Pagination Demo")
    print("=" * 50)

    # Get first page with small limit to demonstrate pagination
    print("\n1. Fetching first page...")
    page1 = client.debts.list(limit=2)

    print(f"   📄 Page 1: {len(page1.data)} debts")
    print(f"   🔗 Has more: {page1.has_more}")
    if page1.total_count:
        print(f"   📊 Total count: {page1.total_count}")

    # Show pagination cursors available
    if page1.pagination:
        print("\n   🧭 Navigation cursors available:")
        for relation, info in page1.pagination.items():
            cursor_key = "after" if "after" in info else "before" if "before" in info else "none"
            cursor_value = info.get("after") or info.get("before", "N/A")
            print(f"      {relation}: {cursor_key}={cursor_value}")

    # Navigate to next page using cursor (much easier than before!)
    if page1.has_more and page1.pagination and "next" in page1.pagination:
        print("\n2. Navigating to next page using cursor...")
        next_cursor = page1.pagination["next"]["after"]
        print(f"   🎯 Using cursor: after={next_cursor}")

        page2 = client.debts.list(limit=2, after=next_cursor)
        print(f"   📄 Page 2: {len(page2.data)} debts")
        print(f"   🔗 Has more: {page2.has_more}")

        # Show available navigation options for page 2
        if page2.pagination:
            print("\n   🧭 Available navigation from page 2:")
            for relation, info in page2.pagination.items():
                cursor_key = "after" if "after" in info else "before" if "before" in info else "none"
                cursor_value = info.get("after") or info.get("before", "N/A")
                print(f"      {relation}: {cursor_key}={cursor_value}")

            # Go back to previous page
            if "prev" in page2.pagination:
                print("\n3. Going back to previous page...")
                prev_cursor = page2.pagination["prev"]["before"]
                print(f"   🎯 Using cursor: before={prev_cursor}")

                prev_page = client.debts.list(limit=2, before=prev_cursor)
                print(f"   📄 Previous page: {len(prev_page.data)} debts")

    print("\n✅ Enhanced pagination working perfectly!")
    print("\nKey improvements:")
    print("• 🎯 Cursors extracted automatically from Link headers")
    print("• 🧭 Easy navigation with pagination.next.after, pagination.prev.before")
    print("• 🔗 No need to manually extract last item IDs")
    print("• 📊 Total count from X-Total-Count header")
    print("• 🏠 Support for first page navigation")


if __name__ == "__main__":
    demonstrate_enhanced_pagination()
