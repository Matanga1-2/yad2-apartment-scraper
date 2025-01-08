import logging
from unittest.mock import MagicMock

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from src.yad2.browser import Browser
from src.yad2.navigation import NavigationHandler
from src.yad2.selectors import SAVED_ITEMS_CONTAINER

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@pytest.fixture
def mock_browser():
    browser = MagicMock(spec=Browser)
    browser.driver = MagicMock()
    return browser

@pytest.fixture
def navigation(mock_browser):
    return NavigationHandler(mock_browser)

def test_handle_feed_page_success(navigation, mock_browser):
    """Test successful navigation to feed page."""
    # Setup
    mock_browser.wait_for_element.side_effect = [
        MagicMock(),  # Feed container
        MagicMock(is_displayed=lambda: True)  # Favorites badge
    ]
    
    # Execute
    result = navigation._handle_feed_page()
    
    # Verify
    assert result is True
    assert mock_browser.wait_for_element.call_count == 2

def test_handle_feed_page_no_container(navigation, mock_browser):
    """Test navigation to feed page when container is not found."""
    # Setup
    mock_browser.wait_for_element.side_effect = TimeoutException()
    
    # Execute
    result = navigation._handle_feed_page()
    
    # Verify
    assert result is False

def test_handle_saved_items_success(navigation, mock_browser):
    """Test successful navigation to saved items page."""
    # Setup
    mock_browser.wait_for_element.return_value = MagicMock()
    
    # Execute
    result = navigation._handle_saved_items_page()
    
    # Verify
    assert result is True
    mock_browser.wait_for_element.assert_called_once_with(
        By.CSS_SELECTOR, 
        SAVED_ITEMS_CONTAINER, 
        timeout=30
    )

def test_handle_saved_items_no_container(navigation, mock_browser):
    """Test navigation to saved items page when container is not found."""
    # Setup
    mock_browser.wait_for_element.side_effect = TimeoutException()
    
    # Execute
    result = navigation._handle_saved_items_page()
    
    # Verify
    assert result is False

def test_navigate_to_feed_page(navigation, mock_browser):
    """Test navigation to feed page URL."""
    # Setup
    mock_browser.wait_for_element.side_effect = [
        MagicMock(),  # Feed container
        MagicMock(is_displayed=lambda: True)  # Favorites badge
    ]
    
    # Execute
    result = navigation.navigate_to("https://www.yad2.co.il/realestate/forsale")
    
    # Verify
    assert result is True
    mock_browser.driver.get.assert_called_once()

def test_navigate_to_saved_items(navigation, mock_browser):
    """Test navigation to saved items URL."""
    # Setup
    mock_browser.wait_for_element.return_value = MagicMock()
    
    # Execute
    result = navigation.navigate_to("https://www.yad2.co.il/my-favorites")
    
    # Verify
    assert result is True
    mock_browser.driver.get.assert_called_once()

def test_navigation_error_logging(navigation, mock_browser, caplog):
    """Test error logging during navigation failure."""
    # Setup
    caplog.set_level(logging.ERROR)
    mock_browser.wait_for_element.side_effect = Exception("Test error")
    
    # Execute
    navigation.navigate_to("https://www.yad2.co.il/invalid-page")
    
    # Verify
    assert "Failed to navigate to URL" in caplog.text 