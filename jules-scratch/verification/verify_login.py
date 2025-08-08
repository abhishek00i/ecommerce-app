from playwright.sync_api import sync_playwright, expect

def run_verification():
    """
    This script tests the login flow using the default user
    created by the backend's startup logic.
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

            # Screenshot: Capture the final result
            print("Taking screenshot...")
            page.screenshot(path="jules-scratch/verification/verification.png")
            print("Successfully took screenshot of dashboard.")

        except Exception as e:
            print(f"An error occurred during Playwright verification: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
