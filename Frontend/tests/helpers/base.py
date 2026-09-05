"""Base test case with shared helpers for driving the PHARVO UI.

Extending :class:`PharvoTestCase` gives every test the same browser, a set of
friendly wait/assert helpers, and login / navigation shortcuts so the test
cases stay short and readable.
"""
import time
import unittest

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import config
from helpers.driver import create_driver


class PharvoTestCase(unittest.TestCase):
    """Base class for every PHARVO UI test."""

    @classmethod
    def setUpClass(cls):
        cls.driver = create_driver()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Start every test logged out. PHARVO stores its session in
        # localStorage (not cookies), so clear that and reload, then wait for
        # the login form so the SPA session check cannot race the test.
        self.driver.get(config.BASE_URL + config.LOGIN_PATH)
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.get(config.BASE_URL + config.LOGIN_PATH)
        self.wait_for(By.ID, config.LOGIN_USERNAME_ID, timeout=config.PAGE_LOAD_TIMEOUT)

    # --- Browser helpers ---------------------------------------------------

    def wait_for(self, by, value, timeout=None):
        """Wait until an element is present and return it."""
        timeout = timeout or config.DEFAULT_TARGET_LOAD_WAIT
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_text(self, text, by=By.XPATH, timeout=None):
        """Wait until an element containing ``text`` appears in the DOM."""
        timeout = timeout or config.DEFAULT_TARGET_LOAD_WAIT
        return self.wait_for(by, self._xpath_contains_text(text), timeout)

    def find_text(self, text, timeout=None):
        """Return element(s) matching a visible text string."""
        timeout = timeout or config.DEFAULT_TARGET_LOAD_WAIT
        self.wait_text(text, timeout=timeout)
        return self.driver.find_elements(By.XPATH, self._xpath_contains_text(text))

    def is_text_visible(self, text, timeout=None):
        """True if ``text`` is currently rendered on the page.

        Uses ``innerText`` (which excludes hidden elements, ``<script>`` and
        ``<style>`` content) so CSS comments and other invisible copy never
        count as "shown".
        """
        timeout = timeout or config.IMPLICIT_WAIT
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            elements = self.driver.find_elements(
                By.XPATH, self._xpath_contains_text(text)
            )
            for el in elements:
                if self._element_renders_text(el, text):
                    return True
            time.sleep(0.25)
        return False

    @staticmethod
    def _element_renders_text(el, text):
        """True if the element is displayed and its rendered text has ``text``.

        CSS ``text-transform`` (e.g. ``uppercase``) changes what ``innerText``
        reports, so the comparison is case-insensitive.
        """
        try:
            if not el.is_displayed():
                return False
            return text.lower() in (el.get_attribute("innerText") or "").lower()
        except Exception:
            return False

    def click_text(self, text, wait_after=1.0):
        """Click a visible button/link rendered with the given text.

        Multiple DOM nodes may carry the same string (e.g. a wrapper div, the
        actual button and its inner label). We walk the matches deepest-first
        and click the first one Brave reports as interactable.
        """
        elements = self.find_text(text)
        if not elements:
            self.fail(f"Click target with text '{text}' not found.")
        last_error = None
        for el in reversed(elements):
            try:
                if self._element_renders_text(el, text):
                    el.click()
                    time.sleep(wait_after)
                    return
            except Exception as e:  # noqa: BLE001 - keep trying other nodes
                last_error = e
        self.fail(f"Could not click an element with text '{text}': {last_error}")

    def wait_for_any(self, *texts, timeout=None):
        """Wait until at least one of the given texts is present."""
        deadline = time.monotonic() + (timeout or config.DEFAULT_TARGET_LOAD_WAIT)
        while time.monotonic() < deadline:
            for t in texts:
                if self.is_text_visible(t, timeout=1):
                    return True
            time.sleep(0.3)
        return False

    @staticmethod
    def _xpath_contains_text(text):
        # Use "." (full string-value of the node) so elements whose text mixes
        # static labels with JSX interpolations are matched too, and quote the
        # literal safely for XPath.
        if "'" in text and '"' in text:
            bits = text.split("'")
            concat = "concat(" + ",'\\'',".join("'" + b + "'" for b in bits) + ")"
            return f"//*[contains(normalize-space(.), {concat})]"
        quote = '"' if "'" in text else "'"
        return f"//*[contains(normalize-space(.), {quote}{text}{quote})]"

    # --- App-level helpers --------------------------------------------------

    def wait_for_url(self, substring, timeout=None):
        """Wait until the current URL contains ``substring``."""
        timeout = timeout or config.PAGE_LOAD_TIMEOUT
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if substring in self.driver.current_url:
                return self.driver.current_url
            time.sleep(0.25)
        raise TimeoutException(
            f"URL never contained '{substring}'. Current URL: {self.driver.current_url}"
        )

    def login(self, username=None, password=None, wait_for=None, wait_url=None):
        """Log in with the given credentials.

        ``wait_for`` waits for landing text; ``wait_url`` waits for the URL
        to settle after the SPA navigation (the URL can lag the DOM slightly).
        """
        username = username or config.DEMO_USERNAME
        password = password or config.DEMO_PASSWORD

        self.wait_for(By.ID, config.LOGIN_USERNAME_ID).send_keys(username)
        self.wait_for(By.ID, config.LOGIN_PASSWORD_ID).send_keys(password)
        self.wait_for(By.ID, config.LOGIN_SUBMIT_ID).click()

        if wait_for:
            self.wait_text(wait_for, timeout=config.PAGE_LOAD_TIMEOUT)
        if wait_url:
            self.wait_for_url(wait_url, timeout=config.PAGE_LOAD_TIMEOUT)

    def open_module(self, label, expected_title):
        """Navigate to a sidebar module and wait for its header title."""
        self.click_text(label)
        self.wait_text(expected_title, timeout=config.PAGE_LOAD_TIMEOUT)

    def close_modal(self):
        """Close any open modal by pressing Escape if needed (no-op if none)."""
        from selenium.webdriver.common.keys import Keys
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    # --- Small convenience assertions ----------------------------------------

    def assert_shown(self, text, timeout=None):
        self.assertTrue(
            self.is_text_visible(text, timeout=timeout),
            f"Expected text '{text}' to be shown on the page but it was not.",
        )

    def assert_not_shown(self, text, timeout=2):
        self.assertFalse(
            self.is_text_visible(text, timeout=timeout),
            f"Expected text '{text}' NOT to be shown, but it was.",
        )