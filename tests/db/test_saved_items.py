import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.models import Base
from src.db.saved_items_repository import SavedItemsRepository


@pytest.fixture
def db_session():
    """Create a test database in memory"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def repository(db_session):
    return SavedItemsRepository(db_session)

def test_add_item(repository):
    # Given
    item_id = "123"
    url = "https://www.yad2.co.il/item/123"
    
    # When
    repository.add_item(item_id, url)
    
    # Then
    assert repository.is_saved(item_id)

def test_is_saved_returns_false_for_non_existent_item(repository):
    assert not repository.is_saved("non_existent")

def test_add_duplicate_item(repository):
    # Given
    item_id = "123"
    url1 = "https://www.yad2.co.il/item/123"
    url2 = "https://www.yad2.co.il/item/123?updated"
    
    # When
    repository.add_item(item_id, url1)
    repository.add_item(item_id, url2)
    
    # Then
    saved_items = repository.get_all_items()
    assert len(saved_items) == 1
    assert saved_items[0].url == url2

def test_get_all_items(repository):
    # Given
    items = [
        ("123", "https://www.yad2.co.il/item/123"),
        ("456", "https://www.yad2.co.il/item/456")
    ]
    
    # When
    for item_id, url in items:
        repository.add_item(item_id, url)
    
    # Then
    saved_items = repository.get_all_items()
    assert len(saved_items) == 2
    assert {item.item_id for item in saved_items} == {"123", "456"} 