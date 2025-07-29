# Shadowfax Flash Integration API Client

An async Python client for the Shadowfax Flash Integration API, providing a simple and type-safe way to interact with Shadowfax's delivery services.

## Features

- Full support for all Shadowfax Flash API endpoints
- Async/await support using aiohttp
- Type hints and data validation using Pydantic
- Support for both production and staging environments
- Comprehensive error handling

## Installation

```bash
pip install shadowfax-flash
```

## Usage

### Basic Setup

```python
import asyncio
from shadowfax_flash import ShadowfaxFlashClient, Environment
from shadowfax_flash.models import LocationDetails, DropLocationDetails, OrderDetails, UserDetails

async def main():
    # Initialize the client
    async with ShadowfaxFlashClient(
        api_key="your_api_key_here",
        environment=Environment.PRODUCTION  # or Environment.STAGING
    ) as client:
        # Example: Validate credits key
        validation = await client.validate_credits_key(
            credits_key="your_credits_key",
            store_brand_id="your_store_brand_id"
        )
        print("Credits validation:", validation)

        # Example: Check serviceability
        serviceability = await client.check_serviceability(
            pickup_details={
                "address": "123 Main St, Bangalore, Karnataka 560001",
                "latitude": 12.9716,
                "longitude": 77.5946
            },
            drop_details={
                "address": "456 MG Road, Bangalore, Karnataka 560001",
                "latitude": 12.9758,
                "longitude": 77.6050
            }
        )
        print("Serviceability:", serviceability)

        # Example: Create an order
        order_response = await client.create_order(
            pickup_details=LocationDetails(
                name="John Doe",
                contact_number="9876543210",
                address="123 Main St, Bangalore, Karnataka 560001",
                latitude=12.9716,
                longitude=77.5946
            ),
            drop_details=DropLocationDetails(
                name="Jane Smith",
                contact_number="9876543211",
                address="456 MG Road, Bangalore, Karnataka 560001",
                latitude=12.9758,
                longitude=77.6050
            ),
            order_details=OrderDetails(
                order_id="ORDER123",
                is_prepaid=False,
                cash_to_be_collected=150.0
            ),
            user_details=UserDetails(
                contact_number="9876543210",
                credits_key="your_credits_key"
            )
        )
        print("Order created:", order_response)

        # Example: Track an order
        tracking = await client.track_order(order_id="ORDER123")
        print("Order status:", tracking.status)

        # Example: Cancel an order
        cancel_response = await client.cancel_order(order_id="ORDER123")
        print("Cancel response:", cancel_response)

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
```

### Handling Webhook Callbacks

```python
from fastapi import FastAPI, Request
from shadowfax_flash.models import OrderCallbackRequest

app = FastAPI()

@app.post("/webhook/order-status")
async def handle_webhook(request: Request):
    # Parse the incoming webhook data
    data = await request.json()
    
    # Process the callback
    try:
        callback = OrderCallbackRequest(**data)
        print(f"Order {callback.coid} status changed to {callback.status}")
        
        # Handle different statuses
        if callback.status == "DELIVERED":
            print(f"Order {callback.coid} has been delivered!")
        elif callback.status == "CANCELLED":
            print(f"Order {callback.coid} was cancelled. Reason: {callback.cancel_reason}")
        
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}
```

## Available Methods

- `validate_credits_key(credits_key: str, store_brand_id: str)`: Validate a credits key
- `check_serviceability(pickup_details, drop_details)`: Check if a location is serviceable
- `create_order(pickup_details, drop_details, order_details, user_details, validations=None, communications=None)`: Create a new order
- `cancel_order(order_id: str)`: Cancel an existing order
- `track_order(order_id: str)`: Track the status of an order
- `process_order_callback(callback_data)`: Process an order status callback

## Models

The package includes Pydantic models for all request and response types, providing type hints and validation:

- `LocationDetails`: Pickup location details
- `DropLocationDetails`: Drop location details (extends LocationDetails)
- `ServiceabilityLocation`: Location for serviceability check
- `UserDetails`: User information
- `OrderDetails`: Order information
- `Validations`: Validation settings
- `Communications`: Communication preferences
- `OrderStatus`: Enum of possible order statuses
- `OrderCallbackRequest`: Model for webhook callbacks
- `OrderTrackResponse`: Model for order tracking responses

## Error Handling

The client raises appropriate exceptions for different types of errors:

- `aiohttp.ClientError`: For network-related errors
- `ValueError`: For API errors (e.g., validation errors, invalid requests)
- `pydantic.ValidationError`: For input validation errors

## Testing

To run the tests, you'll need to install the development dependencies:

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT

## Author

Goutham Soratoor (grsoratoor@gmail.com)

## Deployment

To deploy a new version to PyPI:

1. Update the version in `pyproject.toml` following [Semantic Versioning](https://semver.org/)
2. Run the deployment script:

```bash
# Using Python script (recommended)
python scripts/deploy.py

# Or using bash script
./scripts/deploy.sh
```

The script will:
1. Clean up previous builds
2. Install build dependencies
3. Build the package
4. Verify the package
5. Prompt for confirmation before uploading to PyPI

### Prerequisites

- Python 3.11+
- `build` and `twine` packages (will be installed automatically)
- PyPI account with access to upload the package
- Configured `~/.pypirc` with your PyPI credentials or use environment variables:
  ```bash
  export TWINE_USERNAME=your_username
  export TWINE_PASSWORD=your_password
  ```

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) for more information.

## Support

For support, please contact [Shadowfax Support](mailto:gaurav.dakliya@shadowfax.in)
