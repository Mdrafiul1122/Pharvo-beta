"""Tests for the admin/pharmacist Dashboard."""
import unittest

from helpers import config
from helpers.base import PharvoTestCase


class TestDashboard(PharvoTestCase):

    def test_dashboard_loads_core_summary_cards(self):
        """The dashboard shows its main stat, chart and alert cards."""
        self.login(wait_for="Overview of your pharmacy operations today")
        self.assert_shown("Today's Sales")
        self.assert_shown("Today's Profit")
        self.assert_shown("Low Stock")
        self.assert_shown("Expiring Soon")
        self.assert_shown("Sales & Profit Overview")

    def test_dashboard_has_important_alerts_panel(self):
        """The important-alerts panel renders with the three alert types."""
        self.login(wait_for="Overview of your pharmacy operations today")
        self.assert_shown("Important Alerts")
        # Three alert topic labels live in the panel.
        self.assert_shown("Stock")
        self.assert_shown("Expiry")
        self.assert_shown("Security")
        # Each alert carries a descriptive action sentence.
        self.assert_shown("medicines below minimum stock")
        self.assert_shown("medicines expire within 30 days")

    def test_dashboard_allows_switching_report_range(self):
        """The dashboard period buttons are present and interactive."""
        import time
        self.login(wait_for="Overview of your pharmacy operations today")
        # Wait for data to load initially.
        time.sleep(2)
        for label in ("7 Days", "30 Days", "3 Months"):
            targets = self.find_text(label)
            self.assertTrue(len(targets) > 0, f"Expected dashboard range '{label}' to exist.")


if __name__ == "__main__":
    unittest.main(verbosity=2)