import logging
from typing import Optional, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from .models import FeedItem, Location, PropertySpecs
from .selectors import *

logger = logging.getLogger(__name__)

class FeedParser:
    def parse_item(self, element: WebElement) -> Optional[FeedItem]:
        try:
            link = element.find_element(By.CSS_SELECTOR, ITEM_LINK)
            url = link.get_attribute('href').split('?')[0]
            item_id = url.split('/item/')[1].split('?')[0]

            return FeedItem(
                item_id=item_id,
                url=url,
                price=self._extract_price(element),
                location=self._extract_location(element),
                specs=self._extract_specs(element),
                is_saved=self._is_saved(element),
                is_agency=self._is_agency(element),
                agency_name=self._extract_agency_name(element),
                tags=self._extract_tags(element)
            )
        except Exception as e:
            logger.error(f"Failed to parse feed item: {str(e)}")
            return None

    def _extract_price(self, element: WebElement) -> Optional[int]:
        try:
            price_elem = element.find_element(By.CSS_SELECTOR, PRICE_CONTAINER)
            price_text = price_elem.text.replace('₪', '').replace(',', '').strip()
            return int(price_text)
        except Exception as e:
            logger.warning(f"Could not parse price value from element: {str(e)}")
            return None

    def _extract_location(self, element: WebElement) -> Location:
        try:
            street = element.find_element(By.CSS_SELECTOR, STREET_NAME).text.strip()
            location_info = element.find_element(By.CSS_SELECTOR, LOCATION_INFO).text
            parts = [p.strip() for p in location_info.split(',')]
        except Exception as e:
            logger.error(f"Failed to extract location data: {str(e)}")
            raise
        
        return Location(
            street=street,
            city=parts[-1],
            neighborhood=parts[-2] if len(parts) > 2 else None,
            area=parts[-3] if len(parts) > 3 else None
        )

    def _extract_specs(self, element: WebElement) -> PropertySpecs:
        try:
            specs_text = element.find_element(By.CSS_SELECTOR, PROPERTY_SPECS).text
            parts = specs_text.split('•')
            
            rooms = float(parts[0].split()[0]) if len(parts) > 0 else None
            floor = int(parts[1].split()[1]) if len(parts) > 1 else None
            size = int(parts[2].split()[0]) if len(parts) > 2 else None
            
            return PropertySpecs(rooms=rooms, floor=floor, size_sqm=size)
        except Exception as e:
            logger.warning(f"Failed to extract specs: {str(e)}")
            return PropertySpecs(rooms=None, floor=None, size_sqm=None)

    def _is_saved(self, element: WebElement) -> bool:
        try:
            # Find button div
            save_button = element.find_element(By.CSS_SELECTOR, "[data-testid='like-button']")
            # Get first div child
            icon_div = save_button.find_element(By.CSS_SELECTOR, "div")
            # Check number of classes - saved has 1, unsaved has 2
            classes = icon_div.get_attribute('class').split()
            return len(classes) == 1
        except Exception as e:
            return False

    def _is_agency(self, element: WebElement) -> bool:
        try:
            element.find_element(By.CSS_SELECTOR, AGENCY_CONTAINER)
            return True
        except Exception:
            return False

    def _extract_agency_name(self, element: WebElement) -> Optional[str]:
        if not self._is_agency(element):
            return None
        try:
            name = element.find_element(By.CSS_SELECTOR, AGENCY_NAME).text.strip()
            if not name:
                logger.warning("Agency listing found but name is empty")
            return name
        except Exception:
            logger.warning("Agency listing found but failed to extract name")
            return None

    def _extract_tags(self, element: WebElement) -> List[str]:
        try:
            tags_container = element.find_element(By.CSS_SELECTOR, TAGS_CONTAINER)
            return [tag.text.strip() for tag in tags_container.find_elements(By.TAG_NAME, 'span')]
        except Exception:
            return []
