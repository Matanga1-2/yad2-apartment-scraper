import logging

from src.yad2_client import Yad2Client

# Setup logger at module level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Only add handler if none exists to prevent duplicate handlers
if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

def test_yad2_client_search():
    with Yad2Client(headless=False) as client:
        success = client.open_search_page()
        assert success, "Failed to open search page"


def test_yad2_feed_items():
    with Yad2Client(headless=False) as client:
        client.open_search_page()
        items = client.get_feed_items()
        assert len(items) > 0, "No feed items found"