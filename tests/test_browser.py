import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.browser import BrowserSetup

logger = logging.getLogger(__name__)


def test_browser_initialization():
    logger.info("Testing browser initialization")
    browser = BrowserSetup(headless=True)
    driver = browser.init_driver()
    assert driver is not None
    browser.quit()
    logger.info("Browser initialization test completed")


def test_yad2_access():
    logger.info("Testing Yad2 website access")
    browser = BrowserSetup(headless=False)
    driver = browser.init_driver()

    try:
        url = "https://www.yad2.co.il/realestate/forsale"
        logger.info(f"Accessing URL: {url}")
        driver.get(url)

        assert "yad2" in driver.current_url.lower()
        logger.info("URL validation successful")

        if browser.check_for_captcha():
            logger.warning("Waiting for manual Captcha resolution...")

        logger.info("Waiting for search box element")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "map-page-layout_searchBox__bMAwa"))
        )
        logger.info("Search box element found")

        if browser.check_for_captcha():
            logger.warning("Captcha still present after timeout")
            raise RuntimeError("Could not proceed - Captcha challenge active")

    except Exception as e:
        if browser.check_for_captcha():
            raise RuntimeError("Blocked by Captcha challenge") from e
        raise
    finally:
        browser.quit()


def test_browser_quit():
    """Test browser closes properly"""
    logger.info("Testing browser quit functionality")
    browser = BrowserSetup(headless=True)
    driver = browser.init_driver()
    assert driver is not None

    logger.info("Closing browser")
    browser.quit()

    # Simply verify driver attribute is None after quit
    assert browser.driver is None
    logger.info("Browser quit test completed")