import logging
from typing import List

from src.address import AddressMatcher
from src.db.saved_items_repository import SavedItemsRepository
from src.utils.console import prompt_yes_no
from src.utils.text_formatter import format_hebrew
from src.yad2.client import Yad2Client
from src.yad2.models import FeedItem

from .feed_categorizer import categorize_feed_items


def process_item(item: FeedItem, client: Yad2Client) -> None:
    """Process a single feed item."""
    try:
        # 1. First approval
        if not prompt_yes_no("Do you approve to send?"):
            logging.info(f"Rejected item: {item.url}")
        else:
            # 2. Enrich item
            enriched_item = client.enrich_feed_item(item)

            # 3. Check last floor
            if item.specs.features.current_floor == item.specs.features.total_floors:
                print("Last floor is not recommended")
                logging.info(f"Rejected item: {item.url}")
            else:
                # 4. Show formatted listing and get format approval
                print("\nFormatted listing:")
                print(format_hebrew(enriched_item.format_listing()))
                logging.info(f"Approved and enriched item: {item.url}")
                
                # 5. Format approval and send
                if prompt_yes_no("Do you approve the format?"):
                    client.send_feed_item(enriched_item)
                else:
                    logging.info(f"Skipped sending item: {item.url}")

    except Exception as e:
        logging.error(f"Failed to enrich item {item.url}: {str(e)}")
        print(f"Error: Failed to enrich item: {str(e)}")
    finally:
        # Always try to save the ad at the end, regardless of what happened
        try:
            client.save_ad(item)
        except Exception as e:
            logging.error(f"Failed to save ad {item.url}: {str(e)}")
            print(f"Error: Failed to save ad: {str(e)}")

def process_feed_items(
    items: List[FeedItem], 
    address_matcher: AddressMatcher, 
    client: Yad2Client,
    saved_items_repo: SavedItemsRepository
) -> None:
    """Process feed items in order: supported streets first, then unsupported."""
    if not items:
        logging.warning("No items to process")
        return

    def handle_saved_state(item: FeedItem) -> bool:
        """
        Handle the saved state of an item. Returns True if item should be skipped.
        """
        try:
            is_saved_locally = saved_items_repo.is_saved(item.item_id)
            is_saved_yad2 = item.is_saved

            if is_saved_locally and is_saved_yad2:
                logging.info(f"Item {item.item_id} already saved in both DB and Yad2 - skipping")
                return True
            elif is_saved_locally and not is_saved_yad2:
                logging.info(f"Item {item.item_id} saved in DB only - saving to Yad2")
                try:
                    client.save_ad(item)
                except Exception as e:
                    logging.error(f"Failed to save ad {item.url} to Yad2: {str(e)}")
                return True
            elif not is_saved_locally and is_saved_yad2:
                logging.info(f"Item {item.item_id} saved in Yad2 only - saving to DB")
                try:
                    saved_items_repo.add_item(item.item_id, item.url)
                except Exception as e:
                    logging.error(f"Failed to save item {item.url} to DB: {str(e)}")
                return True
            
            return False
        except Exception as e:
            logging.error(f"Failed to check saved state for item {item.url}: {str(e)}")
            return False  # Continue with normal processing if we can't check saved state

    # First, handle saved state for all items
    for item in items:
        if handle_saved_state(item):
            continue

    # Then process remaining items
    categorized = categorize_feed_items(items, address_matcher)

    # Process supported items first (including those with constraints)
    if categorized.supported_items:
        print("\nProcessing supported streets...")
        for idx, item in enumerate(categorized.supported_items, 1):
            # Skip if already handled in saved state check
            if item.is_saved:
                continue

            print(f"\nSupported Item {idx}/{len(categorized.supported_items)}")
            match = address_matcher.is_street_allowed(item.location.street, item.location.city)
            
            if match.constraint:
                print(f"Street: {format_hebrew(item.location.street)} ({format_hebrew(match.neighborhood)})")
                print(f"Constraint: {format_hebrew(match.constraint)}")
            else:
                print(f"Street: {format_hebrew(item.location.street)}")
                
            print(f"Item link: {item.url}")
            
            if match.constraint:
                if prompt_yes_no("Street has constraints, proceed?"):
                    process_item(item, client)
                else:
                    print("Skipping...")
                    client.save_ad(item)
                    continue
            else:
                process_item(item, client)

    # Process unsupported items
    if categorized.unsupported_items:
        print("\nProcessing unsupported streets...")
        for idx, item in enumerate(categorized.unsupported_items, 1):
            # Skip if already handled in saved state check
            if item.is_saved:
                continue

            print(f"\nUnsupported Item {idx}/{len(categorized.unsupported_items)}")
            print(f"Street: {format_hebrew(item.location.street)}")
            print(f"Item link: {item.url}")
            if not prompt_yes_no("Street isn't supported, skip?"):
                process_item(item, client)
            else:
                print("Skipping...") 
                client.save_ad(item)