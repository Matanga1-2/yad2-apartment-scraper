import logging
from typing import Optional, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .selectors import SAVED_ITEM_LINK


class SavedFeedParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_item(self, element: WebElement) -> Optional[Tuple[str, str]]:
        """
        Parse a saved item from the saved items page.
        Returns tuple of (item_id, url) if successful, None otherwise.
        """
        try:
            link = element.find_element(By.CSS_SELECTOR, SAVED_ITEM_LINK)
            url = link.get_attribute('href').split('?')[0]
            item_id = url.split('/item/')[1]
            
            return item_id, url

        except Exception as e:
            self.logger.error(f"Failed to parse saved item: {str(e)}")
            return None