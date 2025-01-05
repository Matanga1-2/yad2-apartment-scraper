import logging
from typing import List

from address import AddressMatcher
from utils.console import prompt_yes_no
from yad2.client import Yad2Client
from yad2.models import FeedItem


def process_item(item: FeedItem, client: Yad2Client) -> None:
    """Process a single feed item."""
    if prompt_yes_no("Do you approve to send?"):
        try:
            enriched_item = client.enrich_feed_item(item)
            print("\nFormatted listing:")
            print(enriched_item.format_listing())
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
        if not item:
            logging.warning(f"Empty item found at index {idx}")
            continue

        print(f"\nItem {idx}/{len(items)}")
        print(f"\nItem link: {item.url}")
        
        if should_process_item(item, address_matcher):
            process_item(item, client)

def should_process_item(item: FeedItem, address_matcher: AddressMatcher) -> bool:
    """Determine if an item should be processed based on its street and constraints."""
    street = item.location.street
    match = address_matcher.is_street_allowed(street, item.location.city)
    
    if not match.is_allowed:
        logging.info(f"Street not supported: {street}")
        should_process = not prompt_yes_no(f"Street {street} isn't supported, skip?")
        if not should_process:
            logging.info(f"Skipped unsupported street: {street}")
            print("Skipping...")
        return should_process
    
    if match.constraint:
        print(f"Street: {street} ({match.neighborhood})")
        print(f"Constraint: {match.constraint}")
        logging.info(f"Street with constraints: {street} - {match.constraint}")
        
        should_process = prompt_yes_no(f"Street {street} with constraints, please check. Process?")
        if not should_process:
            logging.info(f"Skipped street with constraints: {street}")
            print("Skipping...")
        return should_process
    
    print(f"Street {street} is supported")
    logging.info(f"Processing supported street: {street}")
    return True 