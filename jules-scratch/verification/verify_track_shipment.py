import httpx
from playwright.sync_api import sync_playwright, expect
import time

def create_shipment_via_api(headers, carrier_id):
    """Helper function to create a shipment."""
    shipment_payload = {
        "package_length": 1, "package_width": 1, "package_height": 1, "package_weight": 1,
        "contents": "Test Tracking Shipment", "invoice_value": 100, "carrier_id": carrier_id,
        "sender_address": {"contact_name": "A", "contact_phone": "1", "address_line_1": "1", "city": "A", "state": "A", "pincode": "1"},
        "recipient_address": {"contact_name": "B", "contact_phone": "2", "address_line_1": "2", "city": "B", "state": "B", "pincode": "2"}
    }
    r = httpx.post("http://localhost:8000/shipments/", json=shipment_payload, headers=headers, timeout=20)
    assert r.status_code == 200, f"Failed to create shipment: {r.text}"
    return r.json()

def add_delivery_update_via_api(headers, shipment_id, status, location):
    """Helper function to add a tracking update."""
    delivery_payload = {"status": status, "location": location}
    r = httpx.post(f"http://localhost:8000/shipments/{shipment_id}/deliveries", json=delivery_payload, headers=headers, timeout=20)
    assert r.status_code == 200, f"Failed to add delivery update: {r.text}"

def run_verification():
    BASE_API_URL = "http://localhost:8000"

    # --- Setup: Log in and create test data ---
    print("Logging in and creating test data...")
    login_payload = {"username": "test@test.com", "password": "password"}
    r = httpx.post(f"{BASE_API_URL}/token", data=login_payload, timeout=20)
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    carrier_payload = {"name": "TrackTestCarrier", "is_active": True}
    r = httpx.post(f"{BASE_API_URL}/carriers/", json=carrier_payload, headers=headers, timeout=20)
    assert r.status_code == 200, f"Carrier creation failed: {r.text}"
    carrier_id = r.json()["id"]

    shipment = create_shipment_via_api(headers, carrier_id)
    shipment_id = shipment["id"]
    awb_number = shipment["awb_number"]
    assert awb_number is not None, "AWB number was not generated."

    add_delivery_update_via_api(headers, shipment_id, "In Transit", "Mumbai Hub")
    add_delivery_update_via_api(headers, shipment_id, "Out for Delivery", "Delhi Hub")
    print(f"Test data created. AWB: {awb_number}")

    # --- Playwright Test ---
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:5173/login", timeout=30000)
            page.evaluate(f"localStorage.setItem('authToken', '{token}')")

            print("Navigating to Track Shipments page...")
            page.goto("http://localhost:5173/track-shipments", timeout=30000)

            expect(page.get_by_role("heading", name="Track Your Shipment")).to_be_visible()

            # Search for the shipment
            print(f"Searching for AWB: {awb_number}")
            page.get_by_placeholder("e.g., 123456789").fill(awb_number)
            page.get_by_role("button", name="Track").click()

            # Assert that the tracking history is displayed
            print("Verifying tracking history...")
            expect(page.get_by_text("Out for Delivery")).to_be_visible(timeout=10000)
            expect(page.get_by_text("Mumbai Hub")).to_be_visible()

            print("Taking screenshot...")
            page.screenshot(path="jules-scratch/verification/track_shipment_verification.png")
            print("Successfully took screenshot.")

        except Exception as e:
            print(f"An error occurred during Playwright verification: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
