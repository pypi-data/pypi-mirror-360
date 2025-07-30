#!/usr/bin/env python3
"""
All Resources Direct Model Usage Example

This example demonstrates how all Ophelos SDK resources now support
passing model instances directly to create and update methods.

Set API_CALL = False to only print payloads without making API calls.
Set API_CALL = True to make actual API calls.
"""

import json
import os
from datetime import date, datetime

from pydantic import ValidationError

from ophelos_sdk import OphelosClient
from ophelos_sdk.models import Customer, Debt, DebtStatus, Payment, PaymentStatus

# Configuration: Set to False to only print payloads, True to make API calls
API_CALL = False


def setup_client():
    """Initialize the Ophelos client."""
    return OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID", "your_client_id"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET", "your_client_secret"),
        audience=os.getenv("OPHELOS_AUDIENCE", "your_audience"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "staging"),
    )


def print_payload(client, operation, resource, model, additional_info=""):
    """Print the API payload that would be sent."""
    print(f"\n📤 {operation} {resource} Payload{additional_info}:")
    print("=" * 50)

    try:
        # Use the model's to_api_body() method directly
        if hasattr(model, "to_api_body"):
            payload = model.to_api_body()
        else:
            # Fallback to manual processing for non-model data
            payload = simulate_prepare_data(model)

        print(json.dumps(payload, indent=2, default=str))
    except Exception as e:
        print(f"❌ Error generating payload: {e}")
        # Fallback to raw model dump
        try:
            payload = model.model_dump() if hasattr(model, "model_dump") else model
            print("Fallback - Raw model data:")
            print(json.dumps(payload, indent=2, default=str))
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")

    print("=" * 50)


def simulate_prepare_data(data):
    """Fallback data preparation for when to_api_body() isn't available."""
    from ophelos_sdk.models import BaseOphelosModel

    if isinstance(data, BaseOphelosModel):
        # Use to_api_body() if available (it should be on all models now)
        if hasattr(data, "to_api_body"):
            return data.to_api_body()

        # Fallback to manual processing (legacy support)
        model_data = data.model_dump()

        # Remove server-generated fields that shouldn't be sent in create/update
        server_fields = {"id", "object", "created_at", "updated_at"}
        api_data = {}

        for key, value in model_data.items():
            if key in server_fields or value is None:
                continue

            # Handle nested model objects/lists (simplified version)
            processed_value = process_nested_value_simple(value, key)
            api_data[key] = processed_value

        return api_data

    return data


def process_nested_value_simple(value, field_name=""):
    """Simplified version of nested value processing."""
    from ophelos_sdk.models import BaseOphelosModel

    if isinstance(value, BaseOphelosModel):
        # Only convert to ID reference for specific relationship fields with real IDs
        should_convert_to_id = (
            field_name in {"customer", "organisation"}
            and hasattr(value, "id")
            and value.id
            and not value.id.startswith("temp")
        )

        if should_convert_to_id:
            return value.id

        # In all other cases, return the full model data (excluding server fields)
        model_data = value.model_dump()
        server_fields = {"id", "object", "created_at", "updated_at"}
        return {
            k: process_nested_value_simple(v, k)
            for k, v in model_data.items()
            if k not in server_fields and v is not None
        }

    elif isinstance(value, list):
        # Process each item in the list
        return [process_nested_value_simple(item, field_name) for item in value]

    elif isinstance(value, dict):
        # Process nested dictionaries recursively
        return {k: process_nested_value_simple(v, k) for k, v in value.items()}

    else:
        # Primitive value, return as-is
        return value


def customer_direct_model_example(client):
    """Demonstrate direct Customer model usage."""
    print("\n" + "=" * 50)
    print("👥 CUSTOMER - DIRECT MODEL USAGE")
    print("=" * 50)

    try:
        # Create Customer model
        customer_model = Customer(
            id="temp_customer",
            object="customer",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            kind="individual",
            first_name="Alex",
            last_name="Thompson",
            preferred_locale="en-US",
            metadata={"source": "all_resources_example", "account_type": "premium"},
        )

        print("Creating customer using direct model...")
        print(type(customer_model))
        print_payload(client, "CREATE", "Customer", customer_model)

        if API_CALL:
            created_customer = client.customers.create(customer_model)
            print(f"✅ Customer created: {created_customer.id} - {created_customer.full_name}")
        else:
            # Simulate created customer for demo purposes
            created_customer = customer_model
            created_customer.id = "cust_demo_123"
            print(f"🔍 [DEMO MODE] Would create customer: {created_customer.id} - {created_customer.full_name}")

        # Update using modified model
        print("\nUpdating customer using modified model...")
        created_customer.preferred_locale = "en-GB"
        created_customer.metadata["last_updated"] = datetime.now().isoformat()

        print_payload(client, "UPDATE", "Customer", created_customer, f" (ID: {created_customer.id})")

        if API_CALL:
            updated_customer = client.customers.update(created_customer.id, created_customer)
            print(f"✅ Customer updated: Locale changed to {updated_customer.preferred_locale}")
        else:
            print(f"🔍 [DEMO MODE] Would update customer: Locale changed to {created_customer.preferred_locale}")

        return created_customer

    except Exception as e:
        print(f"❌ Customer model error: {e}")
        return None


def debt_direct_model_example(client, customer_id):
    """Demonstrate direct Debt model usage."""
    print("\n" + "=" * 50)
    print("💰 DEBT - DIRECT MODEL USAGE")
    print("=" * 50)

    try:
        # Create Debt model
        debt_model = Debt(
            id="temp_debt",
            object="debt",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status={
                "value": DebtStatus.PREPARED,
                "whodunnit": "system",
                "context": None,
                "reason": None,
                "updated_at": datetime.now(),
            },
            kind="purchased",
            account_number="ACC-001",
            customer=customer_id,
            organisation="org_default",  # This would be a real org ID
            currency="GBP",
            summary={
                "amount_total": 50000,  # £500.00 in pence
                "amount_paid": 0,
                "amount_remaining": 50000,
                "breakdown": {"principal": 50000, "interest": 0, "fees": 0},
            },
            balance_amount=50000,
            start_at=date.today(),
            metadata={"source": "all_resources_example", "priority": "high"},
        )

        print("Creating debt using direct model...")
        print_payload(client, "CREATE", "Debt", debt_model)

        if API_CALL:
            created_debt = client.debts.create(debt_model)
            print(f"✅ Debt created: {created_debt.id} - £{created_debt.summary.amount_total / 100:.2f}")
        else:
            # Simulate created debt for demo purposes
            created_debt = debt_model
            created_debt.id = "debt_demo_123"
            print(
                f"🔍 [DEMO MODE] Would create debt: {created_debt.id} - £{created_debt.summary.amount_total / 100:.2f}"
            )

        # Update using modified model
        print("\nUpdating debt using modified model...")
        created_debt.account_number = "ACC-001-UPDATED"
        created_debt.metadata["last_updated"] = datetime.now().isoformat()

        print_payload(client, "UPDATE", "Debt", created_debt, f" (ID: {created_debt.id})")

        if API_CALL:
            updated_debt = client.debts.update(created_debt.id, created_debt)
            print(f"✅ Debt updated: Account number changed to {updated_debt.account_number}")
        else:
            print(f"🔍 [DEMO MODE] Would update debt: Account number changed to {created_debt.account_number}")

        return created_debt

    except Exception as e:
        print(f"❌ Debt model error: {e}")
        return None


def payment_direct_model_example(client, debt_id):
    """Demonstrate direct Payment model usage for debt payments."""
    print("\n" + "=" * 50)
    print("💳 PAYMENT - DIRECT MODEL USAGE")
    print("=" * 50)

    try:
        # Create Payment model
        payment_model = Payment(
            id="temp_payment",
            object="payment",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            debt=debt_id,
            status=PaymentStatus.SUCCEEDED,
            transaction_at=datetime.now(),
            transaction_ref="TXN-12345",
            amount=15000,  # £150.00 in pence
            currency="GBP",
            payment_provider="stripe",
            metadata={"source": "all_resources_example", "payment_method": "card"},
        )

        print("Creating payment using direct model...")
        print_payload(client, "CREATE", "Payment", payment_model, f" (for debt {debt_id})")

        if API_CALL:
            created_payment = client.debts.create_payment(debt_id, payment_model)
            print(f"✅ Payment created: {created_payment.id} - £{created_payment.amount / 100:.2f}")
        else:
            # Simulate created payment for demo purposes
            created_payment = payment_model
            created_payment.id = "pay_demo_123"
            print(f"🔍 [DEMO MODE] Would create payment: {created_payment.id} - £{created_payment.amount / 100:.2f}")

        # Update using modified model
        print("\nUpdating payment using modified model...")
        created_payment.transaction_ref = "TXN-12345-UPDATED"
        created_payment.metadata["last_updated"] = datetime.now().isoformat()

        print_payload(
            client,
            "UPDATE",
            "Payment",
            created_payment,
            f" (ID: {created_payment.id}, debt: {debt_id})",
        )

        if API_CALL:
            updated_payment = client.debts.update_payment(debt_id, created_payment.id, created_payment)
            print(f"✅ Payment updated: Transaction ref changed to {updated_payment.transaction_ref}")
        else:
            print(f"🔍 [DEMO MODE] Would update payment: Transaction ref changed to {created_payment.transaction_ref}")

        return created_payment

    except Exception as e:
        print(f"❌ Payment model error: {e}")
        return None


def model_factory_patterns_example(client):
    """Demonstrate factory patterns with direct model usage."""
    print("\n" + "=" * 50)
    print("🏭 MODEL FACTORY PATTERNS")
    print("=" * 50)

    # Factory functions for different model types
    def create_test_customer(first_name, last_name, customer_type="individual"):
        """Factory for test customers."""
        return Customer(
            id="temp_factory_customer",
            object="customer",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            kind=customer_type,
            first_name=first_name,
            last_name=last_name,
            full_name=f"{first_name} {last_name}",
            preferred_locale="en-US",
            metadata={"source": "factory_pattern", "test_customer": True, "created_via": "factory"},
        )

    def create_test_debt(customer_id, amount, reference):
        """Factory for test debts."""
        return Debt(
            id="temp_factory_debt",
            object="debt",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status={
                "value": DebtStatus.PREPARED,
                "whodunnit": "factory",
                "updated_at": datetime.now(),
            },
            customer=customer_id,
            organisation="org_default",
            account_number=reference,
            summary={"amount_total": amount, "amount_paid": 0, "amount_remaining": amount},
            balance_amount=amount,
            currency="GBP",
            metadata={"source": "factory_pattern", "test_debt": True},
        )

    created_objects = []

    try:
        # Use factories to create models, then pass directly to API
        print("Creating customer via factory...")
        customer_model = create_test_customer("Factory", "Customer", "individual")
        print_payload(client, "CREATE", "Customer", customer_model, " (via factory)")

        if API_CALL:
            customer = client.customers.create(customer_model)
            created_objects.append(("Customer", customer.id, customer.full_name))
            print(f"✅ Factory customer: {customer.id}")
        else:
            customer = customer_model
            customer.id = "cust_factory_demo"
            created_objects.append(("Customer", customer.id, customer.full_name))
            print(f"🔍 [DEMO MODE] Factory customer: {customer.id}")

        print("\nCreating debt via factory...")
        debt_model = create_test_debt(customer.id, 25000, "FACTORY-001")
        print_payload(client, "CREATE", "Debt", debt_model, " (via factory)")

        if API_CALL:
            debt = client.debts.create(debt_model)
            created_objects.append(("Debt", debt.id, f"£{debt.summary.amount_total / 100:.2f}"))
            print(f"✅ Factory debt: {debt.id}")
        else:
            debt = debt_model
            debt.id = "debt_factory_demo"
            created_objects.append(("Debt", debt.id, f"£{debt.summary.amount_total / 100:.2f}"))
            print(f"🔍 [DEMO MODE] Factory debt: {debt.id}")

        print(f"\n📊 Factory pattern created {len(created_objects)} objects")
        return created_objects

    except Exception as e:
        print(f"❌ Factory pattern error: {e}")
        return created_objects


def model_validation_benefits_example(client):
    """Demonstrate the validation benefits of using models."""
    print("\n" + "=" * 50)
    print("✅ MODEL VALIDATION BENEFITS")
    print("=" * 50)

    # Test cases with validation errors
    validation_tests = [
        {
            "name": "Valid Customer",
            "factory": lambda: Customer(
                id="temp",
                object="customer",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                first_name="Valid",
                last_name="Customer",
            ),
            "should_pass": True,
        },
        {
            "name": "Invalid Date Customer",
            "factory": lambda: Customer(
                id="temp",
                object="customer",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                first_name="Invalid",
                last_name="Customer",
                date_of_birth="not-a-date",  # This should cause validation error
            ),
            "should_pass": False,
        },
    ]

    for test in validation_tests:
        print(f"\n--- Testing: {test['name']} ---")
        try:
            # Create model (validation happens here)
            model = test["factory"]()
            print("✅ Model validation passed")

            if test["should_pass"]:
                print_payload(client, "CREATE", "Customer", model, " (validation test)")
                if API_CALL:
                    # Try to create via API
                    customer = client.customers.create(model)
                    print(f"✅ API creation succeeded: {customer.id}")
                else:
                    print("🔍 [DEMO MODE] Would create customer via API")
            else:
                print("⚠️ Expected validation to fail, but it passed")

        except ValidationError as e:
            if not test["should_pass"]:
                print(f"✅ Expected validation error caught: {str(e)[:100]}...")
            else:
                print(f"❌ Unexpected validation error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def cross_resource_workflow_example(client):
    """Demonstrate a complete workflow using direct models across resources."""
    print("\n" + "=" * 50)
    print("🔄 CROSS-RESOURCE WORKFLOW")
    print("=" * 50)

    workflow_objects = []

    try:
        # Step 1: Create customer
        print("Step 1: Creating customer...")
        customer = Customer(
            id="temp_workflow",
            object="customer",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            first_name="Workflow",
            last_name="Customer",
            kind="individual",
            preferred_locale="en-US",
            metadata={"workflow": "cross_resource", "step": 1},
        )
        print_payload(client, "CREATE", "Customer", customer, " (workflow step 1)")

        if API_CALL:
            created_customer = client.customers.create(customer)
            workflow_objects.append(created_customer)
            print(f"✅ Customer: {created_customer.id}")
        else:
            created_customer = customer
            created_customer.id = "cust_workflow_demo"
            workflow_objects.append(created_customer)
            print(f"🔍 [DEMO MODE] Customer: {created_customer.id}")

        # Step 2: Create debt for customer
        print("\nStep 2: Creating debt...")
        debt = Debt(
            id="temp_workflow_debt",
            object="debt",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            customer=created_customer.id,
            organisation="org_default",
            status={
                "value": DebtStatus.PREPARED,
                "whodunnit": "workflow",
                "updated_at": datetime.now(),
            },
            account_number="WORKFLOW-001",
            summary={"amount_total": 75000, "amount_paid": 0, "amount_remaining": 75000},
            balance_amount=75000,
            currency="GBP",
            metadata={"workflow": "cross_resource", "step": 2},
        )
        print_payload(client, "CREATE", "Debt", debt, " (workflow step 2)")

        if API_CALL:
            created_debt = client.debts.create(debt)
            workflow_objects.append(created_debt)
            print(f"✅ Debt: {created_debt.id}")
        else:
            created_debt = debt
            created_debt.id = "debt_workflow_demo"
            workflow_objects.append(created_debt)
            print(f"🔍 [DEMO MODE] Debt: {created_debt.id}")

        # Step 3: Create payment for debt
        print("\nStep 3: Creating payment...")
        payment = Payment(
            id="temp_workflow_payment",
            object="payment",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            debt=created_debt.id,
            status=PaymentStatus.SUCCEEDED,
            transaction_at=datetime.now(),
            amount=25000,
            currency="GBP",
            transaction_ref="WORKFLOW-PAY-001",
            metadata={"workflow": "cross_resource", "step": 3},
        )
        print_payload(client, "CREATE", "Payment", payment, " (workflow step 3)")

        if API_CALL:
            created_payment = client.debts.create_payment(created_debt.id, payment)
            workflow_objects.append(created_payment)
            print(f"✅ Payment: {created_payment.id}")
        else:
            created_payment = payment
            created_payment.id = "pay_workflow_demo"
            workflow_objects.append(created_payment)
            print(f"🔍 [DEMO MODE] Payment: {created_payment.id}")

        print(f"\n🎉 Workflow completed! Created {len(workflow_objects)} objects.")
        return workflow_objects

    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return workflow_objects


def main():
    """Run all direct model usage examples across resources."""
    print("📚 Ophelos SDK - All Resources Direct Model Usage")
    print(f"🔧 Mode: {'API CALLS ENABLED' if API_CALL else 'PAYLOAD PREVIEW ONLY'}")

    if not API_CALL:
        print("💡 Set API_CALL = True to make actual API calls")
        print("📤 Currently showing payloads that would be sent to API")

    # Check environment variables only if making API calls
    if API_CALL:
        required_vars = ["OPHELOS_CLIENT_ID", "OPHELOS_CLIENT_SECRET", "OPHELOS_AUDIENCE"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print("\n💡 Missing required environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\nSet these environment variables and try again.")
            return

    # Setup client
    client = setup_client()

    try:
        # Test connection only if making API calls
        if API_CALL:
            if not client.test_connection():
                print("❌ Failed to connect to Ophelos API")
                return
            print("✅ Connected to Ophelos API successfully!")
        else:
            print("🔍 Running in demo mode - no API connection needed")

        # Run examples across all resources
        customer = customer_direct_model_example(client)

        if customer:
            debt = debt_direct_model_example(client, customer.id)

            if debt:
                payment_direct_model_example(client, debt.id)

        # Advanced patterns
        factory_objects = model_factory_patterns_example(client)
        model_validation_benefits_example(client)
        workflow_objects = cross_resource_workflow_example(client)

        # Summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE SUMMARY")
        print("=" * 70)

        print("✅ All resources now support direct model passing:")
        print("   - client.customers.create(customer_model)")
        print("   - client.customers.update(id, customer_model)")
        print("   - client.debts.create(debt_model)")
        print("   - client.debts.update(id, debt_model)")
        print("   - client.debts.create_payment(debt_id, payment_model)")
        print("   - client.debts.update_payment(debt_id, payment_id, payment_model)")

        print("\n📈 Examples executed successfully:")
        print("   - Customer operations: ✅")
        print("   - Debt operations: ✅")
        print("   - Payment operations: ✅")
        print(f"   - Factory patterns: {len(factory_objects)} objects")
        print(f"   - Workflow example: {len(workflow_objects)} objects")
        print("   - Validation benefits: ✅")

        mode_text = "with API calls" if API_CALL else "in payload preview mode"
        print(f"\n🎉 All resources direct model usage examples completed {mode_text}!")

        print("\n💡 Key Benefits:")
        print("   ✅ No manual model-to-dict conversion needed")
        print("   ✅ Automatic validation before API calls")
        print("   ✅ Type safety and IDE support")
        print("   ✅ Consistent API across all resources")
        print("   ✅ Backwards compatible with dict data")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
