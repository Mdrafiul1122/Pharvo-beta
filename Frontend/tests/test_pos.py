"""Tests for the Sales / POS module."""
import unittest

from selenium.webdriver.common.by import By

from helpers import config
from helpers.base import PharvoTestCase


class TestPOS(PharvoTestCase):

    def open_pos(self):
        self.login(wait_for=config.PAGE_TITLE_DASHBOARD)
        self.open_module(config.NAV_POS, config.PAGE_TITLE_POS)
        # Placeholders are attributes, not text nodes; wait on CSS.
        self.wait_for(
            By.CSS_SELECTOR, "input[placeholder*='Search medicines by name']",
            timeout=config.PAGE_LOAD_TIMEOUT,
        )

    def test_pos_page_loads(self):
        """The POS module initialises with the expected toolbar elements."""
        self.open_pos()
        self.assert_shown("Walk-in Customer", timeout=6)
        self.assert_shown("Current Sale", timeout=6)

    def test_search_medicine_returns_hits(self):
        """Typing in POS search surfaces matching medicines."""
        self.open_pos()
        search = self.driver.find_element(
            By.CSS_SELECTOR, "input[placeholder*='Search medicines by name']"
        )
        search.send_keys("Brufen")
        self.wait_text("Brufen", timeout=config.PAGE_LOAD_TIMEOUT)

    def test_add_medicine_to_cart(self):
        """Clicking an 'Add' unit button moves a medicine into the current sale."""
        self.open_pos()
        # The catalogue has Add PC / Add Strip / Add Box buttons per row.
        add_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(),'Add ')]")
        self.assertTrue(
            len(add_buttons) > 0, "Expected at least one 'Add ...' unit button in the POS."
        )
        # Try buttons until one lands in the cart (some may be disabled when
        # the medicine has no stock for that unit).
        added = False
        for button in add_buttons:
            button.click()
            if self.is_text_visible("1 ×", timeout=3):
                added = True
                break
        self.assertTrue(
            added, "Clicking an Add button did not put an item into the current sale."
        )
        self.assert_shown("Subtotal", timeout=6)

    def test_payment_methods_are_available(self):
        """The three payment methods render as selectable buttons."""
        self.open_pos()
        for method in ("Cash", "bKash / Digital", "Split"):
            # Method labels come from PAYMENT_METHODS config.
            found = self.driver.find_elements(
                By.XPATH, f"//button[contains(., '{method}')]"
            )
            self.assertTrue(len(found) > 0, f"Expected payment method '{method}' to exist.")

    def test_sale_action_buttons_exist(self):
        """Hold Sale, Clear Cart and Complete Sale controls are available."""
        self.open_pos()
        for label in ("Hold Sale", "Clear Cart", "Complete Sale"):
            self.assert_shown(label, timeout=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)