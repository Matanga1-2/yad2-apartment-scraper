import logging
from typing import Optional
from urllib.parse import urlparse

from processor.models import CategorizedFeed


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

def display_feed_stats(categorized_feed: CategorizedFeed):
    """Display statistics about categorized feed items."""
    stats = categorized_feed.stats
    
    print(f"\nFound {stats['total']} items:")
    print(f"  • {stats['supported_new']} new listings from supported streets")
    print(f"  • {stats['unsupported_new']} new listings from unsupported streets")
    print(f"  • {stats['saved']} saved listings (will be skipped)") 