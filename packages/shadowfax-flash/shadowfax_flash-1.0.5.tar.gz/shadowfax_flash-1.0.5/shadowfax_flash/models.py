"""
Data models for Shadowfax Flash Integration API.
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderStatus(str, Enum):
    """Enum representing order statuses."""

    CREATED = "CREATED"
    ALLOTTED = "ALLOTTED"
    ACCEPTED = "ACCEPTED"
    ARRIVED = "ARRIVED"
    COLLECTED = "COLLECTED"
    CUSTOMER_DOOR_STEP = "CUSTOMER_DOOR_STEP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RTS_INITIATED = "RTS_INITIATED"
    RTS_COMPLETED = "RTS_COMPLETED"


class CancelledBy(str, Enum):
    """Enum representing who cancelled the order."""

    SFX = "sfx"
    CLIENT = "client"


class CancelReason(str, Enum):
    """Enum representing cancellation reasons."""

    EMPTY = ""
    CUSTOMER_CANCELLED = "Cancelled by Customer"
    RIDER_NOT_AVAILABLE = "Rider Not Available or is Late"
    CUSTOMER_NOT_AVAILABLE = "Customer Not Available"
    DUPLICATE_ORDER = "Duplicate Order"
    ADDRESS_UNSERVICEABLE = "Delivery Address Unserviceable or Incorrect"
    OPERATIONAL_ISSUE = "Operational Issue with order"
    SELLER_CANCELLED = "Cancelled by Seller"
    INSUFFICIENT_CASH = "Rider not having enough cash for purchase"
    DELIVERED_BY_SELLER = "Delivered by seller"
    ITEM_NOT_AVAILABLE = "Item not available"
    INCORRECT_SELLER_LOCATION = "Incorrect seller location"
    CUSTOMER_NOT_RESPONDING = "Customer Not responding / Phone switched off"
    MISTAKE = "Placed order by mistake"
    ITEM_NOT_READY = "Order item is not ready"
    FASTER_OPTION_AVAILABLE = "Got faster option from other provider"
    SHORTER_WAIT_TIME = "Expected a shorter wait time"
    PARTNER_REFUSED = "Delivery partner refused pickup"


class BaseLocation(BaseModel):
    """Base location model with common fields."""

    name: Optional[str] = None
    contact_number: str = Field(..., pattern=r"^[6-9]{1}[0-9]{9}$")
    address: str
    landmark: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationDetails(BaseLocation):
    """Model for pickup location details."""

    pass


class DropLocationDetails(BaseLocation):
    """Model for drop location details with additional fields."""

    is_contact_number_masked: bool = False
    contact_number: str = Field(..., pattern=r"^[6-9]{1}[0-9]{9}(,\d+)?$")

    @model_validator(mode="after")
    def validate_masked_number(self):
        if self.is_contact_number_masked and "," not in self.contact_number:
            raise ValueError("For masked numbers, use format: <masked_number,pin>")
        return self


class ServiceabilityLocation(BaseModel):
    """Model for serviceability check location."""

    address: str
    building_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserDetails(BaseModel):
    """Model for user details."""

    contact_number: str = Field(..., pattern=r"^[6-9]{1}[0-9]{9}$")
    credits_key: str


class OrderDetails(BaseModel):
    """Model for order details."""

    order_id: str
    is_prepaid: bool
    cash_to_be_collected: float = 0.0
    delivery_charge_to_be_collected_from_customer: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "123456",
                "is_prepaid": False,
                "cash_to_be_collected": 120.0,
                "delivery_charge_to_be_collected_from_customer": False,
            }
        }
    )


class Validations(BaseModel):
    """Model for order validations."""

    pickup: Optional[Dict[str, Any]] = None
    drop: Optional[Dict[str, Any]] = None
    rts: Optional[Dict[str, Any]] = None


class Communications(BaseModel):
    """Model for communication preferences."""

    send_sms_to_pickup_person: bool = True
    send_sms_to_drop_person: bool = True
    send_rts_sms_to_pickup_person: bool = True


class OrderCallbackRequest(BaseModel):
    """Model for order callback request."""

    coid: str
    status: OrderStatus
    action_time: str
    rider_id: Optional[int] = None
    rider_contact_number: Optional[str] = None
    rider_latitude: Optional[float] = None
    rider_longitude: Optional[float] = None
    rider_name: Optional[str] = None
    rts_reason: Optional[str] = None
    cancelled_by: Optional[CancelledBy] = None
    cancel_reason: Optional[CancelReason] = None


class OrderTrackResponse(BaseModel):
    """Model for order tracking response."""

    order_id: str
    status: OrderStatus
    sfx_order_id: Optional[str] = None
    event_time: Optional[str] = None
    rider_contact_number: Optional[str] = None
    rider_latitude: Optional[float] = None
    rider_longitude: Optional[float] = None
    rider_id: Optional[int] = None
    rider_name: Optional[str] = None
    rts_reason: Optional[str] = None
    tracking_url: Optional[str] = None
    cancelled_by: Optional[CancelledBy] = None
    cancel_reason: Optional[CancelReason] = None
