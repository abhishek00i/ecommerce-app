from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# =======================================
# Token Schemas
# =======================================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# =======================================
# User Schemas
# =======================================
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    client_id: int
    role: str = "operator"

class UserInDB(UserBase):
    id: int
    is_active: bool
    client_id: int
    role: str

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        from_attributes = True

# =======================================
# Client Schemas
# =======================================
class ClientBase(BaseModel):
    company_name: str
    is_active: bool = True

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# =======================================
# Address Schemas (Refactored)
# =======================================
class AddressBase(BaseModel):
    contact_name: str
    contact_phone: str
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int
    client_id: int

    class Config:
        from_attributes = True

# =======================================
# Dashboard Schemas
# =======================================
class DashboardKPIs(BaseModel):
    shipments_in_transit: int
    delivered_today: int
    pending_pickups: int
    delayed_shipments: int

class ShipmentVolumeDataPoint(BaseModel):
    date: str
    count: int

# =======================================
# Delivery (Tracking History) Schemas
# =======================================
class DeliveryBase(BaseModel):
    status: str
    location: Optional[str] = None
    remarks: Optional[str] = None

class DeliveryCreate(DeliveryBase):
    pass

class Delivery(DeliveryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# =======================================
# Carrier Schemas (Refactored)
# =======================================
class CarrierBase(BaseModel):
    name: str
    is_active: bool = True

class CarrierCreate(CarrierBase):
    pass

class Carrier(CarrierBase):
    id: int

    class Config:
        from_attributes = True

# =======================================
# Shipment Schemas (Refactored)
# =======================================
class ShipmentBase(BaseModel):
    package_length: float
    package_width: float
    package_height: float
    package_weight: float
    contents: str
    invoice_value: float

class ShipmentCreate(ShipmentBase):
    sender_address: AddressCreate
    recipient_address: AddressCreate
    carrier_id: int

class Shipment(ShipmentBase):
    id: int
    awb_number: Optional[str] = None
    status: str
    created_at: datetime
    client_id: int

    sender_address: Address
    recipient_address: Address
    carrier: Carrier
    deliveries: List[Delivery] = []

    class Config:
        from_attributes = True
