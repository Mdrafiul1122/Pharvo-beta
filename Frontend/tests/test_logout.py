"""Tests for logout and protected-page navigation."""
import unittest

from selenium.webdriver.common.by import By

from helpers import config
from helpers.base import PharvoTestCase


class TestLogout(PharvoTestCase):

    def test_sign_out_returns_to_login(self):
        """The sidebar Sign Out button clears the session and returns to /."""
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.click_text("Sign Out", wait_after=2)
        # After logout the app redirects to the login page.
        self.wait_text("Welcome back", timeout=config.PAGE_LOAD_TIMEOUT)
        self.wait_for_url(config.LOGIN_PATH, timeout=config.PAGE_LOAD_TIMEOUT)
        self.assertEqual(config.BASE_URL + config.LOGIN_PATH, self.driver.current_url)

    def test_user_menu_sign_out(self):
        """The header user-menu also exposes a working Sign Out action."""
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        # Open the user menu (avatar button in the header).
        menu_buttons = self.driver.find_elements(
            By.CSS_SELECTOR, "header button"
        )
        # Click the first header button that toggles the user menu (the one
        # containing the avatar/down-chevron). We pick the last header button.
        menu_buttons[-1].click()
        self.wait_text("Profile Settings", timeout=6)
        self.click_text("Sign Out", wait_after=2)
        self.wait_text("Welcome back", timeout=config.PAGE_LOAD_TIMEOUT)
        self.wait_for_url(config.LOGIN_PATH, timeout=config.PAGE_LOAD_TIMEOUT)


class TestProtectedPages(PharvoTestCase):

    def test_admin_dashboard_requires_login(self):
        """Visiting a protected route while logged out shows the login page."""
        self.driver.get(config.BASE_URL + config.ADMIN_DASHBOARD_PATH)
        self.wait_text("Welcome back", timeout=config.PAGE_LOAD_TIMEOUT)
        # Dashboard content must NOT be reachable.
        self.assert_not_shown(config.PAGE_TITLE_DASHBOARD, timeout=3)

    def test_unknown_route_falls_back_to_login(self):
        """An unrecognised path renders the login page when not authenticated."""
        self.driver.get(config.BASE_URL + "/totally/unknown")
        self.wait_text("Welcome back", timeout=config.PAGE_LOAD_TIMEOUT)


if __name__ == "__main__":
    unittest.main(verbosity=2)