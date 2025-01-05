import logging
from typing import List

from address import AddressMatcher
from utils.console import prompt_yes_no
from yad2.client import Yad2Client
from yad2.models import FeedItem

from .feed_categorizer import categorize_feed_items


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
    """Process feed items in order: supported streets first, then unsupported."""
    categorized = categorize_feed_items(items, address_matcher)
    
    if not items:
        logging.warning("No items to process")
        return

    # Process supported items first (including those with constraints)
    if categorized.supported_items:
        print("\nProcessing supported streets...")
        for idx, item in enumerate(categorized.supported_items, 1):
            print(f"\nSupported Item {idx}/{len(categorized.supported_items)}")
            match = address_matcher.is_street_allowed(item.location.street, item.location.city)
            
            if match.constraint:
                print(f"Street: {item.location.street} ({match.neighborhood})")
                print(f"Constraint: {match.constraint}")
            else:
                print(f"Street: {item.location.street}")
                
            print(f"Item link: {item.url}")
            
            if match.constraint:
                if prompt_yes_no("Street has constraints, proceed?"):
                    process_item(item, client)
                else:
                    print("Skipping...")
                    continue
            else:
                process_item(item, client)

    # Then process unsupported items
    if categorized.unsupported_items:
        print("\nProcessing unsupported streets...")
        for idx, item in enumerate(categorized.unsupported_items, 1):
            print(f"\nUnsupported Item {idx}/{len(categorized.unsupported_items)}")
            print(f"Street: {item.location.street}")
            print(f"Item link: {item.url}")
            if not prompt_yes_no("Street isn't supported, skip?"):
                process_item(item, client)
            else:
                print("Skipping...") 