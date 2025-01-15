from unittest.mock import MagicMock, patch
import json

import pytest

from src.address import AddressMatcher
from src.app import Yad2ScraperApp
from src.yad2.client import Yad2Client


@pytest.fixture
def mock_client():
    client = MagicMock(spec=Yad2Client)
    client.get_saved_items = MagicMock(return_value=[])
    return client

@pytest.fixture
def mock_address_matcher():
    return MagicMock(spec=AddressMatcher)

@pytest.fixture
def mock_search_urls():
    """Mock the search URLs loaded from search_url.json."""
    return {
        "petach_tikva_1": "https://www.yad2.co.il/realestate/forsale?multiNeighborhood=2001002%2C763%2C765%2C756%2C2001001&propertyGroup=apartments&property=1&rooms=3-4&price=2300000-2600000&floor=1--1&parking=1&elevator=1&balcony=1&shelter=1",
        "petach_tikva_2": "https://www.yad2.co.il/realestate/forsale?multiNeighborhood=2001002%2C763%2C765%2C756%2C2001001&propertyGroup=apartments&property=1&rooms=3-4&price=2300000-2600000&floor=1--1&parking=1&elevator=1&balcony=1&shelter=1&page=2",
    }

@pytest.fixture
def app(mock_client, mock_address_matcher, mock_search_urls):
    """Create an instance of Yad2ScraperApp with mocked dependencies."""
    return Yad2ScraperApp(mock_client, mock_address_matcher, mock_search_urls)

def test_handle_store_saved_items_success(app, capsys):
    """Test successful storing of saved items."""
    # Setup
    app.client.navigate_to_saved_items.return_value = True
    app.client.get_saved_items.return_value = [
        ("123", "https://www.yad2.co.il/item/123"),
        ("456", "https://www.yad2.co.il/item/456")
    ]
    
    # Execute
    app._handle_store_saved_items()
    
    # Verify
    captured = capsys.readouterr()
    assert "Stored 2 items in the database" in captured.out
    app.client.navigate_to_saved_items.assert_called_once()
    app.client.get_saved_items.assert_called_once()

def test_handle_store_saved_items_navigation_failed(app, capsys):
    """Test handling of navigation failure."""
    # Setup
    app.client.navigate_to_saved_items.return_value = False
    
    # Execute
    app._handle_store_saved_items()
    
    # Verify
    captured = capsys.readouterr()
    assert "Failed to navigate to saved items page" in captured.out
    app.client.get_saved_items.assert_not_called()