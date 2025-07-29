"""
Async client for Shadowfax Flash Integration API.
"""

import logging
from enum import Enum
from typing import Any, Dict, Optional, Union

import httpx
from pydantic import TypeAdapter

from .models import (
    Communications,
    DropLocationDetails,
    LocationDetails,
    OrderCallbackRequest,
    OrderDetails,
    OrderTrackResponse,
    ServiceabilityLocation,
    UserDetails,
    Validations,
)

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Available API environments."""

    PRODUCTION = "production"
    STAGING = "staging"
    STAGING1 = "staging1"


class ShadowfaxFlashClient:
    """Async client for Shadowfax Flash Integration API."""

    BASE_URLS = {
        Environment.PRODUCTION: "https://flash-api.shadowfax.in",
        Environment.STAGING: "https://hlbackend.staging.shadowfax.in",
        Environment.STAGING1: "https://hlbackend2.staging.shadowfax.in",
    }

    def __init__(
        self,
        api_key: str,
        environment: Environment = Environment.PRODUCTION,
        client: Optional[httpx.AsyncClient] = None,
    ):
        """Initialize the Shadowfax Flash client.

        Args:
            api_key: Your Shadowfax API key
            environment: API environment (production or staging)
            client: Optional httpx.AsyncClient
        """
        self.api_key = api_key
        self.environment = environment
        self.base_url = self.BASE_URLS[environment]
        self._client = client or httpx.AsyncClient()
        self._headers = {
            "Authorization": f"{self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (get, post, etc.)
            endpoint: API endpoint

        Returns:
            Response data as a dictionary

        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the response contains an error
        """
        url = f"{self.base_url}{endpoint}"
        headers = {**self._headers, **kwargs.pop("headers", {})}

        response = await self._client.request(
            method=method, url=url, headers=headers, **kwargs
        )
        response.raise_for_status()
        return response.json()


    async def validate_credits_key(
        self, credits_key: str, store_brand_id: str
    ) -> Dict[str, Any]:
        """Validate the credits key.

        Args:
            credits_key: The credits key to validate
            store_brand_id: The store brand ID

        Returns:
            Validation result
        """
        payload = {"credits_key": credits_key, "store_brand_id": store_brand_id}

        return await self._request("POST", "/order/credits/key/validate/", json=payload)

    async def check_serviceability(
        self,
        pickup_details: Union[ServiceabilityLocation, Dict],
        drop_details: Union[ServiceabilityLocation, Dict],
    ) -> Dict[str, Any]:
        """Check if a location is serviceable and get delivery charges.

        Args:
            pickup_details: Pickup location details
            drop_details: Drop location details

        Returns:
            Serviceability information
        """
        if not isinstance(pickup_details, dict):
            pickup_details = pickup_details.model_dump(exclude_none=True)
        if not isinstance(drop_details, dict):
            drop_details = drop_details.model_dump(exclude_none=True)

        payload = {"pickup_details": pickup_details, "drop_details": drop_details}

        return await self._request("POST", "/order/serviceability/", json=payload)

    async def create_order(
        self,
        pickup_details: Union[LocationDetails, Dict],
        drop_details: Union[DropLocationDetails, Dict],
        order_details: Union[OrderDetails, Dict],
        user_details: Union[UserDetails, Dict],
        validations: Optional[Union[Validations, Dict]] = None,
        communications: Optional[Union[Communications, Dict]] = None,
    ) -> Dict[str, Any]:
        """Create a new order.

        Args:
            pickup_details: Pickup location details
            drop_details: Drop location details
            order_details: Order details
            user_details: User details
            validations: Optional validation settings
            communications: Optional communication settings

        Returns:
            Order creation response
        """
        # Convert Pydantic models to dict if needed
        if not isinstance(pickup_details, dict):
            pickup_details = pickup_details.model_dump(exclude_none=True)
        if not isinstance(drop_details, dict):
            drop_details = drop_details.model_dump(exclude_none=True)
        if not isinstance(order_details, dict):
            order_details = order_details.model_dump(exclude_none=True)
        if not isinstance(user_details, dict):
            user_details = user_details.model_dump(exclude_none=True)

        payload = {
            "pickup": pickup_details,
            "drop": drop_details,
            "order_details": order_details,
            "user_details": user_details,
        }

        # Add optional fields if provided
        if validations is not None:
            payload["validations"] = (
                validations.model_dump(exclude_none=True)
                if not isinstance(validations, dict)
                else validations
            )

        if communications is not None:
            payload["communications"] = (
                communications.model_dump(exclude_none=True)
                if not isinstance(communications, dict)
                else communications
            )

        return await self._request("POST", "/order/create/", json=payload)

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order.

        Args:
            order_id: The ID of the order to cancel

        Returns:
            Cancellation response
        """
        payload = {"order_id": order_id}

        return await self._request("POST", "/order/cancel/", json=payload)

    async def track_order(self, order_id: str) -> OrderTrackResponse:
        """Track the status of an order.

        Args:
            order_id: The ID of the order to track

        Returns:
            Order tracking information
        """
        response = await self._request("GET", f"/order/track/{order_id}/")

        # Convert response to Pydantic model
        return OrderTrackResponse(**response)

    async def process_order_callback(
        self, callback_data: Union[Dict[str, Any], OrderCallbackRequest]
    ) -> OrderCallbackRequest:
        """Process an order status callback.

        Args:
            callback_data: The callback data received from the webhook

        Returns:
            Parsed callback data
        """
        if not isinstance(callback_data, OrderCallbackRequest):
            callback_data = OrderCallbackRequest(**callback_data)

        # Here you can add your custom logic to handle the callback
        # For example, update your database, send notifications, etc.

        return callback_data
