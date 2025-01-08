import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


def get_db_path():
    """Get the appropriate database file path that works both in dev and compiled mode"""
    try:
        if getattr(sys, 'frozen', False):
            app_dir = os.path.join(os.path.expanduser('~'), '.Yad2Scraper')
            if not os.path.exists(app_dir):
                os.makedirs(app_dir)
            return os.path.join(app_dir, 'yad2scraper.db')
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yad2scraper.db')
    except Exception:
        return 'yad2scraper.db'

class Database:
    def __init__(self):
        db_path = get_db_path()
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(self.engine)
        
    def get_session(self):
        return self.SessionLocal() 