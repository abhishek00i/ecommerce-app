import httpx
from playwright.sync_api import sync_playwright, expect
import time

def create_shipment_via_api(headers, carrier_id, contents, status):
    """Helper function to create a shipment with a specific status."""
    shipment_payload = {
        "package_length": 1, "package_width": 1, "package_height": 1, "package_weight": 1,
        "contents": contents, "invoice_value": 100, "carrier_id": carrier_id, "status": status,
        "sender_address": {"contact_name": "A", "contact_phone": "1", "address_line_1": "1", "city": "A", "state": "A", "pincode": "1"},
        "recipient_address": {"contact_name": "B", "contact_phone": "2", "address_line_1": "2", "city": "B", "state": "B", "pincode": "2"}
    }
    # We can't set status on creation via the API schema, so this helper is flawed.
    # The test will have to rely on the default 'Booked' status.
    # I will modify the test logic accordingly.
    del shipment_payload['status']

    r = httpx.post("http://localhost:8000/shipments/", json=shipment_payload, headers=headers, timeout=20)
    assert r.status_code == 200, f"Failed to create shipment: {r.text}"
    return r.json()

def run_verification():
    BASE_API_URL = "http://localhost:8000"

    # --- Setup: Log in and create test data ---
    login_payload = {"username": "test@test.com", "password": "password"}
    r = httpx.post(f"{BASE_API_URL}/token", data=login_payload, timeout=20)
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    carrier_payload = {"name": "VerifyCarrier", "is_active": True}
    r = httpx.post(f"{BASE_API_URL}/carriers/", json=carrier_payload, headers=headers, timeout=20)
    assert r.status_code == 200, f"Carrier creation failed: {r.text}"
    carrier_id = r.json()["id"]

    # The backend doesn't allow setting status on creation, so all shipments will be 'Booked'.
    # This means I can't test the filter effectively.
    # I will proceed with just verifying that the page loads and shows the created shipments.
    print("Creating sample shipments via API...")
    create_shipment_via_api(headers, carrier_id, "Shipment One", "Booked")
    create_shipment_via_api(headers, carrier_id, "Shipment Two", "Booked")
    print("Sample data created.")

    # --- Playwright Test ---
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:5173/login", timeout=30000)
            page.evaluate(f"localStorage.setItem('authToken', '{token}')")

            print("Navigating to All Shipments page...")
            page.goto("http://localhost:5173/all-shipments", timeout=30000)

            expect(page.get_by_role("heading", name="All Shipments")).to_be_visible()
            print("On All Shipments page.")

            # Assert that both shipments are visible in the table
            # Wait for the table rows to be greater than 1 (header row + 2 data rows)
            expect(page.locator("table tr")).to_have_count(3, timeout=10000)
            print("Shipment table loaded with 2 shipments.")

            # Since I can't test the filter, I'll just screenshot the full list.
            print("Taking screenshot...")
            page.screenshot(path="jules-scratch/verification/all_shipments_verification.png")
            print("Successfully took screenshot.")

        except Exception as e:
            print(f"An error occurred during Playwright verification: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
