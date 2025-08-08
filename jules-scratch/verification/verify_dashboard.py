from playwright.sync_api import sync_playwright, expect
import time

def run_verification():
    """
    This script tests that a user can log in and view the dashboard
    with the KPI cards and chart rendered.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the login page
            print("Navigating to login page...")
            page.goto("http://localhost:5173/login", timeout=30000)

            # Fill in the login form with the default user credentials
            print("Filling in login form...")
            page.get_by_label("Email Address").fill("test@test.com")
            page.get_by_label("Password").fill("password")

            # Click the login button
            print("Clicking login button...")
            page.get_by_role("button", name="Log In").click()

            # Assert: Check for the Dashboard heading to appear
            print("Waiting for dashboard...")
            dashboard_heading = page.get_by_role("heading", name="Dashboard")
            expect(dashboard_heading).to_be_visible(timeout=15000)
            print("Dashboard is visible.")

            # Wait for KPI cards to be populated (check for non-placeholder value)
            # We check the "In Transit" card. The value is initially '...'
            in_transit_kpi = page.locator('p:has-text("In Transit")').locator('xpath=preceding-sibling::p')
            expect(in_transit_kpi).not_to_have_text("...", timeout=10000)
            print("KPI cards have loaded data.")

            # A small delay to ensure chart animation can complete
            time.sleep(1)

            # Screenshot: Capture the final result
            print("Taking screenshot...")
            page.screenshot(path="jules-scratch/verification/dashboard_verification.png")
            print("Successfully took screenshot of dashboard.")

        except Exception as e:
            print(f"An error occurred during Playwright verification: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
