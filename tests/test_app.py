from unittest.mock import MagicMock

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
def app(mock_client, mock_address_matcher):
    return Yad2ScraperApp(mock_client, mock_address_matcher)

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