import logging

from src.address import AddressMatcher
from src.cli.input_handler import display_feed_stats, get_valid_url
from src.db.database import Database
from src.db.saved_items_repository import SavedItemsRepository
from src.mail_sender.init_credentials import init_gmail_credentials
from src.processor.feed_processor import categorize_feed_items, process_feed_items
from src.utils.console import prompt_yes_no
from src.utils.text_formatter import format_hebrew
from src.yad2.client import Yad2Client


class Yad2ScraperApp:
    def __init__(self, client: Yad2Client, address_matcher: AddressMatcher, search_urls: dict):
        # Initialize database
        self.db = Database()
        self.db.create_tables()
        self.saved_items_repo = SavedItemsRepository(self.db.get_session())
        
        # Initialize client
        self.client = client
        self.client.saved_items_repo = self.saved_items_repo  # Set the repo on the existing client
        self.address_matcher = address_matcher
        self.search_urls = search_urls
        self.feed_items = None

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
        print("5. Go to all URLs")
        print("6. Refresh Gmail credentials")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            self._handle_new_url()
        elif choice == '2':
            self._handle_get_feed()
        elif choice == '3':
            self._handle_process_feed()
        elif choice == '4':
            self._handle_store_saved_items()
        elif choice == '5':
            self._handle_go_to_all_urls()
        elif choice == '6':
            self._handle_refresh_credentials()
        elif choice == '7':
            print("Goodbye!")
            return False
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")
        
        return True

    def _handle_store_saved_items(self) -> None:
        """Handle storing saved items from Yad2 to local DB."""
        print("\nNavigating to saved items page...")
        if not self.client.navigate_to_saved_items():
            print("Failed to navigate to saved items page")
            return
        
        items = self.client.get_saved_items()
        if not items:
            print("No items found on the saved items page")
            return
        
        count = 0
        for item_id, url in items:  # Now we know items are tuples
            try:
                self.saved_items_repo.add_item(item_id, url)
                count += 1
            except Exception as e:
                logging.error(f"Failed to store item {item_id}: {str(e)}")
        
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


    def _handle_go_to_all_urls(self) -> None:
        self._handle_store_saved_items()
        for name, url in self.search_urls.items():
            print(f"Navigating to URL {name}...")
            self.client.navigate_to(url)
            self._handle_get_feed()
            self._handle_process_feed()
        print("Done going through all URLs!")
        return False

    def _handle_get_feed(self) -> None:
        print("Fetching feed items...")
        self.feed_items = self.client.get_feed_items()
        if not self.feed_items:
            logging.warning("No feed items found")
            print("No feed items found")
            return
        
        # Update is_saved flag based on DB state
        for item in self.feed_items:
            if self.saved_items_repo.is_saved(item.item_id):
                item.is_saved = True
        
        categorized_feed = categorize_feed_items(self.feed_items, self.address_matcher)
        display_feed_stats(categorized_feed)

    def _handle_process_feed(self) -> None:
        if self.feed_items is None:
            print("No feed items available. Please get feed items first.")
            return
            
        items_to_process = [item for item in self.feed_items if not item.is_saved]
        process_feed_items(items_to_process, self.address_matcher, self.client, self.saved_items_repo)

    def _handle_refresh_credentials(self) -> None:
        """Handle refreshing Gmail credentials."""
        print("\nRefreshing Gmail credentials...")
        force_new = prompt_yes_no("Do you want to force creation of new credentials?")
        
        try:
            success = init_gmail_credentials(force_new=force_new)
            if success:
                print("Successfully refreshed Gmail credentials!")
            else:
                print("Failed to refresh Gmail credentials. Check the logs for more details.")
        except Exception as e:
            logging.error(f"Failed to refresh credentials: {str(e)}", exc_info=True)
            print(f"Failed to refresh credentials: {str(e)}") 