import logging

from src.browser import Browser
from src.yad2_client import Yad2Client

logger = logging.getLogger(__name__)

def test_browser_initialization():
    logger.info("Testing browser initialization")
    with Browser(headless=True) as browser:
        assert browser.driver is not None
    logger.info("Browser initialization test completed")

def test_browser_quit():
    logger.info("Testing browser quit functionality")
    browser = Browser(headless=True)
    browser.init_driver()
    assert browser.driver is not None
    browser.quit()
    assert browser.driver is None
    logger.info("Browser quit test completed")

def test_yad2_client():
    logger.info("Testing Yad2 client access")
    with Yad2Client(headless=False) as client:
        success = client.open_search_page()
        assert success, "Failed to open Yad2 search page"
        assert "yad2" in client.browser.driver.current_url.lower()
        logger.info("Yad2 client test completed")