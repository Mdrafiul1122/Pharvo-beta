"""Shared Selenium web driver setup that launches Brave (Chromium)."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from helpers import config


def create_driver():
    """Build a Selenium WebDriver that drives Brave Browser.

    Brave is Chromium based, so ChromeDriver (resolved automatically by
    Selenium Manager) can drive it once we point at the ``brave.exe`` binary.
    """
    options = Options()
    options.binary_location = config.BRAVE_BINARY

    if config.HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    # Keep Brave stable in automation environments.
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    driver.implicitly_wait(config.IMPLICIT_WAIT)
    return driver