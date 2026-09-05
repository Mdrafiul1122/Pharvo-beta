"""Tests for the home (login) page and sidebar navigation."""
import unittest

from selenium.webdriver.common.by import By

from helpers import config
from helpers.base import PharvoTestCase


class TestHomePage(PharvoTestCase):

    def test_login_page_loads_with_title_fields_and_button(self):
        """The home route shows the login form with all expected controls."""
        self.assert_shown("Welcome back", timeout=6)
        self.assertTrue(
            self.driver.find_element(By.ID, config.LOGIN_TITLE_ID).is_displayed()
        )
        self.assertTrue(self.driver.find_element(By.ID, config.LOGIN_USERNAME_ID).is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, config.LOGIN_PASSWORD_ID).is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, config.LOGIN_SUBMIT_ID).is_displayed())

    def test_demo_credentials_are_shown(self):
        """The demo login box exposes the documented username and password."""
        self.assert_shown("Demo Login", timeout=6)
        self.assert_shown(config.DEMO_USERNAME)
        self.assert_shown(config.DEMO_PASSWORD)

    def test_signup_link_navigates_to_signup(self):
        """The 'Create an account' link goes to the /signup route."""
        self.click_text("Create an account")
        self.wait_text("Create your account", timeout=config.PAGE_LOAD_TIMEOUT)
        self.assertEqual(config.BASE_URL + config.SIGNUP_PATH, self.driver.current_url)


class TestSignupPage(PharvoTestCase):

    def test_signup_page_has_expected_fields(self):
        """The sign-up form contains the documented field IDs."""
        self.driver.get(config.BASE_URL + config.SIGNUP_PATH)
        self.wait_text("Create your account", timeout=6)
        for field_id in ("full-name", "email", "password", "confirm-password", "sign-up-btn"):
            self.assertTrue(
                self.driver.find_element(By.ID, field_id).is_displayed(),
                f"Expected signup field #{field_id} to exist.",
            )


class TestSidebarNavigation(PharvoTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def run_sidebar_navigation(self):
        """Log in as admin and walk through each sidebar module."""
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)

        cases = [
            (config.NAV_POS, config.PAGE_TITLE_POS),
            (config.NAV_MEDICINES, config.PAGE_TITLE_MEDICINES),
            (config.NAV_CUSTOMERS, config.PAGE_TITLE_CUSTOMERS),
            (config.NAV_CRM, "CRM"),
            (config.NAV_ORDERS, config.PAGE_TITLE_ORDERS),
            (config.NAV_REPORTS, config.PAGE_TITLE_REPORTS),
            (config.NAV_NOTIFICATIONS, config.PAGE_TITLE_NOTIFICATIONS),
            (config.NAV_SETTINGS, config.PAGE_TITLE_SETTINGS),
            (config.NAV_DASHBOARD, config.PAGE_TITLE_DASHBOARD),
        ]
        for nav_label, expected_title in cases:
            with self.subTest(module=nav_label, expected=expected_title):
                self.open_module(nav_label, expected_title)

    def test_all_sidebar_modules_navigate_correctly(self):
        """Every sidebar entry switches to its module and updates the header."""
        self.run_sidebar_navigation()


if __name__ == "__main__":
    unittest.main(verbosity=2)