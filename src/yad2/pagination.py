import logging
import re
from urllib.parse import parse_qs, urlencode, urlparse

from selenium.webdriver.common.by import By

from .browser import Browser
from .selectors import PAGINATION_NAV, PAGINATION_TEXT


class PaginationHandler:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.logger = logging.getLogger(__name__)

    def get_total_pages(self) -> int:
        """Get total number of pages from pagination element."""
        try:
            # First check if pagination exists
            nav = self.browser.wait_for_element(
                By.CSS_SELECTOR, 
                PAGINATION_NAV,
                timeout=5
            )
            
            if not nav:
                self.logger.info("No pagination found, assuming single page")
                return 1

            pagination_text = self.browser.wait_for_element(
                By.CSS_SELECTOR, 
                PAGINATION_TEXT,
                timeout=5
            )
            
            if pagination_text:
                # Get text using textContent attribute instead of .text
                text_content = pagination_text.get_attribute('textContent')
                
                match = re.search(r'מתוך (\d+)', text_content)
                if match:
                    total_pages = int(match.group(1))
                    self.logger.info(f"Found {total_pages} total pages")
                    return total_pages
            
            self.logger.info("No pagination text found, assuming single page")
            return 1
            
        except Exception as e:
            self.logger.warning(f"Failed to get total pages: {str(e)}")
            return 1

    def modify_url_for_page(self, url: str, page: int) -> str:
        """Modify URL to include or update page parameter."""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['page'] = [str(page)]
        new_query = urlencode(query_params, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}" 