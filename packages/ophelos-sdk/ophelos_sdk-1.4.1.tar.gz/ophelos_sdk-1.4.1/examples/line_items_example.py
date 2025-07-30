"""
Example: Working with Line Items

This example demonstrates how to use the LineItemsResource to create and list
line items for debts using the Ophelos SDK.
"""

import os
from datetime import datetime

from ophelos_sdk import OphelosClient
from ophelos_sdk.models import LineItem, LineItemKind, Currency


def main():
    """Main function demonstrating line items operations."""

    # Initialize client with access token from environment
    client = OphelosClient(
        access_token=os.getenv("OPHELOS_ACCESS_TOKEN", "your_access_token_here"),
        environment="development",  # Change to "production" for live API
    )

    # Example debt ID (replace with a real debt ID)
    debt_id = "debt_123456789"

    print("=== Line Items Management Example ===\n")

    # Example 1: Create a line item using a dictionary
    print("1. Creating line item with dictionary data...")
    try:
        line_item_data = {
            "kind": "debt",
            "description": "Principal amount",
            "amount": 100000,  # Amount in cents (£1000.00)
            "currency": "GBP",
            "metadata": {"category": "principal"},
        }

        created_line_item = client.line_items.create(debt_id, line_item_data)
        print(f"✓ Line item created: {created_line_item.id}")
        print(f"  Kind: {created_line_item.kind}")
        print(f"  Description: {created_line_item.description}")
        print(f"  Amount: {created_line_item.amount} {created_line_item.currency}")
        print()

    except Exception as e:
        print(f"✗ Error creating line item: {e}\n")


    # Example 2: Create a line item using LineItem model with enums and transaction_at
    print("2. Creating line item with model, enums, and transaction_at...")
    try:
        line_item = LineItem(
            kind=LineItemKind.INTEREST,
            description="Monthly interest charge",
            amount=2500,  # Amount in cents (£25.00)
            currency=Currency.GBP,
            transaction_at=datetime.now(),  # Specific transaction timestamp
            metadata={"interest_rate": "5.5%"},
        )

        # LineItem instances can be passed directly - no need to call to_api_body()
        # Both approaches work: client.line_items.create(debt_id, line_item)
        #                  or: client.line_items.create(debt_id, line_item.to_api_body())
        created_line_item = client.line_items.create(debt_id, line_item)
        print(f"✓ Line item created: {created_line_item.id}")
        print(f"  Kind: {created_line_item.kind}")
        print(f"  Description: {created_line_item.description}")
        print(f"  Amount: {created_line_item.amount} {created_line_item.currency}")
        print(f"  Transaction at: {created_line_item.transaction_at}")
        print()

    except Exception as e:
        print(f"✗ Error creating line item: {e}\n")

    # Example 3: Create multiple line items
    print("3. Creating multiple line items...")
    try:
        line_items_data = [
            {
                "kind": "fee",
                "description": "Processing fee",
                "amount": 1500,  # £15.00
                "currency": "GBP",
            },
            {
                "kind": "vat",
                "description": "VAT on processing fee",
                "amount": 300,  # £3.00 (20% VAT)
                "currency": "GBP",
            },
        ]

        for i, data in enumerate(line_items_data, 1):
            created_line_item = client.line_items.create(debt_id, data)
            print(f"✓ Line item {i} created: {created_line_item.id}")
            print(f"  Kind: {created_line_item.kind}")
            print(f"  Description: {created_line_item.description}")
            print(f"  Amount: {created_line_item.amount} {created_line_item.currency}")
        print()

    except Exception as e:
        print(f"✗ Error creating multiple line items: {e}\n")

    # Example 4: List all line items for a debt
    print("4. Listing all line items for debt...")
    try:
        line_items = client.line_items.list(debt_id, limit=10)
        print(f"✓ Found {len(line_items.data)} line items")
        
        total_amount = 0
        for i, item in enumerate(line_items.data, 1):
            print(f"  {i}. {item.kind}: {item.description} - {item.amount} {item.currency}")
            total_amount += item.amount or 0

        print(f"  Total amount: {total_amount} {line_items.data[0].currency if line_items.data else 'GBP'}")

        if line_items.has_more:
            print("  ... and more results available")
        print()

    except Exception as e:
        print(f"✗ Error listing line items: {e}\n")

    # Example 5: List line items with pagination
    print("5. Paginated listing of line items...")
    try:
        # Get first page
        first_page = client.line_items.list(debt_id, limit=5)
        print(f"✓ First page: {len(first_page.data)} line items")

        if first_page.has_more and first_page.data:
            # Get next page using the last item's ID as cursor
            last_item_id = first_page.data[-1].id
            next_page = client.line_items.list(debt_id, limit=5, after=last_item_id)
            print(f"✓ Next page: {len(next_page.data)} line items")

        print()

    except Exception as e:
        print(f"✗ Error with paginated listing: {e}\n")

    # Example 6: Create credit/refund line items (negative amounts)
    print("6. Creating credit/refund line items...")
    try:
        credit_data = {
            "kind": "credit",
            "description": "Account credit applied",
            "amount": -5000,  # Negative amount for credit (£50.00)
            "currency": "GBP",
            "metadata": {"credit_reason": "overpayment"},
        }

        created_credit = client.line_items.create(debt_id, credit_data)
        print(f"✓ Credit line item created: {created_credit.id}")
        print(f"  Kind: {created_credit.kind}")
        print(f"  Description: {created_credit.description}")
        print(f"  Amount: {created_credit.amount} {created_credit.currency}")
        print()

    except Exception as e:
        print(f"✗ Error creating credit line item: {e}\n")

    print("=== Line Items Example Complete ===")


if __name__ == "__main__":
    main() 