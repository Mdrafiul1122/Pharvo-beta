"""Tests for the CRM module."""
import unittest

from helpers import config
from helpers.base import PharvoTestCase


class TestCRM(PharvoTestCase):

    def open_crm(self):
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.open_module(config.NAV_CRM, "CRM")
        self.wait_text("CRM Dashboard", timeout=config.PAGE_LOAD_TIMEOUT)

    def test_crm_submenu_tabs_exist(self):
        """The CRM module exposes all six sub-menu tabs."""
        self.open_crm()
        for tab in ("CRM Dashboard", "Customer Tiers", "Medicine Reminders",
                    "Health Information", "Receipts", "Notifications"):
            self.assert_shown(tab, timeout=6)

    def test_crm_dashboard_stat_cards(self):
        """The CRM dashboard shows customer/reminder summary statistics."""
        self.open_crm()
        # A couple of representative stat card labels render on the dashboard.
        self.wait_for_any(
            "Total Customers", "Med. Purchases", "Customer Spend",
            "Active Reminders", timeout=config.PAGE_LOAD_TIMEOUT,
        )

    def test_navigate_to_medicine_reminders(self):
        """Switching to the Medicine Reminders tab shows the reminders filters."""
        self.open_crm()
        self.click_text("Medicine Reminders")
        self.wait_text("Med. Reminders", timeout=config.PAGE_LOAD_TIMEOUT)
        self.assert_shown("Add Reminder", timeout=6)

    def test_reminder_add_modal_fields(self):
        """Opening 'Add Reminder' reveals the documented reminder form fields."""
        self.open_crm()
        self.click_text("Medicine Reminders")
        self.wait_text("Med. Reminders", timeout=config.PAGE_LOAD_TIMEOUT)
        self.click_text("Add Reminder")
        self.wait_text("Add Medicine Reminder", timeout=6)
        for field in ("Customer", "Medicine Name", "Dose", "Frequency", "Start Date", "End Date"):
            self.assert_shown(field, timeout=6)

    def test_navigate_to_receipts(self):
        """Switching to the Receipts tab shows the receipts table."""
        self.open_crm()
        self.click_text("Receipts")
        self.wait_text("Recent Receipts", timeout=config.PAGE_LOAD_TIMEOUT)
        self.assert_shown("Export", timeout=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)