import logging

from selenium.webdriver.common.by import By

from .browser import Browser


class Yad2Client:
    BASE_URL = "https://www.yad2.co.il"
    REALESTATE_URL = f"{BASE_URL}/realestate/forsale"
    FEED_SELECTOR = "feed-list_feed_oXbRw"
    ITEM_SELECTOR = "feed-item-list-box"

    def __init__(self, headless: bool = True):
        self.browser = Browser(headless=headless)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
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

            self.browser.wait_for_element(By.CSS_SELECTOR, "[class^='map-page-layout_searchBox']")

            if self.browser.has_captcha():
                self.logger.warning("Post-wait captcha check failed")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to open search page: {str(e)}")
            return False

    def get_feed_items(self):
        try:
            # Wait for dynamic content
            self.browser.random_delay(2.0, 4.0)

            # Debug page structure
            self.logger.info("Analyzing page structure...")
            feed_items = self.browser.driver.find_elements(By.CSS_SELECTOR, "[class^='feed-list_feed_']")
            self.logger.info(f"Feed container elements found: {len(feed_items)}")

            if not feed_items:
                # Log all available classes for debugging
                all_elements = self.browser.driver.find_elements(By.CSS_SELECTOR, "*")
                classes = set()
                for elem in all_elements:
                    class_name = elem.get_attribute('class')
                    if class_name and 'feed' in class_name.lower():
                        classes.add(class_name)
                self.logger.info(f"Available feed-related classes: {classes}")
                return []

            self.logger.info(f"Feed container classes: {feed_items[0].get_attribute('class')}")

            # Try direct selector based on list items
            feed_items = feed_items[0].find_elements(By.CSS_SELECTOR, "li[data-nagish='feed-item-list-box']")
            self.logger.info(f"Found {len(feed_items)} feed items")

            for idx, item in enumerate(feed_items, 1):
                href = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                item_id = href.split('/item/')[1].split('?')[0]
                self.logger.info(f"Item {idx}: ID={item_id}, URL={href}")

            return feed_items

            self.logger.info(f"Found {len(feed_items)} feed items")
            if feed_items:
                self.logger.info(f"Sample item classes: {feed_items[0].get_attribute('class')}")

            return feed_items

        except Exception as e:
            self.logger.error(f"Failed to get feed items: {str(e)}")
            return []

    def close(self):
        self.browser.quit()

    def __enter__(self):
        self.browser.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()