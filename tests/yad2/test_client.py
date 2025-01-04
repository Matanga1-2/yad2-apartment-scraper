from unittest.mock import Mock, patch

import pytest
from selenium.webdriver.common.by import By

from src.yad2.client import Yad2Client
from src.yad2.models import FeedItem, Location, PropertySpecs
from src.yad2.selectors import FEED_CONTAINER


@pytest.fixture
def mock_browser_class():
    with patch('src.yad2.client.Browser') as mock:
        yield mock

@pytest.fixture
def mock_parser():
    with patch('src.yad2.client.FeedParser') as mock:
        parser_instance = Mock()
        mock.return_value = parser_instance
        yield parser_instance

@pytest.fixture
def mock_auth():
    with patch('src.yad2.auth.Auth') as mock:
        auth_instance = Mock()
        mock.return_value = auth_instance
        yield auth_instance

@pytest.fixture
def sample_url():
    return "https://www.yad2.co.il/realestate/forsale/test-search"

def test_client_initialization(mock_browser_class, mock_auth, _):
    """Test that Yad2Client initializes with default settings"""
    # Create client with default settings
    client = Yad2Client()
    
    # Verify Browser class was instantiated with default headless=True
    mock_browser_class.assert_called_once_with(headless=True)
    
    # Verify client has the correct base URLs
    assert client.BASE_URL == "https://www.yad2.co.il"
    assert client.REALESTATE_URL == "https://www.yad2.co.il/realestate/forsale"

    # Test with explicit headless=False
    Yad2Client(headless=False)
    mock_browser_class.assert_called_with(headless=False)

def test_open_search_page_success(mock_browser_class, mock_auth, _):
    """Test successful opening of search page"""
    # Setup browser mock behavior
    browser_instance = Mock()
    browser_instance.has_captcha.return_value = False
    browser_instance.wait_for_element.return_value = True
    mock_browser_class.return_value = browser_instance
    
    # Create client and open search page
    client = Yad2Client()
    result = client.open_search_page()
    
    # Verify the expected calls were made
    browser_instance.driver.get.assert_called_with(client.REALESTATE_URL)
    browser_instance.wait_for_element.assert_called_once_with(
        By.CSS_SELECTOR, 
        "[class^='map-page-layout_searchBox']"
    )
    assert result == True

def test_get_feed_items_success(mock_browser_class, mock_parser, mock_auth, sample_url):
    """Test successful retrieval of feed items"""
    # Setup mock feed items with correct parameters
    mock_feed_item = FeedItem(
        item_id="123456",
        url="https://www.yad2.co.il/item/123456",
        price=2790000,
        location=Location(
            street="הרצל 5",
            neighborhood="עזרא",
            area="הארגזים",
            city="תל אביב יפו"
        ),
        specs=PropertySpecs(
            rooms=4,
            floor=5,
            size_sqm=107
        ),
        is_saved=False,
        is_agency=False,
        agency_name=None,
        tags=["נוף לים", "חניה"]
    )
    
    # Setup browser mock behavior
    browser_instance = Mock()
    browser_instance.driver = Mock()
    browser_instance.has_captcha.return_value = False
    mock_feed_container = Mock()
    mock_feed_items = [Mock(), Mock()]  # Two mock feed items
    
    browser_instance.driver.find_element.return_value = mock_feed_container
    mock_feed_container.find_elements.return_value = mock_feed_items
    mock_browser_class.return_value = browser_instance
    
    # Setup the mock parser from the fixture to return our feed item
    mock_parser.parse_item.return_value = mock_feed_item
    
    # Create client and get feed items
    client = Yad2Client()
    result = client.get_feed_items(sample_url)
    
    # Verify the expected calls were made
    browser_instance.driver.get.assert_called_with(sample_url)
    browser_instance.wait_for_element.assert_called_with(
        By.CSS_SELECTOR, 
        FEED_CONTAINER,
        timeout=30
    )
    browser_instance.random_delay.assert_called()
    browser_instance.has_captcha.assert_called()
    
    # Verify we got the expected number of items
    assert len(result) == 2
    assert all(isinstance(item, FeedItem) for item in result)
    
    # Verify the first item's content
    first_item = result[0]
    assert first_item.item_id == "123456"
    assert first_item.price == 2790000
    assert first_item.location.street == "הרצל 5"
    assert first_item.location.city == "תל אביב יפו"
    assert first_item.specs.rooms == 4
    assert first_item.specs.size_sqm == 107
    assert "נוף לים" in first_item.tags

def test_get_feed_items_with_captcha(mock_browser_class, mock_parser, mock_auth, sample_url):
    """Test feed items retrieval when captcha is present"""
    browser_instance = Mock()
    browser_instance.driver = Mock()
    browser_instance.has_captcha.return_value = True
    mock_browser_class.return_value = browser_instance
    
    client = Yad2Client()
    result = client.get_feed_items(sample_url)
    
    assert result == []
    browser_instance.has_captcha.assert_called()

def test_get_feed_items_with_error(mock_browser_class, mock_parser, mock_auth, sample_url):
    """Test feed items retrieval when an error occurs"""
    browser_instance = Mock()
    browser_instance.driver = Mock()
    browser_instance.driver.get.side_effect = Exception("Test error")
    mock_browser_class.return_value = browser_instance
    
    client = Yad2Client()
    result = client.get_feed_items(sample_url)
    
    assert result == []
    browser_instance.driver.get.assert_called()
