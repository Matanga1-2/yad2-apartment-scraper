#!/usr/bin/env python3

import json
import logging
import os
import signal
import sys

from address import AddressMatcher
from app import Yad2ScraperApp
from utils.logging_config import setup_logging
from yad2.client import Yad2Client


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_log_path():
    """Get the appropriate log file path that works both in dev and compiled mode"""
    try:
        if getattr(sys, 'frozen', False):
            app_dir = os.path.join(os.path.expanduser('~'), '.Yad2Scraper')
            if not os.path.exists(app_dir):
                os.makedirs(app_dir)
            return os.path.join(app_dir, 'main.log')
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.log')
    except Exception:
        return 'main.log'

def signal_handler(*_):
    """Handle interrupt signals gracefully."""
    print("\nReceived interrupt signal. Exiting...")
    sys.exit(0)

def main():
    try:
        log_level = os.getenv('DEFAULT_LOG_LEVEL', 'WARNING')
        file_log_level = os.getenv('DEFAULT_FILE_LOG_LEVEL', 'INFO')
        log_file = get_log_path()
        setup_logging(level=getattr(logging, log_level), log_file=log_file, log_file_level=file_log_level)
    except Exception as e:
        print(f"Failed to setup logging: {str(e)}")
        return 1

    try:
        signal.signal(signal.SIGINT, signal_handler)
    except Exception as e:
        logging.error(f"Failed to setup signal handler: {str(e)}")
        return 1
    
    client = None
    try:
        client = Yad2Client(headless=False)
        address_matcher = AddressMatcher(get_resource_path(os.path.join('consts', 'supported_streets.json')))
        search_urls = json.load(open(get_resource_path(os.path.join('consts', 'search_url.json'))))
        
        app = Yad2ScraperApp(client, address_matcher, search_urls)
        app.run()
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"Fatal error: {str(e)}")
        return 1
    finally:
        if client:
            try:
                client.close()
            except Exception as e:
                logging.error(f"Error closing client: {str(e)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 