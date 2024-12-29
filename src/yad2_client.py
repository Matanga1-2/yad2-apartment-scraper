import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .browser import Browser


class Yad2Client:
    BASE_URL = "https://www.yad2.co.il"
    REALESTATE_URL = f"{BASE_URL}/realestate/forsale"

    def __init__(self, headless: bool = True):
        self.browser = Browser(headless=headless)
        self.logger = logging.getLogger(__name__)

    def open_search_page(self, timeout: int = 60) -> bool:
        """Opens Yad2 real estate search page and waits for it to load"""
        try:
            self.logger.info(f"Accessing {self.REALESTATE_URL}")
            self.browser.driver.get(self.REALESTATE_URL)

            if self.browser.has_captcha():
                self.logger.warning("Initial captcha check failed")
                return False

            # Wait for search box to appear
            WebDriverWait(self.browser.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "map-page-layout_searchBox__bMAwa"))
            )

            if self.browser.has_captcha():
                self.logger.warning("Post-wait captcha check failed")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to open search page: {str(e)}")
            return False

    def close(self):
        """Closes the browser"""
        self.browser.quit()

    def __enter__(self):
        self.browser.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()