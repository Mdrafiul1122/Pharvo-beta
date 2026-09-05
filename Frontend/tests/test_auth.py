"""Tests for the PHARVO authentication flow (login and sign-up)."""
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from helpers import config
from helpers.base import PharvoTestCase


class TestLogin(PharvoTestCase):

    def test_login_with_valid_demo_credentials(self):
        """Signing in with the demo credentials lands on the admin dashboard."""
        self.login(
            wait_for=config.PAGE_TITLE_DASHBOARD,
            wait_url=config.ADMIN_DASHBOARD_PATH,
        )
        self.assertEqual(
            config.BASE_URL + config.ADMIN_DASHBOARD_PATH, self.driver.current_url
        )

    def test_login_with_invalid_password_shows_error(self):
        """An invalid password keeps the user on the login page with an alert."""
        self.login(
            username=config.INVALID_USERNAME,
            password=config.INVALID_PASSWORD,
        )
        # The app shows a form-level error banner and stays on the login page.
        self.wait_text(
            "No active account found with the given credentials",
            timeout=config.PAGE_LOAD_TIMEOUT,
        )
        self.assertEqual(config.BASE_URL + config.LOGIN_PATH, self.driver.current_url)

    def test_submit_empty_form_blocks_login(self):
        """Submitting an empty form shows inline validation and does not redirect."""
        self.wait_for(By.ID, config.LOGIN_SUBMIT_ID).click()
        # Client-side validation messages appear before any request is made.
        self.wait_text("Email or username is required.", timeout=6)
        self.assertTrue(
            self.is_text_visible("Password is required."),
            "Expected a password-required validation message.",
        )

    def test_password_show_hide_toggle(self):
        """The password visibility toggle flips the input type between types."""
        password = self.wait_for(By.ID, config.LOGIN_PASSWORD_ID)
        password.send_keys("secret")
        self.assertEqual(
            password.get_attribute("type"), "password",
            "Password should be masked initially.",
        )
        toggle = self.wait_for(By.CSS_SELECTOR, "button[data-toggle-password]")
        toggle.click()
        self.assertEqual(
            password.get_attribute("type"), "text",
            "Password should be visible after toggling.",
        )


class TestSignupValidation(PharvoTestCase):

    def test_signup_with_empty_fields_shows_validation(self):
        """Attempting to sign up with blank fields surfaces validation errors."""
        self.driver.get(config.BASE_URL + config.SIGNUP_PATH)
        self.wait_text("Create your account", timeout=6)
        self.driver.find_element(By.ID, "sign-up-btn").click()

        self.wait_text("This field is required.", timeout=6)
        self.assertTrue(
            self.is_text_visible("Select a role."),
            "Expected a role-selection validation message.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)