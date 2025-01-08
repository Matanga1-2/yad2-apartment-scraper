import logging

import pytest

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
    items = handler.get_saved_items()
    
    assert len(items) == 2
    assert all(isinstance(item, tuple) for item in items)
    assert items[0][0] == "123"
    assert items[1][0] == "456"
    
    logger.info("Saved items retrieval test completed successfully")

@pytest.fixture
def sample_feed_html():
    return """
    <div class="feed-list_feed_123">
        <div data-nagish="feed-item-list-box">
            <a class="feed-item_link" 
               href="https://www.yad2.co.il/item/123"></a>
            <div class="price_price__xyz">₪ 5,000</div>
            <div class="item-data-content_heading__xyz">רחוב הרצל</div>
            <div class="item-data-content_itemInfoLine__xyz first__xyz">תל אביב, מרכז העיר</div>
            <div class="item-data-content_itemInfoLine__xyz">3 • קומה 2 • 80 מ"ר</div>
            <div data-testid="like-button">
                <div class="like-toggle_likeButton__xyz"></div>
            </div>
            <div class="item-tags_itemTagsBox__xyz">
                <span>מיזוג</span>
                <span>מעלית</span>
            </div>
        </div>
        <div data-nagish="feed-item-list-box">
            <a class="feed-item_link" 
               href="https://www.yad2.co.il/item/456"></a>
            <div class="price_price__xyz">₪ 6,000</div>
            <div class="item-data-content_heading__xyz">רחוב אלנבי</div>
            <div class="item-data-content_itemInfoLine__xyz first__xyz">תל אביב, פלורנטין</div>
            <div class="item-data-content_itemInfoLine__xyz">4 • קומה 3 • 100 מ"ר</div>
            <div data-testid="like-button">
                <div class="like-toggle_likeButton__xyz saved__xyz"></div>
            </div>
            <div class="item-tags_itemTagsBox__xyz">
                <span>חניה</span>
                <span>מרפסת</span>
            </div>
        </div>
    </div>
    """

def test_get_feed_items(browser, handler, sample_feed_html):
    logger.info("Testing feed items retrieval")
    
    browser.inject_html(sample_feed_html)
    items = handler.get_feed_items()
    
    assert len(items) == 2
    assert all(hasattr(item, 'item_id') for item in items)
    
    logger.info("Feed items retrieval test completed successfully") 