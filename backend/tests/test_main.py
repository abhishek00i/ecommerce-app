import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from backend.main import app, get_db
from backend.database import Base

# =======================================
# Test Database Setup
# =======================================
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# =======================================
# Dependency Override & Test Client
# =======================================
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# =======================================
# Test Fixture for Clean State
# =======================================
@pytest.fixture(autouse=True)
def cleanup_database():
    """Ensure each test starts with a fresh, empty database."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

# =======================================
# Test Cases
# =======================================

def test_create_client_and_user():
    """Test creating a client and then a user for that client."""
    # Create a client
    client_res = client.post("/clients/", json={"company_name": "TestCorp", "is_active": True})
    assert client_res.status_code == 200
    client_data = client_res.json()
    assert client_data["company_name"] == "TestCorp"
    client_id = client_data["id"]

    # Create a user for the client
    user_res = client.post(
        "/users/",
        json={
            "email": "test@testcorp.com",
            "password": "password123",
            "full_name": "Test User",
            "client_id": client_id,
            "role": "admin",
        },
    )
    assert user_res.status_code == 200
    user_data = user_res.json()
    assert user_data["email"] == "test@testcorp.com"
    assert "password" not in user_data  # Ensure password is not returned

def test_login_and_get_me():
    """Test user login and fetching user details with the token."""
    # Step 1: Create client and user
    client_res = client.post("/clients/", json={"company_name": "LoginCorp", "is_active": True})
    client_id = client_res.json()["id"]
    client.post(
        "/users/",
        json={
            "email": "login@logincorp.com", "password": "a_secure_password",
            "full_name": "Login User", "client_id": client_id, "role": "operator",
        },
    )

    # Step 2: Log in to get token
    login_res = client.post(
        "/token", data={"username": "login@logincorp.com", "password": "a_secure_password"}
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Step 3: Use token to access protected route /users/me/
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/users/me/", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "login@logincorp.com"

def test_shipment_data_isolation():
    """
    The most critical test: Ensure one client cannot see or interfere with another's data.
    """
    # Create Client A and User A
    client_a_res = client.post("/clients/", json={"company_name": "ClientA", "is_active": True})
    client_a_id = client_a_res.json()["id"]
    client.post("/users/", json={"email": "user_a@clienta.com", "password": "pass_a", "client_id": client_a_id})

    # Create Client B and User B
    client_b_res = client.post("/clients/", json={"company_name": "ClientB", "is_active": True})
    client_b_id = client_b_res.json()["id"]
    client.post("/users/", json={"email": "user_b@clientb.com", "password": "pass_b", "client_id": client_b_id})

    # Log in as User A
    login_a_res = client.post("/token", data={"username": "user_a@clienta.com", "password": "pass_a"})
    token_a = login_a_res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Log in as User B
    login_b_res = client.post("/token", data={"username": "user_b@clientb.com", "password": "pass_b"})
    token_b = login_b_res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a carrier and a shipment
    carrier_res = client.post("/carriers/", json={"name": "TestCarrier"}, headers=headers_a)
    carrier_id = carrier_res.json()["id"]
    shipment_payload_a = {
        "package_length": 1, "package_width": 1, "package_height": 1, "package_weight": 1,
        "contents": "Shipment A", "invoice_value": 100, "carrier_id": carrier_id,
        "sender_address": {"contact_name": "A", "contact_phone": "1", "address_line_1": "1", "city": "A", "state": "A", "pincode": "1"},
        "recipient_address": {"contact_name": "A", "contact_phone": "1", "address_line_1": "1", "city": "A", "state": "A", "pincode": "1"}
    }
    client.post("/shipments/", json=shipment_payload_a, headers=headers_a)

    # User A should see 1 shipment
    shipments_a_res = client.get("/shipments/", headers=headers_a)
    assert shipments_a_res.status_code == 200
    assert len(shipments_a_res.json()) == 1
    assert shipments_a_res.json()[0]["contents"] == "Shipment A"

    # User B should see 0 shipments
    shipments_b_res = client.get("/shipments/", headers=headers_b)
    assert shipments_b_res.status_code == 200
    assert len(shipments_b_res.json()) == 0

    # User B creates a shipment
    shipment_payload_b = {
        "package_length": 2, "package_width": 2, "package_height": 2, "package_weight": 2,
        "contents": "Shipment B", "invoice_value": 200, "carrier_id": carrier_id,
        "sender_address": {"contact_name": "B", "contact_phone": "2", "address_line_1": "2", "city": "B", "state": "B", "pincode": "2"},
        "recipient_address": {"contact_name": "B", "contact_phone": "2", "address_line_1": "2", "city": "B", "state": "B", "pincode": "2"}
    }
    client.post("/shipments/", json=shipment_payload_b, headers=headers_b)

    # User B should now see 1 shipment
    shipments_b_res_2 = client.get("/shipments/", headers=headers_b)
    assert shipments_b_res_2.status_code == 200
    assert len(shipments_b_res_2.json()) == 1
    assert shipments_b_res_2.json()[0]["contents"] == "Shipment B"

    # User A should still only see their 1 shipment
    shipments_a_res_2 = client.get("/shipments/", headers=headers_a)
    assert shipments_a_res_2.status_code == 200
    assert len(shipments_a_res_2.json()) == 1
    assert shipments_a_res_2.json()[0]["contents"] == "Shipment A"
