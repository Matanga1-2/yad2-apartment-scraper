import logging
import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from src.yad2.item_enricher import ItemEnricher
from src.yad2.models import FeedItem, PropertySpecs, PropertyFeatures, Location
from src.yad2.browser import Browser
import urllib.parse

# Reuse the existing logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

# Reuse the existing driver fixture
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def sample_listing_html():
    fixtures_dir = Path(__file__).parent / "fixtures"
    with open(fixtures_dir / "sample_listing.html", "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def sample_feed_item():
    return FeedItem(
        item_id="123",
        url="https://www.yad2.co.il/item/123",
        price=1000000,
        location=Location(
            city="תל אביב",
            street="דיזנגוף",
            neighborhood="לב העיר"
        ),
        specs=PropertySpecs(
            rooms=3,
            floor=2,
            size_sqm=80,
            features=PropertyFeatures()
        ),
        is_agency=False,
        is_saved=False
    )

@pytest.fixture
def browser(driver):
    """Create a Browser instance for testing."""
    browser = Browser(headless=True)
    # Instead of initializing a new driver, use the one from the driver fixture
    browser.driver = driver
    yield browser
    # The driver cleanup is handled by the driver fixture

def test_extract_floor_info(browser, sample_listing_html, sample_feed_item):
    logger.info("Testing floor info extraction")
    
    # Use execute_script approach to load HTML
    browser.driver.get("about:blank")
    browser.driver.execute_script(f"document.write(`{sample_listing_html}`)")
    browser.driver.execute_script("document.close()")
    
    enricher = ItemEnricher(browser)
    enricher._extract_floor_info(sample_feed_item)
    
    assert sample_feed_item.specs.features.current_floor == 3
    assert sample_feed_item.specs.features.total_floors == 4
    
    logger.info("Floor info extraction test completed successfully")

def test_extract_features(browser, sample_listing_html, sample_feed_item):
    logger.info("Testing features extraction")
    
    # Use a more reliable way to load the HTML
    browser.driver.get("about:blank")
    browser.driver.execute_script(f"document.write(`{sample_listing_html}`)")
    browser.driver.execute_script("document.close()")
    
    enricher = ItemEnricher(browser)
    enricher._extract_features(sample_feed_item)
    
    assert sample_feed_item.specs.features.has_balcony is True
    assert sample_feed_item.specs.features.has_storage is True
    assert sample_feed_item.specs.features.has_mamad is True
    assert sample_feed_item.specs.features.has_elevator is False
    
    logger.info("Features extraction test completed successfully")

def test_extract_parking_info(browser, sample_listing_html, sample_feed_item):
    logger.info("Testing parking info extraction")
    
    # Use execute_script approach to load HTML
    browser.driver.get("about:blank")
    browser.driver.execute_script(f"document.write(`{sample_listing_html}`)")
    browser.driver.execute_script("document.close()")
    
    enricher = ItemEnricher(browser)
    enricher._extract_parking_info(sample_feed_item)
    
    assert sample_feed_item.specs.features.has_parking is True
    
    logger.info("Parking info extraction test completed successfully")

def test_extract_contact_info(browser, sample_listing_html, sample_feed_item):
    logger.info("Testing contact info extraction")
    
    # Use execute_script approach to load HTML
    browser.driver.get("about:blank")
    browser.driver.execute_script(f"document.write(`{sample_listing_html}`)")
    browser.driver.execute_script("document.close()")
    
    enricher = ItemEnricher(browser)
    enricher._extract_contact_info(sample_feed_item)
    
    assert sample_feed_item.contact is not None
    assert sample_feed_item.contact.name == "איש"
    assert sample_feed_item.contact.phone == "054-123123123"
    
    logger.info("Contact info extraction test completed successfully")



def main():
    # Create Browser instance with headless mode
    browser = Browser(headless=True)
    browser.init_driver()  # Initialize the driver
    
    # Load sample listing
    with open(Path(__file__).parent / "fixtures" / "sample_listing.html", "r", encoding="utf-8") as f:
        sample_listing_html = f.read()
    
    # Create sample feed item with all required arguments
    sample_feed_item = FeedItem(
        item_id="123",
        url="https://www.yad2.co.il/item/123",
        price=1000000,
        location=Location(
            city="תל אביב",
            street="דיזנגוף",
            neighborhood="לב העיר"
        ),
        specs=PropertySpecs(
            rooms=3,
            floor=2,
            size_sqm=80,
            features=PropertyFeatures()
        ),
        is_agency=False,
        is_saved=False
    )
    
    try:
        test_extract_floor_info(browser, sample_listing_html, sample_feed_item)
        test_extract_features(browser, sample_listing_html, sample_feed_item)
        test_extract_parking_info(browser, sample_listing_html, sample_feed_item)
        test_extract_contact_info(browser, sample_listing_html, sample_feed_item)
    finally:
        browser.quit()  # Use Browser's quit method

if __name__ == "__main__":
    main()
