"""
Tests for the Pydantic models.
"""

from datetime import datetime

import pytest

from shadowfax_flash.models import (
    CancelledBy,
    CancelReason,
    Communications,
    DropLocationDetails,
    LocationDetails,
    OrderCallbackRequest,
    OrderDetails,
    OrderStatus,
    OrderTrackResponse,
    UserDetails,
    Validations,
)


class TestLocationModels:
    """Test cases for location-related models."""

    def test_location_details_validation(self):
        """Test LocationDetails model validation."""
        # Valid location
        location = LocationDetails(
            name="Test Location",
            contact_number="9876543210",
            address="123 Test St",
            latitude=12.9716,
            longitude=77.5946,
        )
        assert location.name == "Test Location"

        # Test invalid phone number
        with pytest.raises(ValueError):
            LocationDetails(
                name="Test",
                contact_number="12345",  # Invalid phone number
                address="Test",
            )

    def test_drop_location_details_validation(self):
        """Test DropLocationDetails model validation."""
        # Valid drop location
        drop_location = DropLocationDetails(
            name="Test Drop",
            contact_number="9876543210,1234",  # Masked number with PIN
            is_contact_number_masked=True,
            address="456 Test Ave",
        )
        assert drop_location.is_contact_number_masked is True

        # Test invalid masked number format
        with pytest.raises(ValueError):
            DropLocationDetails(
                name="Test",
                contact_number="9876543210",  # Missing PIN for masked number
                is_contact_number_masked=True,
                address="Test",
            )


class TestOrderModels:
    """Test cases for order-related models."""

    def test_order_details_validation(self):
        """Test OrderDetails model validation."""
        # Valid prepaid order
        order = OrderDetails(
            order_id="ORDER123", is_prepaid=True, cash_to_be_collected=0.0
        )
        assert order.is_prepaid is True

        # Valid COD order
        order = OrderDetails(
            order_id="ORDER124", is_prepaid=False, cash_to_be_collected=100.0
        )
        assert order.cash_to_be_collected == 100.0

        # Test missing required fields
        with pytest.raises(ValueError):
            OrderDetails(
                # Missing required fields
            )


class TestUserModels:
    """Test cases for user-related models."""

    def test_user_details_validation(self):
        """Test UserDetails model validation."""
        # Valid user details
        user = UserDetails(contact_number="9876543210", credits_key="test_credits_key")
        assert user.contact_number == "9876543210"

        # Test invalid phone number
        with pytest.raises(ValueError):
            UserDetails(
                contact_number="12345", credits_key="test_key"  # Invalid phone number
            )


class TestValidationModels:
    """Test cases for validation models."""

    def test_validations_model(self):
        """Test Validations model."""
        validations = Validations(
            pickup={"is_otp_required": True, "otp": "1234"},
            drop={"is_otp_required": False},
            rts={"is_otp_required": True},
        )
        assert validations.pickup["is_otp_required"] is True
        assert validations.drop["is_otp_required"] is False

    def test_communications_model(self):
        """Test Communications model."""
        comms = Communications(
            send_sms_to_pickup_person=True,
            send_sms_to_drop_person=False,
            send_rts_sms_to_pickup_person=True,
        )
        assert comms.send_sms_to_pickup_person is True
        assert comms.send_sms_to_drop_person is False


class TestCallbackModels:
    """Test cases for callback-related models."""

    def test_order_callback_request(self):
        """Test OrderCallbackRequest model."""
        callback_data = {
            "coid": "ORDER123",
            "status": "DELIVERED",
            "action_time": "2024-01-01T10:00:00Z",
            "rider_id": 1234,
            "rider_name": "Test Rider",
        }

        callback = OrderCallbackRequest(**callback_data)
        assert callback.coid == "ORDER123"
        assert callback.status == OrderStatus.DELIVERED
        assert callback.rider_id == 1234

    def test_order_track_response(self):
        """Test OrderTrackResponse model."""
        track_data = {
            "order_id": "ORDER123",
            "status": "DELIVERED",
            "event_time": "2024-01-01T10:00:00Z",
            "rider_name": "Test Rider",
        }

        track = OrderTrackResponse(**track_data)
        assert track.order_id == "ORDER123"
        assert track.status == OrderStatus.DELIVERED
        assert track.rider_name == "Test Rider"


class TestEnums:
    """Test cases for enum types."""

    def test_order_status_enum(self):
        """Test OrderStatus enum values."""
        assert OrderStatus.DELIVERED == "DELIVERED"
        assert OrderStatus.CANCELLED == "CANCELLED"

    def test_cancel_reason_enum(self):
        """Test CancelReason enum values."""
        assert CancelReason.CUSTOMER_CANCELLED == "Cancelled by Customer"
        assert CancelReason.ITEM_NOT_AVAILABLE == "Item not available"

    def test_cancelled_by_enum(self):
        """Test CancelledBy enum values."""
        assert CancelledBy.SFX == "sfx"
        assert CancelledBy.CLIENT == "client"
