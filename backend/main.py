from datetime import timedelta
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from . import auth, crud, models, schemas
from .database import SessionLocal, engine, get_db

def create_initial_data():
    db = SessionLocal()
    try:
        client = crud.get_client_by_name(db, company_name="DefaultCorp")
        if not client:
            print("Creating default client and user...")
            client_schema = schemas.ClientCreate(company_name="DefaultCorp")
            client = crud.create_client(db, client=client_schema)

            user_schema = schemas.UserCreate(
                email="test@test.com",
                password="password",
                full_name="Test User",
                client_id=client.id,
                role="admin"
            )
            crud.create_user(db, user=user_schema)
            print("Default data created.")
    finally:
        db.close()

app = FastAPI(
    title="RVCourier and Logistics pvt ltd API",
    description="The backend API for the Unified Logistics & Courier Management Panel.",
    version="0.1.0",
)

# Create tables and initial data on startup
models.Base.metadata.create_all(bind=engine)
create_initial_data()

# =======================================
# Authentication Endpoint
# =======================================

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Logs in a user and returns a JWT access token.

    Uses OAuth2PasswordRequestForm, so you should provide username and password
    in a form-data body.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# =======================================
# User and Client Management Endpoints
# =======================================

@app.post("/clients/", response_model=schemas.Client, tags=["Clients"])
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    """
    Create a new client company.
    """
    db_client = crud.get_client_by_name(db, company_name=client.company_name)
    if db_client:
        raise HTTPException(status_code=400, detail="Client with this company name already exists")
    return crud.create_client(db=db, client=client)

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user. The user must be associated with an existing client.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_client = crud.get_client(db, client_id=user.client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail=f"Client with id {user.client_id} not found")

    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User, tags=["Users"])
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Get the details of the currently authenticated user.
    """
    return current_user

# =======================================
# Carrier and Shipment Endpoints
# =======================================

@app.post("/carriers/", response_model=schemas.Carrier, tags=["Carriers"])
def create_carrier(
    carrier: schemas.CarrierCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # In a real app, you might restrict carrier creation to super-admins
    # For now, any authenticated user can create a carrier.
    return crud.create_carrier(db=db, carrier=carrier)

@app.post("/shipments/", response_model=schemas.Shipment, tags=["Shipments"])
def create_shipment(
    shipment: schemas.ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Create a new shipment for the authenticated user's client.
    """
    carrier = crud.get_carrier(db, carrier_id=shipment.carrier_id)
    if not carrier or not carrier.is_active:
        raise HTTPException(
            status_code=400,
            detail="Carrier not found or is not active."
        )

    return crud.create_shipment(db=db, shipment=shipment, client_id=current_user.client_id)

@app.get("/shipments/", response_model=List[schemas.Shipment], tags=["Shipments"])
def read_client_shipments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Retrieve all shipments for the authenticated user's client.
    """
    shipments = crud.get_shipments_by_client(
        db, client_id=current_user.client_id, skip=skip, limit=limit
    )
    return shipments

# =======================================
# Dashboard Endpoints
# =======================================

@app.get("/dashboard/kpis", response_model=schemas.DashboardKPIs, tags=["Dashboard"])
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Retrieve Key Performance Indicators (KPIs) for the client's dashboard.
    """
    kpis = crud.get_dashboard_kpis(db, client_id=current_user.client_id)
    return kpis

@app.get("/dashboard/shipment-volume", response_model=List[schemas.ShipmentVolumeDataPoint], tags=["Dashboard"])
def get_shipment_volume(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Retrieve shipment volume data for the last 30 days for the client's dashboard.
    """
    volume_data = crud.get_shipment_volume_last_30_days(db, client_id=current_user.client_id)
    return volume_data

# The root endpoint can be useful for a simple health check.
@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "ok"}
