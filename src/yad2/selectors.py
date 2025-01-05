# Feed container and items
FEED_CONTAINER = '[class*="feed-list_feed_"]'
FEED_ITEM = '[data-nagish="feed-item-list-box"]'
ITEM_LINK = 'a'

# Price related
PRICE_CONTAINER = '[class*="price_price__"]'
AGENCY_CONTAINER = '[class*="price-and-extra_box__"]'
AGENCY_NAME = '[class*="price-and-extra_startFrom__"]'

# Location and details
STREET_NAME = '[class*="item-data-content_heading__"]'
LOCATION_INFO = '[class*="item-data-content_itemInfoLine__"][class*="first__"]'
PROPERTY_SPECS = '[class*="item-data-content_itemInfoLine__"]:not([class*="first__"])'

# Tags and save button
TAGS_CONTAINER = '[class*="item-tags_itemTagsBox__"]'
SAVE_BUTTON = '[class*="like-toggle_likeButton__"]'

# New pagination selectors
PAGINATION_TEXT = 'nav[data-nagish="pagination-navbar"] span:first-of-type'  # The text showing "עמוד X מתוך Y"
PAGINATION_NAV = 'nav[data-nagish="pagination-navbar"]'     # The pagination container
