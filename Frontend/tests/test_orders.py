"""Tests for the Orders module."""
import unittest

from selenium.webdriver.common.by import By

from helpers import config
from helpers.base import PharvoTestCase


class TestOrders(PharvoTestCase):

    def open_orders(self):
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.open_module(config.NAV_ORDERS, config.PAGE_TITLE_ORDERS)
        self.wait_text("Sales Orders", timeout=config.PAGE_LOAD_TIMEOUT)

    def test_stat_cards_are_shown(self):
        """The orders module shows its summary stat cards."""
        self.open_orders()
        for label in ("Orders", "Revenue", "Line Items"):
            self.assert_shown(label, timeout=6)

    def test_order_table_headers(self):
        """The sales-orders table lists the documented columns."""
        self.open_orders()
        for header in ("Invoice", "Customer", "Date", "Items", "Payment", "Discount", "Total"):
            self.assert_shown(header, timeout=6)

    def test_payment_method_filter_exists(self):
        """The payment method dropdown exposes the available methods."""
        self.open_orders()
        for option in ("All Methods", "Cash", "bKash", "Card"):
            found = self.driver.find_elements(
                By.XPATH, f"//option[contains(text(), '{option}')]"
            )
            self.assertTrue(len(found) > 0, f"Expected filter option '{option}'.")

    def test_order_search_input(self):
        """The orders module provides an invoice/customer search box."""
        self.open_orders()
        inputs = self.driver.find_elements(
            By.CSS_SELECTOR, "input[placeholder*='Invoice no. or customer']"
        )
        self.assertTrue(len(inputs) > 0, "Expected an order search input.")


if __name__ == "__main__":
    unittest.main(verbosity=2)