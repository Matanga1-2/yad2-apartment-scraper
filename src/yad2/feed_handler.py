import logging
from typing import List

from selenium.webdriver.common.by import By

from .browser import Browser
from .feed_parser import FeedParser
from .models import FeedItem
from .selectors import FEED_CONTAINER, FEED_ITEM


class FeedHandler:
    def __init__(self, browser: Browser, parser: FeedParser):
        self.browser = browser
        self.parser = parser
        self.logger = logging.getLogger(__name__)

    def get_current_page_items(self) -> List[FeedItem]:
        """Get feed items from the current page."""
        try:
            # Check for CAPTCHA before getting items
            if self.browser.check_for_captcha():
                input("Press Enter once you've completed the CAPTCHA...")
            
            feed_container = self.browser.driver.find_element(By.CSS_SELECTOR, FEED_CONTAINER)
            feed_items = [
                item for item in feed_container.find_elements(By.CSS_SELECTOR, FEED_ITEM)
                if 'yad1-listing' not in item.get_attribute('data-testid')
            ]
            
            self.logger.info(f"Found {len(feed_items)} valid feed items on current page")
            
            parsed_items = []
            for item in feed_items:
                parsed_item = self.parser.parse_item(item)
                if parsed_item:
                    parsed_items.append(parsed_item)
                    self.logger.debug(f"Successfully parsed item {parsed_item.item_id}")
            
            return parsed_items

        except Exception as e:
            self.logger.error(f"Failed to get items from current page: {str(e)}")
            return [] 