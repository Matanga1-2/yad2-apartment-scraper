import logging

from src.yad2_client import Yad2Client

logger = logging.getLogger(__name__)


def test_yad2_client_search():
    with Yad2Client(headless=False) as client:
        success = client.open_search_page()
        assert success, "Failed to open search page"


def test_yad2_feed_items():
    with Yad2Client(headless=False) as client:
        client.open_search_page()
        items = client.get_feed_items()
        assert len(items) > 0, "No feed items found"