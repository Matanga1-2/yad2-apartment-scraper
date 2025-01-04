import logging

from selenium.webdriver.common.by import By

from .browser import Browser
from .models import Contact, FeedItem


class ItemEnricher:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.logger = logging.getLogger(__name__)

    def enrich_item(self, item: FeedItem) -> FeedItem:
        """
        Enriches a FeedItem with additional information from the listing page.
        Opens the item in a new tab and closes it when done.
        """
        # Store the current window handle (main listing page)
        main_window = self.browser.driver.current_window_handle
        
        try:
            # Open new tab and switch to it
            try:
                self.browser.driver.switch_to.new_window('tab')
            except Exception as e:
                self.logger.error(f"Failed to open new tab for item {item.url}: {str(e)}")
                return item
            
            self.browser.driver.get(item.url)
            
            self._extract_floor_info(item)
            self._extract_features(item)
            self._extract_parking_info(item)
            
            if not item.is_agency:
                self._extract_contact_info(item)

            return item

        except Exception as e:
            self.logger.error(f"Failed to enrich item {item.url}: {str(e)}")
            return item
        
        finally:
            # Close the new tab and switch back to main window
            if len(self.browser.driver.window_handles) > 1:
                self.browser.driver.close()
            self.browser.driver.switch_to.window(main_window)

    def _extract_floor_info(self, item: FeedItem):
        try:
            # First find the floor section by looking for the text "קומה"
            floor_section = self.browser.wait_for_element(
                By.XPATH,
                "//span[contains(@class, 'building-item_details')]/span[text()='קומה']/parent::span"
            )
            
            # Then get the value element within that section
            floor_element = floor_section.find_element(
                By.CSS_SELECTOR,
                "span[class*='building-item_itemValue']"
            )
            
            if floor_element:
                floor_text = floor_element.text  # Should now get "3/4"
                if not floor_text or '/' not in floor_text:
                    self.logger.warning(f"Invalid floor format '{floor_text}' for item {item.url}")
                    return
                current_floor, total_floors = map(int, floor_text.split('/'))
                item.specs.features.current_floor = current_floor
                item.specs.features.total_floors = total_floors
        except Exception as e:
            self.logger.error(
                f"Failed to extract floor info for item {item.url}: {str(e)}",
                exc_info=True
            )
            pass

    def _extract_features(self, item: FeedItem):
        try:
            features_section = self.browser.wait_for_element(
                By.XPATH,
                "//section[@data-testid='in-property']"
            )
            feature_items = features_section.find_elements(By.CSS_SELECTOR, '[data-testid="in-property-item"]')
            
            if not feature_items:
                self.logger.warning(f"No features found for item {item.url}")
            
            feature_map = {
                "מעלית": "has_elevator",
                'ממ"ד': "has_mamad", 
                "מרפסת": "has_balcony",
                "מחסן": "has_storage"
            }

            for feature in feature_items:
                self.logger.debug(f"Feature HTML content: {feature.get_attribute('outerHTML')}")
                is_disabled = 'in-property-item_disabled' in feature.get_attribute('class')
                feature_text = feature.find_element(By.CSS_SELECTOR, "span[class*='in-property-item_text']").text
                
                if not is_disabled:
                    if feature_text in feature_map:
                        setattr(item.specs.features, feature_map[feature_text], True)
        except Exception as e:
            self.logger.error(
                f"Failed to extract features for item {item.url}: {str(e)}",
                exc_info=True
            )
            pass

    def _extract_parking_info(self, item: FeedItem):
        try:
            parking_label = self.browser.driver.find_element(By.XPATH, "//dd[text()='חניות']")
            parking_value = parking_label.find_element(By.XPATH, "following-sibling::dt")
            if parking_value and int(parking_value.text) > 0:
                item.specs.features.has_parking = True
        except Exception as e:
            self.logger.error(
                f"Failed to extract parking info for item {item.url}: {str(e)}",
                exc_info=True
            )
            pass

    def _extract_contact_info(self, item: FeedItem):
        try:
            contact_button = self.browser.wait_for_clickable(
                By.CSS_SELECTOR, 
                '[data-testid="show-details-button"]'
            )
            self.browser.safe_click(contact_button)
            
            contact_info = self.browser.wait_for_element(
                By.CSS_SELECTOR, 
                '[data-testid="opened-contact-info"]'
            )
            
            name = contact_info.find_element(By.CSS_SELECTOR, "span[class*='private-contact-info_name']").text
            phone = contact_info.find_element(By.CSS_SELECTOR, "span[class*='phone-number-link_phoneNumberText']").text
            
            item.contact = Contact(name=name, phone=phone)
        except Exception as e:
            self.logger.error(
                f"Failed to extract contact info - Name: {name if 'name' in locals() else 'N/A'}, "
                f"Phone: {phone if 'phone' in locals() else 'N/A'} - Error: {str(e)}"
            )
            pass 