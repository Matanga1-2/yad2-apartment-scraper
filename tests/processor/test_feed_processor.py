from unittest.mock import Mock, call, patch

import pytest

from src.address.matcher import StreetMatch
from src.processor.feed_processor import process_feed_items
from src.yad2.models import FeedItem, Location, PropertySpecs


@pytest.fixture
def mock_prompt_yes_no():
    with patch('src.processor.feed_processor.prompt_yes_no') as mock:
        mock.return_value = False  # Default to "no" for all prompts
        yield mock

@pytest.fixture
def mock_format_hebrew():
    with patch('src.processor.feed_processor.format_hebrew') as mock:
        mock.side_effect = lambda x: x  # Just return the input
        yield mock

def create_test_item(item_id: str, street: str, is_saved: bool = False) -> FeedItem:
    return FeedItem(
        item_id=item_id,
        url=f"https://test.com/{item_id}",
        price=1000000,
        location=Location(city="Test City", street=street),
        specs=PropertySpecs(),
        is_saved=is_saved,
        is_agency=False
    )

def test_process_feed_items_handles_saved_states(mock_prompt_yes_no, mock_format_hebrew):
    # Arrange
    items = [
        create_test_item("1", "Street1", is_saved=True),  # Saved in Yad2
        create_test_item("2", "Street2", is_saved=False), # Saved in DB
        create_test_item("3", "Street3", is_saved=True),  # Saved in both
        create_test_item("4", "Street4", is_saved=False), # Not saved anywhere
    ]
    
    # Mock dependencies
    address_matcher = Mock()
    address_matcher.is_street_allowed.return_value = StreetMatch(True)
    
    client = Mock()
    saved_items_repo = Mock()
    
    # Setup saved_items_repo mock responses
    saved_items_repo.is_saved.side_effect = lambda item_id: {
        "1": False,   # Only in Yad2
        "2": True,    # Only in DB
        "3": True,    # In both
        "4": False,   # Not saved anywhere
    }[item_id]

    # Act
    with patch('src.processor.feed_processor.logging.info'), \
         patch('src.processor.feed_processor.logging.warning'), \
         patch('src.processor.feed_processor.logging.error'), \
         patch('builtins.print'):  # Suppress print statements
        process_feed_items(items, address_matcher, client, saved_items_repo)

    # Assert
    # Item 1 (Only in Yad2) - Should be saved to DB
    assert saved_items_repo.add_item.call_args_list == [
        call("1", "https://test.com/1")
    ]

    # Item 2 (Only in DB) - Should be saved to Yad2
    assert any(call.args[0].item_id == "2" for call in client.save_ad.call_args_list)

    # Item 3 (In both) - Should be skipped
    assert not any(call.args[0].item_id == "3" for call in client.save_ad.call_args_list)
    assert not any(call.args[0] == "3" for call in saved_items_repo.add_item.call_args_list)

    # Item 4 (Not saved anywhere) - Should be processed normally
    assert any(call.args[0].item_id == "4" for call in client.save_ad.call_args_list)

def test_process_feed_items_empty_list(mock_prompt_yes_no, mock_format_hebrew):
    # Arrange
    items = []
    address_matcher = Mock()
    client = Mock()
    saved_items_repo = Mock()

    # Act
    with patch('src.processor.feed_processor.logging.warning'), \
         patch('builtins.print'):  # Suppress print statements
        process_feed_items(items, address_matcher, client, saved_items_repo)

    # Assert
    client.save_ad.assert_not_called()
    saved_items_repo.add_item.assert_not_called()

def test_process_feed_items_handles_exceptions(mock_prompt_yes_no, mock_format_hebrew):
    # Arrange
    items = [create_test_item("1", "Street1")]
    
    address_matcher = Mock()
    address_matcher.is_street_allowed.return_value = StreetMatch(True)
    
    client = Mock()
    client.save_ad.side_effect = Exception("Test error")
    
    saved_items_repo = Mock()
    saved_items_repo.is_saved.return_value = False
    saved_items_repo.add_item.side_effect = Exception("Test error")

    # Act & Assert
    # Should not raise exception
    with patch('src.processor.feed_processor.logging.error'), \
         patch('src.processor.feed_processor.logging.info'), \
         patch('builtins.print'):  # Suppress print statements
        process_feed_items(items, address_matcher, client, saved_items_repo)

@pytest.mark.parametrize("constraint_exists", [True, False])
def test_process_supported_items_with_constraints(mock_prompt_yes_no, mock_format_hebrew, constraint_exists):
    # Arrange
    items = [create_test_item("1", "Street1")]
    
    address_matcher = Mock()
    address_matcher.is_street_allowed.return_value = StreetMatch(
        True, 
        constraint="Some constraint" if constraint_exists else None,
        neighborhood="Test Neighborhood" if constraint_exists else None
    )
    
    client = Mock()
    saved_items_repo = Mock()
    saved_items_repo.is_saved.return_value = False

    # Act
    with patch('src.processor.feed_processor.logging.info'), \
         patch('builtins.print'):  # Suppress print statements
        process_feed_items(items, address_matcher, client, saved_items_repo)

    # Assert
    if constraint_exists:
        assert mock_prompt_yes_no.call_args_list[0] == call("Street has constraints, proceed?")
    client.save_ad.assert_called_once() 