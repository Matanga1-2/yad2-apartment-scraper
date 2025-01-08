import logging
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from .browser import Browser
from .selectors import FEED_CONTAINER, SAVED_ITEMS_CONTAINER


class NavigationHandler:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.logger = logging.getLogger(__name__)

    def navigate_to(self, url: str) -> bool:
        """Navigate to URL and verify page load."""
        try:
            self.logger.info(f"Accessing {url}")
            print("Opening URL...")
            self.browser.driver.get(url)
            
            if "my-favorites" in url:
                return self._handle_saved_items_page()
            else:
                return self._handle_feed_page()

        except Exception as e:
            self.logger.error(f"Failed to navigate to URL: {str(e)}")
            print(f"Failed to navigate to URL: {str(e)}")
            self._log_debug_info()
            return False

    def _handle_saved_items_page(self) -> bool:
        """Handle navigation to saved items page."""
        try:
            container = self.browser.wait_for_element(
                By.CSS_SELECTOR, 
                SAVED_ITEMS_CONTAINER, 
                timeout=30
            )
            if container:
                print("Page loaded successfully!")
                self.logger.info("Saved items page loaded successfully")
                return True
            return False
        except TimeoutException:
            self.logger.error("Timeout waiting for saved items container")
            self._log_debug_info()
            return False

    def _handle_feed_page(self) -> bool:
        """Handle navigation to regular feed page."""
        try:
            # Wait for feed container
            if not self.browser.wait_for_element(By.CSS_SELECTOR, FEED_CONTAINER, timeout=30):
                self.logger.error("Feed container not found")
                return False

            # Wait for favorites badge
            print("Waiting for favorites badge...")
            self.logger.info("Waiting for favorites badge to load...")
            
            favorites_badge = self.browser.wait_for_element(
                By.CSS_SELECTOR,
                'div[data-testid="favorites-dropdown-menu"] span[data-testid="badge"]',
                timeout=300
            )
            
            if favorites_badge and favorites_badge.is_displayed():
                print("Page loaded successfully!")
                self.logger.info("Feed page loaded successfully")
                return True
            
            self.logger.warning("Favorites badge not found or not visible")
            return False

        except TimeoutException:
            self.logger.error("Timeout waiting for feed page elements")
            self._log_debug_info()
            return False

    def _log_debug_info(self) -> None:
        """Log debug information when navigation fails."""
        if self.browser and self.browser.driver:
            self.logger.error(f"Current URL: {self.browser.driver.current_url}")
            self.logger.error(f"Page source snippet: {self.browser.driver.page_source[:1000]}") 