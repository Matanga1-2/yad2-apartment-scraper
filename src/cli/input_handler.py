import logging
from typing import Optional
from urllib.parse import urlparse


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

def display_feed_stats(total_items: int, saved_items: int):
    """Display statistics about feed items."""
    new_items = total_items - saved_items
    logging.info(f"Found {total_items} items ({new_items} new, {saved_items} saved)")
    print(f"\nFound {total_items} items:")
    print(f"  • {new_items} new listings")
    print(f"  • {saved_items} saved listings (will be skipped)") 