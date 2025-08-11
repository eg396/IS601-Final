# tests/e2e/test_e2e.py

# tests/ui/test_calculator_crud.py
import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"

def user_register(page: Page):

    # Navigate to the registration page
    page.goto("http://localhost:8000/register")

    # Fill the registration form fields (use valid data)
    page.fill("#username", "testuser123")
    page.fill("#email", "testuser123@example.com")
    page.fill("#first_name", "Test")
    page.fill("#last_name", "User")
    page.fill("#password", "StrongPass1!")
    page.fill("#confirm_password", "StrongPass1!")

    page.click("button[type=submit]")

    page.wait_for_url("**/login", timeout=5000)

def user_login(page: Page):

    page.fill('input[name="username"]', "testuser123")
    page.fill('input[name="password"]', "StrongPass1!")
    page.click("button[type=submit]")

    # Should redirect to dashboard
    page.wait_for_url("**/dashboard", timeout=5000)

@pytest.mark.e2e
def test_unauthorized_access_redirects_to_login(page):

    url_list = ["http://localhost:8000/dashboard",
                "http://localhost:8000/dashboard/edit",
                "http://localhost:8000/view_calculation"]
    
    for url in url_list:
        page.goto(url)
        try:
            page.wait_for_url("**/login", timeout=3000)
            assert "/login" in page.url
        except:
            # If not redirected, check for 404 text or JSON
            assert "not found" in page.content().lower()

@pytest.mark.e2e
def test_calculation_crud_flow(page: Page):

    # 1. Register

    user_register(page)

    # 2. Login

    user_login(page)

    # 3. Create a calculation
    page.click("text=New Calculation")
    page.select_option("select[name='type']", "multiplication")
    page.fill("input[name='inputs']", "3,4")
    page.click("button[type=submit]")

    # 4. Verify calculation is listed on dashboard

    expect(page.locator("table")).to_contain_text("multiplication")
    expect(page.locator("table")).to_contain_text("12")  # 3*4 result

    # 5. Edit calculation
    page.click("text=Edit")
    page.fill("input[name='inputs']", "5,6")
    page.click("button[type=submit]")

    # Check to see if page has updated to display new calculation result
    assert page.locator("text=30").count() > 0


    # 6. Delete calculation
    page.click("text=View Details")
    page.on("dialog", lambda dialog: dialog.accept())
    page.click("text=Delete")
    page.wait_for_url("**/dashboard")

    # Verify it's gone from list
    table_text = page.locator("table").inner_text()
    assert "multiplication" not in table_text

@pytest.mark.e2e
def test_register_invalid_email(page):
    page.goto("http://localhost:8000/register")
    page.fill("#username", "testuser123")
    page.fill("#email", "invalid-email")  # Invalid email format
    page.fill("#first_name", "Test")
    page.fill("#last_name", "User")
    page.fill("#password", "StrongPass1!")
    page.fill("#confirm_password", "StrongPass1!")
    old_url = page.url
    page.click("button[type=submit]")
    # wait a moment to give the client-side validation time to kick in
    page.wait_for_timeout(5000)  
    # assert URL stayed the same (i.e., no navigation)
    assert page.url == old_url

@pytest.mark.e2e
def test_bad_calculation_input(page: Page):
    # Login first

    page.goto("http://localhost:8000/login")

    user_login(page)

    # Navigate to New Calculation page or open modal
    page.click("text=New Calculation")

    # Select operation type
    page.select_option("select[name='type']", "addition")

    # Fill invalid inputs (non-numeric)
    page.fill("input[name='inputs']", "three seven")

    # Submit the calculation form
    page.click("button[type=submit]")

    assert page.locator("text=10").count() == 0

@pytest.mark.e2e
def test_api_error_response_redirects_to_login(page):
    # Set up localStorage to simulate a logged-in user
    page.add_init_script("""
        window.localStorage.setItem('access_token', 'fake-valid-token');
        window.localStorage.setItem('username', 'TestUser');
    """)

    # Force the /calculations API call to fail with a 500 error
    page.route("/calculations", lambda route: route.fulfill(
        status=500,
        body='{"detail":"Internal Server Error"}',
        headers={"Content-Type": "application/json"}
    ))

    # Go to the dashboard (where the failing API request happens)
    page.goto("http://localhost:8000/dashboard")

    # Wait for the app to handle it and redirect to login
    page.wait_for_url("**/login")

    # Confirm we are back on the login screen
    assert page.url.endswith("/login")