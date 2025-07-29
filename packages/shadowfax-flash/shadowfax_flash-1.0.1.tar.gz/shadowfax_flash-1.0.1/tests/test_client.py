"""
Tests for the ShadowfaxFlashClient class.
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock

from shadowfax_flash import Environment, ShadowfaxFlashClient
from shadowfax_flash.models import OrderStatus


class TestShadowfaxFlashClient:
    """Test cases for ShadowfaxFlashClient."""

    @pytest.mark.asyncio
    async def test_initialization(self, test_client):
        """Test client initialization with different parameters."""
        # Test with default environment (production)
        async with ShadowfaxFlashClient(api_key="test_key") as client:
            assert client.environment == Environment.PRODUCTION

        # Test with staging environment
        async with ShadowfaxFlashClient(
            api_key="test_key", environment=Environment.STAGING
        ) as client:
            assert client.environment == Environment.STAGING

    @pytest.mark.asyncio
    async def test_validate_credits_key_success(
        self, test_client, httpx_mock: HTTPXMock
    ):
        """Test successful credits key validation."""
        mock_response = {
            "is_valid": True,
            "message": "Valid Credits Key",
        }

        httpx_mock.add_response(
            method="POST",
            url="https://hlbackend3.staging.shadowfax.in/order/credits/key/validate/",
            json=mock_response,
        )

        result = await test_client.validate_credits_key(
            credits_key="test_credits_key", store_brand_id="test_brand_id"
        )

        assert result["is_valid"] is True
        assert "Valid Credits Key" in result["message"]
        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_check_serviceability(
        self, test_client, sample_location, sample_drop_location, httpx_mock: HTTPXMock
    ):
        """Test serviceability check."""
        mock_response = {
            "is_serviceable": True,
            "total_amount": 50,
            "message": "We are serviceable",
        }

        httpx_mock.add_response(
            method="POST",
            url="https://hlbackend3.staging.shadowfax.in/order/serviceability/",
            json=mock_response,
        )

        result = await test_client.check_serviceability(
            pickup_details=sample_location, drop_details=sample_drop_location
        )

        assert result["is_serviceable"] is True
        assert result["total_amount"] == 50
        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_create_order(
        self,
        test_client,
        sample_location,
        sample_drop_location,
        sample_order_details,
        sample_user_details,
        httpx_mock: HTTPXMock,
    ):
        """Test order creation."""
        mock_response = {
            "is_order_created": True,
            "message": "Order created successfully",
            "flash_order_id": "FLASH_123",
            "pickup_otp": 1234,
            "drop_otp": 5678,
            "total_amount": 50,
        }

        httpx_mock.add_response(
            method="POST",
            url="https://hlbackend3.staging.shadowfax.in/order/create/",
            json=mock_response,
        )

        result = await test_client.create_order(
            pickup_details=sample_location,
            drop_details=sample_drop_location,
            order_details=sample_order_details,
            user_details=sample_user_details,
        )

        assert result["is_order_created"] is True
        assert "Order created successfully" in result["message"]
        assert "flash_order_id" in result
        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_cancel_order_success(self, test_client, httpx_mock: HTTPXMock):
        """Test successful order cancellation."""
        mock_response = {
            "is_cancelled": True,
            "message": "Order cancelled successfully",
        }

        httpx_mock.add_response(
            method="POST",
            url="https://hlbackend3.staging.shadowfax.in/order/cancel/",
            json=mock_response,
        )

        result = await test_client.cancel_order(order_id="TEST_ORDER_123")

        assert result["is_cancelled"] is True
        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_track_order(self, test_client, httpx_mock: HTTPXMock):
        """Test order tracking."""
        mock_response = {
            "order_id": "TEST_ORDER_123",
            "status": "DELIVERED",
            "event_time": "2024-01-01T10:00:00Z",
        }

        httpx_mock.add_response(
            method="GET",
            url="https://hlbackend3.staging.shadowfax.in/order/track/TEST_ORDER_123/",
            json=mock_response,
        )

        result = await test_client.track_order(order_id="TEST_ORDER_123")

        assert result.order_id == "TEST_ORDER_123"
        assert result.status == OrderStatus.DELIVERED
        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_process_order_callback(self, test_client, sample_callback_data):
        """Test order callback processing."""
        callback = await test_client.process_order_callback(sample_callback_data)

        assert callback.coid == sample_callback_data["coid"]
        assert callback.status.value == sample_callback_data["status"]
        assert callback.rider_name == sample_callback_data["rider_name"]

    @pytest.mark.asyncio
    async def test_request_error_handling(self, test_client, httpx_mock: HTTPXMock):
        """Test error handling for API requests."""
        httpx_mock.add_exception(httpx.RequestError("Test error"))

        with pytest.raises(ValueError) as exc_info:
            await test_client.validate_credits_key(
                credits_key="test_key", store_brand_id="test_brand"
            )

        assert "Test error" in str(exc_info.value)
