import logging
from typing import List

from dotenv import load_dotenv

from src.mail_sender.sender import EmailSender

from .auth import Yad2Auth
from .browser import Browser
from .feed_handler import FeedHandler
from .feed_parser import FeedParser
from .item_enricher import ItemEnricher
from .models import FeedItem
from .navigation import NavigationHandler
from .pagination import PaginationHandler


class Yad2Client:
    BASE_URL = "https://www.yad2.co.il"
    REALESTATE_URL = f"{BASE_URL}/realestate/forsale"

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
        self.pagination = PaginationHandler(self.browser)
        self.feed_handler = FeedHandler(self.browser, self.parser)
        self.email_sender = EmailSender()
        self.logger = logging.getLogger(__name__)
        
        self.login()

    def navigate_to(self, url: str) -> bool:
        return self.navigation.navigate_to(url)

    def get_feed_items(self) -> List[FeedItem]:
        """Get feed items from all available pages."""
        all_items = []
        current_url = self.browser.driver.current_url
        MAX_PAGES = 10
        
        try:
            # Get items from first page
            print("Processing page 1...")
            first_page_items = self.feed_handler.get_current_page_items()
            all_items.extend(first_page_items)
            
            # Check for additional pages
            total_pages = min(self.pagination.get_total_pages(), MAX_PAGES)
            if total_pages > 1:
                if total_pages == MAX_PAGES:
                    print(f"Found more than {MAX_PAGES} pages, limiting to first {MAX_PAGES}...")
                else:
                    print(f"Found {total_pages} pages, processing remaining pages...")
                
                for page in range(2, total_pages + 1):
                    print(f"Processing page {page}/{total_pages}...")
                    next_page_url = self.pagination.modify_url_for_page(current_url, page)
                    
                    # Add random delay between page navigations
                    self.browser.random_delay(3.0, 5.0)
                    
                    if not self.navigate_to(next_page_url):
                        self.logger.warning(f"Failed to load page {page}, stopping pagination")
                        break
                    
                    # Check for captcha after each navigation
                    if self.browser.has_captcha():
                        self.logger.warning("Captcha detected, stopping pagination")
                        print("\nCaptcha detected! Stopping to prevent blocking...")
                        break
                    
                    page_items = self.feed_handler.get_current_page_items()
                    all_items.extend(page_items)
            
            print(f"\nFound {len(all_items)} items total")
            return all_items
            
        except Exception as e:
            self.logger.error(f"Error while getting feed items: {str(e)}")
            print(f"Error while getting feed items: {str(e)}")
            return all_items

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
