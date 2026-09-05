"""Tests for the Customers module."""
import time
import unittest

from selenium.webdriver.common.by import By

from helpers import config
from helpers.base import PharvoTestCase


class TestCustomers(PharvoTestCase):

    def open_customers(self):
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.open_module(config.NAV_CUSTOMERS, config.PAGE_TITLE_CUSTOMERS)
        self.wait_text("Customer Management", timeout=config.PAGE_LOAD_TIMEOUT)

    def test_stat_cards_are_shown(self):
        """The customers module shows its four summary stat cards."""
        self.open_customers()
        for label in ("Total Customers", "Loyalty Members", "Active", "New"):
            self.assert_shown(label, timeout=6)

    def test_search_customer_input(self):
        """The customers module provides a name/phone/email search box."""
        self.open_customers()
        inputs = self.driver.find_elements(
            By.CSS_SELECTOR, "input[placeholder*='Search by name, phone or email']"
        )
        self.assertTrue(len(inputs) > 0, "Expected a customer search input.")

    def test_tier_and_status_filters_exist(self):
        """Both tier and status dropdown filters are present."""
        self.open_customers()
        self.assert_shown("All Tiers", timeout=6)
        self.assert_shown("All Status", timeout=6)

    def test_add_customer_button_opens_modal(self):
        """Clicking 'Add Customer' opens the new-customer modal with fields."""
        self.open_customers()
        self.click_text("Add Customer")
        self.wait_text("Add New Customer", timeout=6)
        for field in ("Full Name", "Phone Number", "Email", "Address", "Membership Tier", "Notes"):
            self.assert_shown(field, timeout=6)

    def test_customer_table_headers(self):
        """The customer table lists the documented columns."""
        self.open_customers()
        for header in ("Customer", "Phone", "Email", "Membership", "Purchases", "Last Purchase", "Status", "Actions"):
            self.assert_shown(header, timeout=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)