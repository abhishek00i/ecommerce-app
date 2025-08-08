from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# =======================================
# User and Client Management
# =======================================

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="client")
    addresses = relationship("Address", back_populates="client")
    shipments = relationship("Shipment", back_populates="client")
    manifests = relationship("Manifest", back_populates="client")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)

    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="users")

    # Simple role management for now, e.g., 'admin', 'operator'
    role = Column(String, default="operator")


# =======================================
# Core Logistics Models
# =======================================

class Carrier(Base):
    __tablename__ = "carriers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="addresses")

    contact_name = Column(String)
    contact_phone = Column(String)
    address_line_1 = Column(String)
    address_line_2 = Column(String, nullable=True)
    city = Column(String)
    state = Column(String)
    pincode = Column(String)
    country = Column(String, default="India")


# Association Table for Manifests and Shipments (Many-to-Many)
manifest_shipment_association = Table(
    "manifest_shipment_association",
    Base.metadata,
    Column("manifest_id", Integer, ForeignKey("manifests.id"), primary_key=True),
    Column("shipment_id", Integer, ForeignKey("shipments.id"), primary_key=True),
)

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="shipments")

    awb_number = Column(String, unique=True, index=True, nullable=True)

    sender_address_id = Column(Integer, ForeignKey("addresses.id"))
    recipient_address_id = Column(Integer, ForeignKey("addresses.id"))
    sender_address = relationship("Address", foreign_keys=[sender_address_id])
    recipient_address = relationship("Address", foreign_keys=[recipient_address_id])

    carrier_id = Column(Integer, ForeignKey("carriers.id"))
    carrier = relationship("Carrier")

    package_length = Column(Float)
    package_width = Column(Float)
    package_height = Column(Float)
    package_weight = Column(Float)

    contents = Column(String)
    invoice_value = Column(Float)

    status = Column(String, index=True, default="Booked")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    deliveries = relationship("Delivery", back_populates="shipment")
    manifests = relationship(
        "Manifest",
        secondary=manifest_shipment_association,
        back_populates="shipments"
    )

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"))
    shipment = relationship("Shipment", back_populates="deliveries")

    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, index=True)
    location = Column(String, nullable=True)
    remarks = Column(String, nullable=True)


class Manifest(Base):
    __tablename__ = "manifests"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="manifests")

    manifest_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shipments = relationship(
        "Shipment",
        secondary=manifest_shipment_association,
        back_populates="manifests"
    )
