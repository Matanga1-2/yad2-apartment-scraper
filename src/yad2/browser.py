import logging
import random
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Browser:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def init_driver(self) -> webdriver.Chrome:
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless=new')
            options.add_argument('--start-maximized')
            options.add_argument('--window-size=1920,1080')

            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            
            return self.driver

        except WebDriverException as e:
            self.logger.error(f"Browser initialization failed: {str(e)}")
            raise

    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be present and visible"""
        try:
            self.logger.debug(f"Attempting to wait for element: {by}={value}")
            # Try direct find first to verify element exists
            direct_find = self.driver.find_elements(by, value)
            self.logger.debug(f"Direct find returned {len(direct_find)} elements")
            
            if len(direct_find) > 0:
                self.logger.debug("Element found directly without waiting")
                return direct_find[0]
                
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            self.logger.debug("Element found through wait_for_element")
            return element
        except Exception:
            self.logger.error(f"Element not found: {by}={value}")
            # self.logger.error(f"Current URL: {self.driver.current_url}")
            # self.logger.error(f"Page source snippet: {self.driver.page_source[:500]}")
            raise

    @staticmethod
    def random_delay(min_sec: float = 1.0, max_sec: float = 3.0):
        """Add random delay between actions"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def quit(self):
        if self.driver:
            self.logger.info("Closing browser")
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        self.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception as e:
            self.logger.error(f"Element not clickable: {by}={value}, {str(e)}")
            raise

    def safe_click(self, element):
        """Attempt to click with retries and waits"""
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                # Try regular click first
                element.click()
                return
            except Exception as e:
                if attempt == max_attempts - 1:  # Last attempt
                    # Try JavaScript click as last resort
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                        return
                    except Exception as js_e:
                        self.logger.error(f"Both regular and JS clicks failed: {str(e)}, {str(js_e)}")
                        raise
                self.random_delay(0.2, 0.5)  # Short delay between attempts

    def inject_html(self, html_content: str):
        """Safely inject HTML content into the page for testing"""
        self.driver.get("about:blank")
        # Escape any script-breaking characters
        safe_html = html_content.replace("`", "\\`").replace("$", "\\$")
        self.driver.execute_script(f"document.write(`{safe_html}`)")
        self.driver.execute_script("document.close()")

    def check_for_captcha(self):
        """Check if the current URL indicates a CAPTCHA challenge."""
        if self.driver and "validate.perfdrive.com" in self.driver.current_url:
            message = "CAPTCHA challenge identified. Please attend to it."
            self.logger.warning(message)
            print(message)
            return True
        return False