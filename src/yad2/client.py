import logging
from typing import List
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

from .browser import Browser
from .feed_parser import FeedParser
from .models import FeedItem, Contact
from .selectors import FEED_CONTAINER, FEED_ITEM
from .auth import Yad2Auth
from .item_enricher import ItemEnricher
from src.email.sender import EmailSender

class Yad2Client:
    BASE_URL = "https://www.yad2.co.il"
    REALESTATE_URL = f"{BASE_URL}/realestate/forsale"

    def __init__(self, headless: bool = True):
        load_dotenv()  # Load environment variables from .env file
        self.browser = Browser(headless=headless)
        self.browser.init_driver()  # Initialize the driver here
        self.parser = FeedParser()
        self.auth = Yad2Auth(self.browser)
        self.enricher = ItemEnricher(self.browser)
        self.login()
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self.email_sender = EmailSender()

    def _setup_logging(self):
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            handlers = [
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            for handler in handlers:
                handler.setFormatter(formatter)
                handler.setLevel(logging.INFO)
                self.logger.addHandler(handler)

    def open_search_page(self, timeout: int = 60) -> bool:
        try:
            self.logger.info(f"Accessing {self.REALESTATE_URL}")
            self.browser.driver.get(self.REALESTATE_URL)

            if self.browser.has_captcha():
                self.logger.warning("Initial captcha check failed")
                return False

            self.browser.wait_for_element(By.CSS_SELECTOR, "[class^='map-page-layout_searchBox']", timeout=timeout)

            if self.browser.has_captcha():
                self.logger.warning("Post-wait captcha check failed")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to open search page: {str(e)}")
            return False

    def get_feed_items(self, url: str) -> List[FeedItem]:
        try:
            # Ensure browser is initialized
            if not self.browser.driver:
                self.browser.init_driver()
            
            # Navigate to the provided URL
            self.logger.info(f"Accessing {url}")
            self.browser.driver.get(url)
            
            # Wait for the feed container to be present and visible
            self.browser.wait_for_element(By.CSS_SELECTOR, FEED_CONTAINER, timeout=30)
            self.browser.random_delay(2.0, 4.0)
            
            # Check for captcha after loading
            if self.browser.has_captcha():
                self.logger.warning("Captcha detected while loading feed items")
                return []
            
            feed_container = self.browser.driver.find_element(By.CSS_SELECTOR, FEED_CONTAINER)
            # Filter out yad1 listings when getting feed items
            feed_items = [
                item for item in feed_container.find_elements(By.CSS_SELECTOR, FEED_ITEM)
                if 'yad1-listing' not in item.get_attribute('data-testid')
            ]
            
            self.logger.info(f"Found {len(feed_items)} valid feed items (excluding yad1 listings)")
            
            parsed_items = []
            for item in feed_items:
                parsed_item = self.parser.parse_item(item)
                if parsed_item:
                    parsed_items.append(parsed_item)
                    self.logger.debug(f"Successfully parsed item {parsed_item.item_id}")
            
            return parsed_items

        except Exception as e:
            self.logger.error(f"Failed to get feed items: {str(e)}")
            return []

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
    def save_feed_item(self, item: FeedItem) -> bool:
        """
        Saves a feed item by clicking the save button.
        Returns True if successful, False otherwise.
        """
        try:
            # More specific selector targeting the actual button
            button_selector = "button[data-testid='like-button']"
            
            # First wait for element to be present
            save_button = self.browser.wait_for_element(
                By.CSS_SELECTOR, 
                button_selector,
                timeout=10
            )
            
            # Scroll element into view
            self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            self.browser.random_delay(0.4, 0.7)  # Small delay after scroll
            
            # wait_for_clickable doesn't work, fallback to safe_click
            try:
                self.browser.safe_click(save_button)
            except Exception:
                self.logger.warning("Regular click failed, trying JavaScript click")
                self.browser.driver.execute_script("arguments[0].click();", save_button)
            
            self.browser.random_delay(1.0, 2.0)  # Wait for any animations
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save item {item.url}: {str(e)}")
            return False

    def send_feed_item(self, item: FeedItem) -> None:
        """
        Sends an email notification for a feed item.
        
        Args:
            item: The FeedItem to send
            
        Raises:
            Exception: If email sending fails
        """
        try:
            title = item.format_listing()
            body = f"{item.url}"
            
            self.email_sender.send_email(subject=title, body=body)
            self.logger.info(f"Successfully sent email notification for item {item.item_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email for item {item.item_id}: {str(e)}")
            raise
