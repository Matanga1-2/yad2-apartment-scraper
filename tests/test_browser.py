import logging
import time

from selenium.webdriver.common.by import By

from src.yad2.browser import Browser

# Setup logger at module level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Only add handler if none exists to prevent duplicate handlers
if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)


def test_browser_initialization():
    logger.info("Testing browser initialization")
    with Browser(headless=True) as browser:
        assert browser.driver is not None
    logger.info("Browser initialization test completed")


def test_wait_for_element():
    with Browser(headless=True) as browser:
        browser.driver.get("https://example.com")
        element = browser.wait_for_element(By.TAG_NAME, "h1")
        assert element.text == "Example Domain"


def test_random_delay():
    min_delay = 1.0
    max_delay = 2.0
    margin = 0.1  # Allow 100ms margin for timing variations
    start_time = time.time()
    Browser.random_delay(min_delay, max_delay)
    elapsed = time.time() - start_time
    assert min_delay <= elapsed <= max_delay + margin


def test_wait_for_clickable():
    with Browser(headless=True) as browser:
        browser.driver.get("https://example.com")
        element = browser.wait_for_clickable(By.TAG_NAME, "a")
        assert element is not None


def test_safe_click():
    with Browser(headless=True) as browser:
        browser.driver.get("https://example.com")
        element = browser.wait_for_clickable(By.TAG_NAME, "a")
        browser.safe_click(element)
        assert True  # If no exception raised, click successful


def test_browser_quit():
    logger.info("Testing browser quit functionality")
    browser = Browser(headless=True)
    browser.init_driver()
    assert browser.driver is not None
    browser.quit()
    assert browser.driver is None
    logger.info("Browser quit test completed")