import logging
import re
from typing import List, Tuple

from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from src.mail_sender.sender import EmailSender

from .auth import Yad2Auth
from .browser import Browser
from .feed_handler import FeedHandler
from .feed_parser import FeedParser
from .item_enricher import ItemEnricher
from .models import FeedItem
from .navigation import NavigationHandler


class Yad2Client:
    BASE_URL = "https://www.yad2.co.il"
    REALESTATE_URL = f"{BASE_URL}/realestate/forsale"
    SAVED_ITEMS_URL = f"{BASE_URL}/my-favorites"

    def __init__(self, headless: bool = True):
        load_dotenv()
        self.browser = Browser(headless=headless)
        self.browser.init_driver()
        
        if not self.browser.driver:
            raise RuntimeError("Browser initialization failed")

        self.parser = FeedParser()
        self.auth = Yad2Auth(self.browser)
        self.enricher = ItemEnricher(self.browser)
        self.navigation = NavigationHandler(self.browser)
        self.feed_handler = FeedHandler(self.browser, self.parser)
        self.email_sender = EmailSender()
        self.logger = logging.getLogger(__name__)
        
        self.login()

    def navigate_to(self, url: str) -> bool:
        success = self.navigation.navigate_to(url)
        
        # Check for CAPTCHA after navigation
        if self.browser.check_for_captcha():
            input("Press Enter once you've completed the CAPTCHA...")
        
        return success

    def _deduplicate_items(self, items: List[FeedItem]) -> List[FeedItem]:
        """Remove duplicate items based on URL while preserving order."""
        seen_urls = set()
        unique_items = []
        
        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        duplicates_count = len(items) - len(unique_items)
        if duplicates_count > 0:
            self.logger.info(f"Removed {duplicates_count} duplicate items")
        
        return unique_items

    def get_feed_items(self) -> List[FeedItem] |List[Tuple[str, str]]:
        """
        Get feed items from current page.
        Returns either List[FeedItem] for regular feed or List[Tuple[str, str]] for saved items.
        """
        try:
            # Check for CAPTCHA before getting items
            if self.browser.check_for_captcha():
                input("Press Enter once you've completed the CAPTCHA...")
            
            # Get and deduplicate items
            items = self.feed_handler.get_current_page_items()
            
            # If items are tuples, they're from saved items page
            if items and isinstance(items[0], tuple):
                return items
                
            # Otherwise they're regular feed items that need deduplication
            return self._deduplicate_items(items)
            
        except Exception as e:
            self.logger.error(f"Error while getting feed items: {str(e)}")
            print(f"Error while getting feed items: {str(e)}")
            return []

    def _get_total_pages(self) -> int:
        """Get total number of pages from pagination element."""
        try:
            # Check if pagination exists - updated selector
            nav = self.browser.wait_for_element(
                By.CSS_SELECTOR, 
                'nav[class*="pagination-wrapper_pagination"]',
                timeout=5
            )
            
            if not nav:
                self.logger.info("No pagination found, assuming single page")
                return 1

            # Updated selector for the text element
            pagination_text = self.browser.wait_for_element(
                By.CSS_SELECTOR, 
                'span[class*="pagination-wrapper_textVariant"]',
                timeout=5
            )
            
            if pagination_text:
                text_content = pagination_text.get_attribute('textContent')
                match = re.search(r'מתוך (\d+)', text_content)
                if match:
                    total_pages = int(match.group(1))
                    self.logger.info(f"Found {total_pages} total pages")
                    return total_pages
            
            # Alternative method: count the number of page links
            page_links = self.browser.driver.find_elements(
                By.CSS_SELECTOR,
                'ol[class*="list_list"] a[class*="item_item"]'
            )
            if page_links:
                total_pages = len(page_links)
                self.logger.info(f"Found {total_pages} total pages from page links")
                return total_pages
            
            self.logger.info("No pagination text found, assuming single page")
            return 1
            
        except Exception as e:
            self.logger.warning(f"Failed to get total pages: {str(e)}")
            return 1

    def close(self):
        self.browser.quit()

    def __enter__(self):
        self.browser.init_driver()
        return self

    def __exit__(self, *_):
        self.close()

    def login(self) -> bool:
        return self.auth.login()

    def enrich_feed_item(self, item: FeedItem) -> FeedItem:
        """
        Enriches a FeedItem with additional information from the listing page.
        Opens the item in a new tab and closes it when done.
        """
        return self.enricher.enrich_item(item)
    

    def send_feed_item(self, item: FeedItem) -> None:
        """
        Sends an email notification for a feed item.
        
        Args:
            item: The FeedItem to send
            
        Raises:
            Exception: If email sending fails
        """
        if not item or not item.url:
            self.logger.error("Attempting to send invalid feed item")
            raise ValueError("Invalid feed item")
        try:
            title = item.format_listing()
            body = f"{item.url}"
            
            self.email_sender.send_email(subject=title, body=body)
            self.logger.info(f"Successfully sent email notification for item {item.item_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email for item {item.item_id}: {str(e)}")
            raise

    def save_ad(self, item: FeedItem) -> bool:
        """
        Attempts to save/like a specific feed item by clicking its save button.
        
        Args:
            item: The FeedItem to save
            
        Returns:
            bool: True if the save operation was successful, False otherwise
        """
        if not item or not item.item_id:
            self.logger.error("Attempting to save invalid feed item")
            return False
        
        try:
            # Execute JavaScript to find and click the button for this specific item
            success = self.browser.driver.execute_script("""
                // Find the feed item by its base URL (without query params)
                const itemId = arguments[0];
                const itemLink = document.querySelector(`a[href*="/realestate/item/${itemId}"]`);
                if (!itemLink) return false;
                
                // Find the like button within this item's container
                const itemContainer = itemLink.closest('div[class*="card_cardBox"]');
                if (!itemContainer) return false;
                
                const likeButton = itemContainer.querySelector('[data-testid="like-button"]');
                if (!likeButton) return false;
                
                likeButton.click();
                return true;
            """, item.item_id)
            
            if success:
                self.logger.info(f"Successfully saved item {item.item_id}")
                print("Saved ad")
                return True
            else:
                self.logger.warning(f"Could not find save button for item {item.item_id}")
                print("Error saving ad!")
                return False
            
        except Exception as e:
            self.logger.error(f"Error while trying to save item {item.item_id}: {str(e)}")
            print("Error saving ad!")
            return False

    def navigate_to_saved_items(self) -> bool:
        """Navigate to the saved items page."""
        return self.navigate_to(self.SAVED_ITEMS_URL)
