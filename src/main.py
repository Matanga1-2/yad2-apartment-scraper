#!/usr/bin/env python3

import logging
import os
import signal
import sys
from typing import List, Optional
from urllib.parse import urlparse

from utils.logging_config import setup_logging

# Get the directory containing main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (project root)
project_root = os.path.dirname(current_dir)
# Construct path to supported_streets.json
SUPPORTED_STREETS_PATH = os.path.join(project_root, 'consts', 'supported_streets.json')

from address import AddressMatcher
from utils.console import prompt_yes_no
from yad2.client import Yad2Client
from yad2.models import FeedItem


def validate_yad2_url(url: str) -> bool:
    """Validate that the URL is a valid Yad2 URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc == "www.yad2.co.il" and parsed.scheme == "https"
    except Exception as e:
        logging.error(f"Failed to validate URL: {str(e)}")
        return False

def get_valid_url() -> Optional[str]:
    """Prompt user for a valid Yad2 URL."""
    while True:
        try:
            url = input("Enter Yad2 URL (or 'q' to quit): ").strip()
            
            if url.lower() == 'q':
                return None
                
            if validate_yad2_url(url):
                return url
            else:
                print("Error: Please enter a valid Yad2 URL (https://www.yad2.co.il/...)")
        except EOFError:
            logging.warning("User terminated input with EOF")
            return None

def signal_handler(*_):
    """Handle interrupt signals gracefully."""
    print("\nReceived interrupt signal. Exiting...")
    sys.exit(0)

def process_item(item: FeedItem, client: Yad2Client) -> None:
    """Process a single feed item."""
    print(f"\nItem link: {item.url}")
    if prompt_yes_no("Do you approve to send?"):
        try:
            # Enrich the item with additional details
            enriched_item = client.enrich_feed_item(item)
            # Print the formatted listing
            print("\nFormatted listing:")
            print(enriched_item.format_listing()[::-1])
            logging.info(f"Approved and enriched item: {item.url}")
            if prompt_yes_no("Do you approve the format?"):
                client.send_feed_item(enriched_item)
            else:
                logging.info(f"Skipped sending item: {item.url}")
        except Exception as e:
            logging.error(f"Failed to enrich item {item.url}: {str(e)}")
            print(f"Error: Failed to enrich item: {str(e)}")
    else:
        logging.info(f"Rejected item: {item.url}")

def process_feed_items(items: List[FeedItem], address_matcher: AddressMatcher, client: Yad2Client) -> None:
    """Process feed items and prompt user for unsupported streets."""
    logging.info(f"Starting to process {len(items)} items...")
    print(f"\nProcessing {len(items)} items...")
    
    for idx, item in enumerate(items, 1):
        logging.debug(f"Processing item {idx}/{len(items)}")
        if not item:
            logging.warning(f"Empty item found at index {idx}")
            continue
        street = item.location.street
        match = address_matcher.is_street_allowed(street)
        
        if not match.is_allowed:
            print(f"\nItem {idx}/{len(items)}")
            logging.info(f"Street not supported: {street[::-1]}")
            if not prompt_yes_no(f"Street {street[::-1]} isn't supported, skip?"):
                logging.info(f"Processing unsupported street: {street[::-1]}")
                process_item(item, client)
            else:
                logging.info(f"Skipped unsupported street: {street[::-1]}")
                print("Skipping...")
                # Save the skipped item
                if client.save_feed_item(item):
                    logging.info(f"Successfully saved skipped item: {item.url}")
                else:
                    logging.error(f"Failed to save skipped item: {item.url}")
                continue
        
        elif match.constraint:
            print(f"\nItem {idx}/{len(items)}")
            print(f"Street: {street[::-1]} ({match.neighborhood[::-1]})")
            print(f"Constraint: {match.constraint[::-1]}")
            logging.info(f"Street with constraints: {street[::-1]} - {match.constraint[::-1]}")
            
            if prompt_yes_no(f"Street {street[::-1]} with constraints, please check. Process?"):
                logging.info(f"Processing street with constraints: {street[::-1]}")
                process_item(item, client)
                # Save the processed item
                if client.save_feed_item(item):
                    logging.info(f"Successfully saved processed item: {item.url}")
                else:
                    logging.error(f"Failed to save processed item: {item.url}")
            else:
                logging.info(f"Skipped street with constraints: {street[::-1]}")
                print("Skipping...")
                continue
        
        else:
            logging.info(f"Processing supported street: {street[::-1]}")
            process_item(item, client)
            # Save the processed item
            if client.save_feed_item(item):
                logging.info(f"Successfully saved processed item: {item.url}")
            else:
                logging.error(f"Failed to save processed item: {item.url}")

def main():
    try:
        # Set up logging using the centralized configuration
        log_level = os.getenv('DEFAULT_LOG_LEVEL', 'WARNING')
        log_file = os.path.join(current_dir, 'main.log')
        setup_logging(
            level=getattr(logging, log_level),
            log_file=log_file
        )
    except Exception as e:
        print(f"Failed to setup logging: {str(e)}")
        return 1

    try:
        # Set up signal handler for clean interrupts
        signal.signal(signal.SIGINT, signal_handler)
    except Exception as e:
        logging.error(f"Failed to setup signal handler: {str(e)}")
        return 1
    
    print("Yad2 Apartment Scraper")
    print("=====================")
    
    try:
        url = get_valid_url()
        if not url:
            logging.info("No URL provided, exiting")
            print("Exiting...")
            return 0
    except Exception as e:
        logging.error(f"Error getting URL: {str(e)}")
        return 1
        
    client = None
    try:
        client = Yad2Client(headless=False)
        address_matcher = AddressMatcher(SUPPORTED_STREETS_PATH)
        logging.debug("Initialized client and address matcher")

        print("Fetching feed items...")
        feed_items = client.get_feed_items(url)
        if not feed_items:
            logging.warning("No feed items found for the given URL")
            return 0
        
        # Calculate statistics
        total_items = len(feed_items)
        saved_items = sum(1 for item in feed_items if item.is_saved)
        new_items = total_items - saved_items
        
        logging.info(f"Found {total_items} items ({new_items} new, {saved_items} saved)")
        print(f"\nFound {total_items} items:")
        print(f"  • {new_items} new listings")
        print(f"  • {saved_items} saved listings (will be skipped)")
        
        # Filter out saved items before processing
        items_to_process = [item for item in feed_items if not item.is_saved]
        
        if prompt_yes_no("\nProceed with processing these items?"):
            process_feed_items(items_to_process, address_matcher, client)
        else:
            logging.info("User chose not to process items")
        
        return 0
        
    except Exception as e:
        logging.error(f"Fatal error in main: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1
    
    finally:
        if client:
            try:
                client.close()
            except Exception as e:
                logging.error(f"Error closing client: {str(e)}")

if __name__ == "__main__":
    sys.exit(main()) 