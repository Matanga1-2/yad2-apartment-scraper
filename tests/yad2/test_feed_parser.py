import logging
import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from src.yad2.feed_parser import FeedParser

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def sample_feed_html():
    fixtures_dir = Path(__file__).parent / "fixtures"
    with open(fixtures_dir / "sample_feed.html", "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def parser():
    return FeedParser()

def test_parse_regular_listing(driver, sample_feed_html, parser):
    logger.info("Testing regular listing parsing")
    
    driver.get(f"data:text/html;charset=utf-8,{sample_feed_html}")
    feed_item = driver.find_element(By.CSS_SELECTOR, '[data-nagish="feed-item-list-box"]')
    
    result = parser.parse_item(feed_item)
    
    assert result is not None
    assert result.item_id == "123456"
    assert result.price == 2790000
    assert result.location.street == "הרצל 5"
    assert result.location.city == "תל אביב יפו"
    assert result.specs.rooms == 4
    assert result.specs.floor == 5
    assert result.specs.size_sqm == 107
    assert len(result.tags) == 2
    assert not result.is_saved
    assert not result.is_agency
    
    logger.info("Regular listing parsing test completed successfully")

def test_parse_invalid_item(parser):
    logger.info("Testing invalid item parsing")
    
    class MockElement:
        def find_element(self, *_):
            raise Exception("Element not found")
    
    result = parser.parse_item(MockElement())
    assert result is None
    
    logger.info("Invalid item parsing test completed") 