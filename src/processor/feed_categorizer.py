from typing import List

from address import AddressMatcher
from yad2.models import FeedItem

from .models import CategorizedFeed


def categorize_feed_items(items: List[FeedItem], address_matcher: AddressMatcher) -> CategorizedFeed:
    """Categorize feed items into supported, unsupported and saved items."""
    supported = []
    unsupported = []
    saved = []
    
    for item in items:
        if item.is_saved:
            saved.append(item)
            continue
            
        street = item.location.street
        match = address_matcher.is_street_allowed(street, item.location.city)
        
        if match.is_allowed:  # Both regular supported and with constraints
            supported.append(item)
        else:
            unsupported.append(item)
    
    return CategorizedFeed(
        supported_items=supported,
        unsupported_items=unsupported,
        saved_items=saved
    ) 