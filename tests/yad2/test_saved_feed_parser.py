import logging
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

from src.yad2.saved_feed_parser import SavedFeedParser

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def sample_saved_html():
    return """
    <article class="feed-item-grid_box__CPaB4">
        <a class="feed-item-grid_linkOverlay__dyFJC" 
           href="https://www.yad2.co.il/item/abcd123"></a>
    </article>
    """

@pytest.fixture
def parser():
    return SavedFeedParser()

def test_parse_saved_item(driver, sample_saved_html, parser):
    logger.info("Testing saved item parsing")
    
    driver.get("data:text/html;charset=utf-8,{0}".format(sample_saved_html))
    item_element = driver.find_element(By.CSS_SELECTOR, "[class*='feed-item-grid_box']")
    
    result = parser.parse_item(item_element)
    
    assert result is not None
    item_id, url = result
    assert item_id == "abcd123"
    assert url == "https://www.yad2.co.il/item/abcd123"
    
    logger.info("Saved item parsing test completed successfully")

def test_parse_invalid_saved_item(parser):
    logger.info("Testing invalid saved item parsing")
    
    class MockElement:
        def find_element(self, *_):
            raise Exception("Element not found")
    
    result = parser.parse_item(MockElement())
    assert result is None
    
    logger.info("Invalid saved item parsing test completed") 