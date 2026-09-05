"""PHARVO Selenium test configuration.

Central place for the base URL, credentials, and selectors used across the
automated test suite. All values were taken directly from the running
PHARVO frontend/backend and its source code.
"""

# --- Application URLs ---------------------------------------------------

# The Vite dev server hosting the PHARVO frontend.
BASE_URL = "http://localhost:5173"

# Route paths used by the app (manual routing via window.location).
LOGIN_PATH = "/"
SIGNUP_PATH = "/signup"
ADMIN_DASHBOARD_PATH = "/admin/dashboard"
PHARMACIST_DASHBOARD_PATH = "/pharmacist/dashboard"
CUSTOMER_PORTAL_PATH = "/customer/portal"

# --- Demo credentials (hardcoded in the login page) ---------------------
# Username / password shown in the green "Demo Login" box on the login page.
DEMO_USERNAME = "rafi"
DEMO_PASSWORD = "787878"

# Invalid credentials used to check the failure path.
INVALID_USERNAME = "rafi"
INVALID_PASSWORD = "totally-wrong-password"

# --- Browser ------------------------------------------------------------
# Full path to the Brave Browser executable (Chromium-based).
BRAVE_BINARY = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# Run in headless mode (no browser window). Set to False to watch the tests.
HEADLESS = True

# --- Timeouts (seconds) -------------------------------------------------
IMPLICIT_WAIT = 6
PAGE_LOAD_TIMEOUT = 20
DEFAULT_TARGET_LOAD_WAIT = 3

# --- Common selectors used everywhere -----------------------------------
LOGIN_USERNAME_ID = "username"
LOGIN_PASSWORD_ID = "password"
LOGIN_SUBMIT_ID = "sign-in-btn"
LOGIN_TITLE_ID = "login-title"

# Sidebar module navigation buttons (identified by exact label text).
NAV_DASHBOARD = "Dashboard"
NAV_POS = "POS / Sales"
NAV_MEDICINES = "Medicines & Inventory"
NAV_CUSTOMERS = "Customers"
NAV_CRM = "CRM"
NAV_ORDERS = "Orders"
NAV_REPORTS = "Reports"
NAV_NOTIFICATIONS = "Notifications"
NAV_SETTINGS = "Settings"

# Header page titles (from PAGE_META in StaffApp.jsx).
PAGE_TITLE_DASHBOARD = "Dashboard"
PAGE_TITLE_POS = "POS / Sales"
PAGE_TITLE_MEDICINES = "Medicines & Inventory"
PAGE_TITLE_CUSTOMERS = "Customer Management"
PAGE_TITLE_ORDERS = "Orders"
PAGE_TITLE_REPORTS = "Reports"
PAGE_TITLE_NOTIFICATIONS = "Notifications"
PAGE_TITLE_SETTINGS = "Settings"