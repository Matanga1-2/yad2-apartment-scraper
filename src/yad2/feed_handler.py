import logging
from typing import List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .browser import Browser
from .feed_parser import FeedParser
from .models import FeedItem
from .saved_feed_parser import SavedFeedParser
from .selectors import FEED_CONTAINER, FEED_ITEM, SAVED_ITEM, SAVED_ITEMS_CONTAINER


class FeedHandler:
    def __init__(self, browser: Browser, parser: FeedParser):
        self.browser = browser
        self.parser = parser
        self.saved_parser = SavedFeedParser()
        self.logger = logging.getLogger(__name__)

    def get_saved_items(self) -> List[Tuple[str, str]]:
        """Get items from the saved items page."""
        try:
            if self.browser.check_for_captcha():
                input("Press Enter once you've completed the CAPTCHA...")
            
            container = self.browser.wait_for_element(By.CSS_SELECTOR, SAVED_ITEMS_CONTAINER)
            return self._get_saved_items(container)
            
        except Exception as e:
            self.logger.error(f"Failed to get saved items: {str(e)}")
            return []

    def get_feed_items(self) -> List[FeedItem]:
        """Get items from the regular feed page."""
        try:
            if self.browser.check_for_captcha():
                input("Press Enter once you've completed the CAPTCHA...")
            
            container = self.browser.wait_for_element(By.CSS_SELECTOR, FEED_CONTAINER)
            return self._get_regular_items(container)
            
        except Exception as e:
            self.logger.error(f"Failed to get feed items: {str(e)}")
            return []

    def _get_saved_items(self, container: WebElement) -> List[Tuple[str, str]]:
        """Parse items from saved items page, returning list of (item_id, url) tuples."""
        saved_items = container.find_elements(By.CSS_SELECTOR, SAVED_ITEM)
        
        parsed_items = []
        for item in saved_items:
            parsed_item = self.saved_parser.parse_item(item)
            if parsed_item:
                parsed_items.append(parsed_item)
                
        return parsed_items

    def _get_regular_items(self, container: WebElement) -> List[FeedItem]:
        """Parse items from regular feed page."""
        feed_items = [
            item for item in container.find_elements(By.CSS_SELECTOR, FEED_ITEM)
            if not item.get_attribute('data-testid') or 'yad1-listing' not in item.get_attribute('data-testid')
        ]
        
        parsed_items = []
        for item in feed_items:
            parsed_item = self.parser.parse_item(item)
            if parsed_item:
                parsed_items.append(parsed_item)
                
        return parsed_items 