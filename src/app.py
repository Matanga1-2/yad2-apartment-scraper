import logging

from address import AddressMatcher
from cli.input_handler import display_feed_stats, get_valid_url
from processor.feed_processor import categorize_feed_items, process_feed_items
from utils.console import prompt_yes_no
from utils.text_formatter import format_hebrew
from yad2.client import Yad2Client
from db.database import Database
from db.saved_items_repository import SavedItemsRepository


class Yad2ScraperApp:
    def __init__(self, client: Yad2Client, address_matcher: AddressMatcher):
        self.client = client
        self.address_matcher = address_matcher
        self.feed_items = None
        
        # Initialize database
        self.db = Database()
        self.db.create_tables()
        self.saved_items_repo = SavedItemsRepository(self.db.get_session())

    def run(self) -> None:
        """Run the main application loop."""
        print("Yad2 Apartment Scraper")
        print("=====================")
        
        while True:
            try:
                if not self._process_menu_choice():
                    break
            except Exception as e:
                logging.error(f"Error: {str(e)}", exc_info=True)
                print(f"Error: {format_hebrew(str(e))}")
                if not prompt_yes_no("\nWould you like to continue?"):
                    break

    def _process_menu_choice(self) -> bool:
        """Process user menu choice. Returns False if should exit."""
        print("\nChoose an action:")
        print("1. Enter new URL")
        print("2. Get feed items")
        print("3. Process current feed")
        print("4. Store saved items")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            self._handle_new_url()
        elif choice == '2':
            self._handle_get_feed()
        elif choice == '3':
            self._handle_process_feed()
        elif choice == '4':
            self._handle_store_saved_items()
        elif choice == '5':
            print("Goodbye!")
            return False
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
        
        return True

    def _handle_store_saved_items(self) -> None:
        """Handle storing saved items from Yad2 to local DB."""
        print("\nPlease navigate to your saved items page on Yad2...")
        input("Press Enter when ready...")
        
        items = self.client.get_feed_items()
        if not items:
            print("No items found on the current page")
            return
            
        count = 0
        for item in items:
            try:
                self.saved_items_repo.add_item(item.item_id, item.url)
                count += 1
            except Exception as e:
                logging.error(f"Failed to store item {item.item_id}: {str(e)}")
        
        print(f"\nStored {count} items in the database")

    def _handle_new_url(self) -> None:
        url = get_valid_url()
        if not url:
            logging.info("No URL provided")
            return
            
        logging.info(f"Navigating to URL: {url}")
        print("Navigating to URL...")
        self.client.navigate_to(url)
        self.feed_items = None

    def _handle_get_feed(self) -> None:
        print("Fetching feed items...")
        self.feed_items = self.client.get_feed_items()
        if not self.feed_items:
            logging.warning("No feed items found")
            print("No feed items found")
            return
        
        categorized_feed = categorize_feed_items(self.feed_items, self.address_matcher)
        display_feed_stats(categorized_feed)

    def _handle_process_feed(self) -> None:
        if self.feed_items is None:
            print("No feed items available. Please get feed items first.")
            return
            
        items_to_process = [item for item in self.feed_items if not item.is_saved]
        
        if prompt_yes_no("\nProceed with processing these items?"):
            process_feed_items(items_to_process, self.address_matcher, self.client) 