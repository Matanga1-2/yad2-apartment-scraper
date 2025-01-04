import logging
from src.yad2.models import FeedItem, Location, PropertySpecs

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

def test_feed_item_creation():
    logger.info("Testing FeedItem creation")
    
    location = Location(
        street="Test Street",
        neighborhood="Test Neighborhood",
        area="Test Area",
        city="Test City"
    )
    
    specs = PropertySpecs(
        rooms=3,
        floor=2,
        size_sqm=100
    )
    
    item = FeedItem(
        item_id="123",
        url="https://example.com",
        price=1000000,
        location=location,
        specs=specs,
        is_saved=False,
        is_agency=False,
        agency_name=None,
        tags=["tag1", "tag2"]
    )
    
    assert item.item_id == "123"
    assert item.price == 1000000
    assert item.location.street == "Test Street"
    assert item.specs.rooms == 3
    assert len(item.tags) == 2
    
    logger.info("FeedItem creation test completed successfully") 