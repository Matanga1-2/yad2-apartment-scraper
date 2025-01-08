from sqlalchemy.orm import Session

from .models import SavedItem


class SavedItemsRepository:
    def __init__(self, session: Session):
        self.session = session
        
    def add_item(self, item_id: str, url: str) -> None:
        item = SavedItem(item_id=item_id, url=url)
        self.session.merge(item)  # merge will update if exists, insert if not
        self.session.commit()
        
    def is_saved(self, item_id: str) -> bool:
        return self.session.query(SavedItem).filter(SavedItem.item_id == item_id).first() is not None
        
    def get_all_items(self):
        return self.session.query(SavedItem).all() 