"""Tests for the Reports / Analytics module."""
import unittest

from helpers import config
from helpers.base import PharvoTestCase


class TestReports(PharvoTestCase):

    def open_reports(self):
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.open_module(config.NAV_REPORTS, config.PAGE_TITLE_REPORTS)

    def test_period_switcher_is_shown(self):
        """The reports module renders the 7/30/90-day period switcher."""
        self.open_reports()
        self.wait_text("Daily Sales Trend", timeout=config.PAGE_LOAD_TIMEOUT)
        for period in ("7 Days", "30 Days", "3 Months"):
            self.assert_shown(period, timeout=6)

    def test_report_summary_cards(self):
        """The reports module shows the four main summary cards."""
        self.open_reports()
        self.wait_text("Daily Sales Trend", timeout=config.PAGE_LOAD_TIMEOUT)
        for label in ("Revenue", "Sales", "Items Sold", "Profit"):
            self.assert_shown(label, timeout=6)

    def test_stock_report_section(self):
        """The stock report panel lists its inventory-health metrics."""
        self.open_reports()
        self.wait_text("Stock Report", timeout=config.PAGE_LOAD_TIMEOUT)
        for label in ("Active Products", "Low Stock", "Out of Stock", "Expired", "Near Expiry"):
            self.assert_shown(label, timeout=6)

    def test_top_selling_products_section(self):
        """The top-selling-products table is rendered on the reports page."""
        self.open_reports()
        self.wait_text("Top Selling Products", timeout=config.PAGE_LOAD_TIMEOUT)


if __name__ == "__main__":
    unittest.main(verbosity=2)