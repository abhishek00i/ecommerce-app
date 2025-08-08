from sqlalchemy.orm import Session
from . import models, schemas, auth

# =======================================
# User CRUD Functions
# =======================================

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a single user from the database by their email address.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database.
    The password from the schema is hashed before storing.
    """
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        client_id=user.client_id,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# =======================================
# Client CRUD Functions
# =======================================

def get_client(db: Session, client_id: int):
    """
    Retrieve a single client by their ID.
    """
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_client_by_name(db: Session, company_name: str):
    """
    Retrieve a single client by its company name.
    """
    return db.query(models.Client).filter(models.Client.company_name == company_name).first()

def create_client(db: Session, client: schemas.ClientCreate):
    """
    Create a new client.
    """
    db_client = models.Client(
        company_name=client.company_name,
        is_active=client.is_active
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# =======================================
# Carrier CRUD Functions (Re-added)
# =======================================

def get_carrier(db: Session, carrier_id: int):
    return db.query(models.Carrier).filter(models.Carrier.id == carrier_id).first()

def create_carrier(db: Session, carrier: schemas.CarrierCreate):
    db_carrier = models.Carrier(**carrier.model_dump())
    db.add(db_carrier)
    db.commit()
    db.refresh(db_carrier)
    return db_carrier

# =======================================
# Shipment CRUD Functions (Refactored)
# =======================================

def create_shipment(db: Session, shipment: schemas.ShipmentCreate, client_id: int):
    # Create addresses and associate them with the client
    sender_address_data = shipment.sender_address.model_dump()
    db_sender_address = models.Address(**sender_address_data, client_id=client_id)

    recipient_address_data = shipment.recipient_address.model_dump()
    db_recipient_address = models.Address(**recipient_address_data, client_id=client_id)

    db.add(db_sender_address)
    db.add(db_recipient_address)
    db.flush()

    # Create the shipment and associate it with the client
    shipment_data = shipment.model_dump(exclude={'sender_address', 'recipient_address'})
    db_shipment = models.Shipment(
        **shipment_data,
        sender_address_id=db_sender_address.id,
        recipient_address_id=db_recipient_address.id,
        client_id=client_id
    )

    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment

def get_shipments_by_client(db: Session, client_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Shipment)
        .filter(models.Shipment.client_id == client_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# =======================================
# Dashboard CRUD Functions
# =======================================
from sqlalchemy import func
from datetime import datetime, timedelta

def get_dashboard_kpis(db: Session, client_id: int):
    today = datetime.utcnow().date()

    shipments_in_transit = (
        db.query(models.Shipment)
        .filter(models.Shipment.client_id == client_id, models.Shipment.status == "In Transit")
        .count()
    )

    delivered_today = (
        db.query(models.Shipment)
        .filter(
            models.Shipment.client_id == client_id,
            models.Shipment.status == "Delivered",
            func.date(models.Shipment.updated_at) == today,
        )
        .count()
    )

    pending_pickups = (
        db.query(models.Shipment)
        .filter(models.Shipment.client_id == client_id, models.Shipment.status == "Booked")
        .count()
    )

    return {
        "shipments_in_transit": shipments_in_transit,
        "delivered_today": delivered_today,
        "pending_pickups": pending_pickups,
        "delayed_shipments": 0, # Placeholder, as 'delayed' logic is not yet defined
    }

def get_shipment_volume_last_30_days(db: Session, client_id: int):
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)

    result = (
        db.query(
            func.date(models.Shipment.created_at).label("date"),
            func.count(models.Shipment.id).label("count"),
        )
        .filter(
            models.Shipment.client_id == client_id,
            func.date(models.Shipment.created_at) > thirty_days_ago,
        )
        .group_by(func.date(models.Shipment.created_at))
        .order_by(func.date(models.Shipment.created_at))
        .all()
    )

    return [{"date": str(date), "count": count} for date, count in result]
