from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SavedItem(Base):
    __tablename__ = 'saved_items'
    
    item_id = Column(String, primary_key=True)
    url = Column(String, nullable=False, unique=True) 