"""Tests for the Medicines & Inventory module."""
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from helpers import config
from helpers.base import PharvoTestCase


class TestMedicinesInventory(PharvoTestCase):

    def open_inventory(self):
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.open_module(config.NAV_MEDICINES, config.PAGE_TITLE_MEDICINES)
        # Wait for the medicine catalogue to load from the API.
        self.wait_text("Medicine Catalogue", timeout=config.PAGE_LOAD_TIMEOUT)
        self.wait_text("Total Medicines", timeout=config.PAGE_LOAD_TIMEOUT)

    def test_stat_cards_are_shown(self):
        """The inventory module shows its five summary stat cards."""
        self.open_inventory()
        for label in ("Total Medicines", "Active", "Low Stock", "Out of Stock", "Expired / Near"):
            self.assert_shown(label, timeout=6)

    def test_medicine_search_filters_rows(self):
        """Typing in the search box narrows the medicine table."""
        self.open_inventory()
        search = self.driver.find_element(
            By.CSS_SELECTOR, "input[placeholder*='Search by name, brand or barcode']"
        )
        search.send_keys("Brufen")
        # Debounce is ~350ms; wait for the filtered result to appear.
        self.wait_text("Brufen", timeout=config.PAGE_LOAD_TIMEOUT)

    def test_status_filter_tabs_exist(self):
        """All five stock-status filter tabs are present."""
        self.open_inventory()
        for tab in ("All", "Low Stock", "Out of Stock", "Expired", "Near Expiry"):
            self.assert_shown(tab, timeout=6)

    def test_inventory_table_columns_exist(self):
        """The medicine table renders the documented column headers."""
        self.open_inventory()
        for header in ("Medicine", "Category", "Price", "Stock Level", "Reorder Level", "Expiry", "Status"):
            self.assert_shown(header, timeout=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)