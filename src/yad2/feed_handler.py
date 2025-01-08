import logging
from typing import List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .browser import Browser
from .feed_parser import FeedParser
from .models import FeedItem
from .saved_feed_parser import SavedFeedParser
from .selectors import FEED_CONTAINER, FEED_ITEM, SAVED_ITEMS_CONTAINER, SAVED_ITEM


class FeedHandler:
    def __init__(self, browser: Browser, parser: FeedParser):
        self.browser = browser
        self.parser = parser
        self.saved_parser = SavedFeedParser()
        self.logger = logging.getLogger(__name__)

    def get_current_page_items(self) -> List[FeedItem] | List[Tuple[str, str]]:
        """
        Get items from the current page.
        Returns either List[FeedItem] for regular feed or List[Tuple[str, str]] for saved items.
        """
        try:
            if self.browser.check_for_captcha():
                input("Press Enter once you've completed the CAPTCHA...")
            
            # Try to find saved items container first
            try:
                container = self.browser.wait_for_element(By.CSS_SELECTOR, SAVED_ITEMS_CONTAINER, timeout=2)
                return self._get_saved_items(container)
            except Exception:
                # If not found, try regular feed container
                container = self.browser.wait_for_element(By.CSS_SELECTOR, FEED_CONTAINER)
                return self._get_regular_items(container)
            
        except Exception as e:
            self.logger.error(f"Failed to get items from current page: {str(e)}")
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
            if 'yad1-listing' not in item.get_attribute('data-testid')
        ]
        
        parsed_items = []
        for item in feed_items:
            parsed_item = self.parser.parse_item(item)
            if parsed_item:
                parsed_items.append(parsed_item)
                
        return parsed_items 