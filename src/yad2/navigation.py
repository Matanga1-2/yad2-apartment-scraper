import logging

from selenium.webdriver.common.by import By

from .browser import Browser
from .selectors import FEED_CONTAINER


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
            
            self.browser.wait_for_element(By.CSS_SELECTOR, FEED_CONTAINER, timeout=30)
            
            print("Waiting for favorites badge...")
            self.logger.info("Waiting for favorites badge to load...")
            
            favorites_badge = self.browser.wait_for_element(
                By.CSS_SELECTOR,
                'div[data-testid="favorites-dropdown-menu"] span[data-testid="badge"]',
                timeout=30
            )
            
            if favorites_badge and favorites_badge.is_displayed():
                print("Page loaded successfully!")
                self.logger.info("Page loaded successfully - favorites badge found")
                return True
            
            self.logger.warning("Favorites badge not found or not visible")
            return False

        except Exception as e:
            self.logger.error(f"Failed to navigate to URL: {str(e)}")
            print(f"Failed to navigate to URL: {str(e)}")
            return False 