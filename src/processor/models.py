from dataclasses import dataclass
from typing import Dict, List

from yad2.models import FeedItem


@dataclass
class CategorizedFeed:
    supported_items: List[FeedItem]
    unsupported_items: List[FeedItem]
    saved_items: List[FeedItem]

    @property
    def stats(self) -> Dict[str, int]:
        return {
            'total': len(self.supported_items) + len(self.unsupported_items) + len(self.saved_items),
            'supported_new': len(self.supported_items),
            'unsupported_new': len(self.unsupported_items),
            'saved': len(self.saved_items)
        } 