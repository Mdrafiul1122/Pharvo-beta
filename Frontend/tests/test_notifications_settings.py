"""Tests for Notifications and Settings modules."""
import unittest

from helpers import config
from helpers.base import PharvoTestCase


class TestNotifications(PharvoTestCase):

    def open_notifications(self):
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.open_module(config.NAV_NOTIFICATIONS, config.PAGE_TITLE_NOTIFICATIONS)

    def test_notifications_page_loads(self):
        """The notifications module renders the filter bar and actions."""
        self.open_notifications()
        self.wait_text("Notifications", timeout=config.PAGE_LOAD_TIMEOUT)
        for control in ("All", "Unread", "Mark all read"):
            self.assert_shown(control, timeout=6)


class TestSettings(PharvoTestCase):

    def open_settings(self):
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.open_module(config.NAV_SETTINGS, config.PAGE_TITLE_SETTINGS)

    def test_settings_shows_account_information(self):
        """The settings module displays the account information panel."""
        self.open_settings()
        self.wait_text("Account Information", timeout=config.PAGE_LOAD_TIMEOUT)
        for label in ("Full Name", "Username", "Email", "Role"):
            self.assert_shown(label, timeout=6)

    def test_settings_shows_sign_out_action(self):
        """The settings page provides a Sign out button."""
        self.open_settings()
        self.wait_text("Account Information", timeout=config.PAGE_LOAD_TIMEOUT)
        self.assert_shown("Sign out", timeout=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)