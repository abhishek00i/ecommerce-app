import httpx
from playwright.sync_api import sync_playwright, expect
import time

def run_verification():
    """
    This script tests the entire "Create Shipment" flow.
    """
    BASE_API_URL = "http://localhost:8000"

    # --- Setup: Log in as the default user to get a token ---
    login_payload = {"username": "test@test.com", "password": "password"}
    r = httpx.post(f"{BASE_API_URL}/token", data=login_payload)
    assert r.status_code == 200, f"Failed to log in: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- Setup: Create a carrier to use in the form ---
    carrier_payload = {"name": "TestCarrier", "is_active": True}
    r = httpx.post(f"{BASE_API_URL}/carriers/", json=carrier_payload, headers=headers)
    assert r.status_code == 200, f"Failed to create carrier: {r.text}"
    carrier_id = r.json()["id"]

    # --- Playwright Test ---
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # First, we need to manually set the auth token in the browser context
            # so the AuthProvider finds it on page load.
            page.goto("http://localhost:5173/login")
            page.evaluate(f"localStorage.setItem('authToken', '{token}')")

            # Navigate to the create shipment page
            print("Navigating to Create Shipment page...")
            page.goto("http://localhost:5173/create-shipment", timeout=30000)

            # Assert that we are on the correct page
            expect(page.get_by_role("heading", name="Create New Shipment")).to_be_visible()
            print("On Create Shipment page.")

            # --- Fill Sender Details ---
            page.get_by_label("Contact Name").first.fill("Sender Name")
            page.get_by_label("Phone").first.fill("1112223333")
            page.get_by_label("Address Line 1").first.fill("123 Sender Lane")
            page.get_by_label("City").first.fill("Senderton")
            page.get_by_label("State").first.fill("Sender State")
            page.get_by_label("Pincode").first.fill("100001")

            # --- Fill Recipient Details ---
            page.get_by_label("Contact Name").nth(1).fill("Recipient Name")
            page.get_by_label("Phone").nth(1).fill("4445556666")
            page.get_by_label("Address Line 1").nth(1).fill("456 Recipient Drive")
            page.get_by_label("City").nth(1).fill("Receiverville")
            page.get_by_label("State").nth(1).fill("Recipient State")
            page.get_by_label("Pincode").nth(1).fill("200002")

            # --- Fill Package Details ---
            page.get_by_label("Weight (kg)").fill("2.5")
            page.get_by_label("Length (cm)").fill("30")
            page.get_by_label("Width (cm)").fill("20")
            page.get_by_label("Height (cm)").fill("10")
            page.get_by_label("Contents").fill("Important Documents")
            page.get_by_label("Invoice Value (₹)").fill("500")
            page.get_by_label("Carrier ID").fill(str(carrier_id))

            # Submit the form
            print("Submitting form...")
            page.get_by_role("button", name="Book Shipment").click()

            # Assert: Check for the success message
            success_message = page.locator("div:has-text('Shipment created successfully')")
            expect(success_message).to_be_visible(timeout=10000)
            print("Success message is visible.")

            # Screenshot: Capture the final result
            print("Taking screenshot...")
            page.screenshot(path="jules-scratch/verification/create_shipment_verification.png")
            print("Successfully took screenshot.")

        except Exception as e:
            print(f"An error occurred during Playwright verification: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
