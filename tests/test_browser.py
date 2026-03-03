import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

def test_oidc_saml_buttons(browser):
    page = browser.new_page()
    page.goto("http://localhost:8000")

    # Test OIDC button
    page.click("#startOidc")
    page.wait_for_selector("#results .row")
    assert page.inner_text("#results") != ""

    # Test SAML button
    page.click("#startSaml")
    page.wait_for_selector("#results .row")
    assert page.inner_text("#results") != ""

    page.close()
