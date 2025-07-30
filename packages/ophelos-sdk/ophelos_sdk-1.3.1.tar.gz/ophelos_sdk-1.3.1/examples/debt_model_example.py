#!/usr/bin/env python3
"""
Robust Debt Models Example with Error Handling

This example shows how to safely work with debt model objects
and handles authentication and API errors gracefully.
"""

import os

from ophelos_sdk import OphelosClient
from ophelos_sdk.exceptions import AuthenticationError, OphelosAPIError
from ophelos_sdk.models import DebtStatus


def setup_client():
    """Initialize the Ophelos client with environment variables."""
    return OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID", "your_client_id"),
        client_secret=os.getenv(
            "OPHELOS_CLIENT_SECRET",
            "your_client_secret",
        ),
        audience=os.getenv("OPHELOS_AUDIENCE", "your_audience"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "development"),  # staging, development, production
    )


def safe_debt_list_example():
    """Safely demonstrate debt list with model objects."""
    print("💰 Safe Debt List with Model Objects")
    print("=" * 60)

    # Check environment variables
    required_vars = ["OPHELOS_CLIENT_ID", "OPHELOS_CLIENT_SECRET", "OPHELOS_AUDIENCE"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("\nPlease set:")
        for var in missing_vars:
            print(f"  export {var}='your_value'")
        return False

    try:
        client = setup_client()
        print(f"✅ Client initialized (environment: {client.authenticator.environment})")

        # Test connection
        print("\n--- Testing Connection ---")
        if not client.test_connection():
            print("❌ Connection test failed")
            return False
        print("✅ Connection successful")

        print("\n--- Fetching Debts (with Model Objects) ---")
        debts_page = client.debts.list(limit=3, expand=["customer", "organisation"])

        print(f"📊 Response type: {type(debts_page)}")
        print(f"📊 Found {len(debts_page.data)} debts")
        print(f"📄 Has more: {debts_page.has_more}")

        # Process each debt - these should be Debt model objects
        for i, debt in enumerate(debts_page.data, 1):
            _process_debt(debt, i)

        return True

    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Check your credentials and try again")
        return False

    except OphelosAPIError as e:
        print(f"❌ API error: {e}")
        print(f"💡 Status code: {e.status_code}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


def _process_debt(debt, index):
    """Process a single debt object to reduce complexity."""
    print(f"\n━━━ Debt #{index} ━━━")

    # Verify it's a model object
    print(f"🔍 Type: {type(debt)}")
    print(f"🔍 Has 'id' attribute: {hasattr(debt, 'id')}")

    if hasattr(debt, "id"):
        _print_debt_details(debt)
    else:
        _handle_dict_debt(debt)


def _print_debt_details(debt):
    """Print details for a proper debt model object."""
    print(f"✅ ID: {debt.id}")
    print(f"✅ Amount: ${debt.summary.amount_total / 100:.2f}")
    print(f"✅ Status: {debt.status.value} (type: {type(debt.status.value)})")
    print(f"✅ Created: {debt.created_at}")

    # Type-safe enum comparisons
    if debt.status.value == DebtStatus.PAYING:
        print("  🟢 This debt is currently being paid")
    elif debt.status.value == DebtStatus.PAID:
        print("  🎉 This debt has been fully paid")

    _print_debt_relations(debt)


def _print_debt_relations(debt):
    """Print debt customer and organisation relations."""
    # Safe customer access
    if debt.customer:
        if isinstance(debt.customer, str):
            print(f"  👤 Customer ID: {debt.customer}")
        else:
            print(f"  👤 Customer: {debt.customer.full_name or 'Unknown'}")
        print(f"  👤 Customer type: {type(debt.customer)}")

    # Safe organisation access
    if debt.organisation:
        if isinstance(debt.organisation, str):
            print(f"  🏢 Organisation ID: {debt.organisation}")
        else:
            print(f"  🏢 Organisation: {debt.organisation.name}")


def _handle_dict_debt(debt):
    """Handle the case where debt is still a dictionary."""
    print("❌ Unexpected: Got dictionary instead of model object")
    print(f"❌ Content: {debt}")

    # Fallback dictionary access
    if isinstance(debt, dict):
        print(f"📋 ID (dict): {debt.get('id', 'N/A')}")
        print(f"📋 Status (dict): {debt.get('status', 'N/A')}")


def pagination_with_models():
    """Show pagination working with model objects."""
    print("\n" + "=" * 60)
    print("📄 PAGINATION WITH MODEL OBJECTS")
    print("=" * 60)

    try:
        client = setup_client()

        print("\n--- Memory-Efficient Iterator ---")
        count = 0
        for debt in client.debts.iterate(limit_per_page=5, max_pages=2):
            count += 1
            # debt is automatically a Debt model object
            print(f"  {count}. Debt {debt.id}: ${debt.summary.amount_total / 100:.2f} ({debt.status.value})")

            if count >= 3:  # Limit output for demo
                print(f"  ... (showing 3 of {count}+ total)")
                break

        print(f"\n✅ Processed {count} debt model objects")

    except Exception as e:
        print(f"❌ Iterator error: {e}")


def main():
    """Run the robust debt example."""
    print("🛡️ Ophelos SDK - Robust Debt Models Example")
    print("This example shows model objects working with proper error handling")

    # Run safe example
    success = safe_debt_list_example()

    if success:
        pagination_with_models()

        print("\n" + "=" * 60)
        print("🎉 SUCCESS: Model Objects Working!")
        print("=" * 60)
        print("✅ API responses automatically become Debt model objects")
        print("✅ Type-safe attribute access (debt.status.value)")
        print("✅ Enum comparisons (DebtStatus.PAYING)")
        print("✅ Nested model objects (debt.customer)")
        print("✅ IDE autocompletion and error detection")
    else:
        print("\n" + "=" * 60)
        print("ℹ️ SETUP REQUIRED")
        print("=" * 60)
        print("Set your environment variables to see model objects in action:")
        print("  export OPHELOS_CLIENT_ID='your_client_id'")
        print("  export OPHELOS_CLIENT_SECRET='your_client_secret'")
        print("  export OPHELOS_AUDIENCE='your_audience'")
        print("  export OPHELOS_ENVIRONMENT='staging'  # optional")


if __name__ == "__main__":
    main()
