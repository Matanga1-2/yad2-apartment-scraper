import logging

import pytest
from selenium.webdriver.common.by import By

from src.yad2.browser import Browser
from src.yad2.feed_handler import FeedHandler
from src.yad2.feed_parser import FeedParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@pytest.fixture
def browser():
    browser = Browser(headless=True)
    browser.init_driver()
    yield browser
    browser.quit()

@pytest.fixture
def handler(browser):
    return FeedHandler(browser, FeedParser())

@pytest.fixture
def sample_saved_feed_html():
    return """
    <div class="category-section-grid_list__veBOu">
        <article class="feed-item-grid_box__CPaB4">
            <a class="feed-item-grid_linkOverlay__dyFJC" 
               href="https://www.yad2.co.il/item/123"></a>
        </article>
        <article class="feed-item-grid_box__CPaB4">
            <a class="feed-item-grid_linkOverlay__dyFJC" 
               href="https://www.yad2.co.il/item/456"></a>
        </article>
    </div>
    """

def test_get_saved_items(browser, handler, sample_saved_feed_html):
    logger.info("Testing saved items retrieval")
    
    browser.inject_html(sample_saved_feed_html)
    items = handler.get_current_page_items()
    
    assert len(items) == 2
    assert all(isinstance(item, tuple) for item in items)
    assert items[0][0] == "123"
    assert items[1][0] == "456"
    
    logger.info("Saved items retrieval test completed successfully")

def test_detect_saved_items_page(browser, handler, sample_saved_feed_html):
    logger.info("Testing page type detection")
    
    browser.inject_html(sample_saved_feed_html)
    items = handler.get_current_page_items()
    
    # Should return tuples for saved items page
    assert all(isinstance(item, tuple) for item in items)
    
    logger.info("Page type detection test completed successfully") 