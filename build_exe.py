import PyInstaller.__main__
import os

# Get the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'src/main.py',  # Your main script
    '--onefile',    # Create a single executable
    '--name=Yad2Scraper',  # Name of your executable
    '--add-data=consts/supported_streets.json:consts',  # Include your JSON file
    '--add-data=src/mail_sender/client_secret.json:src/mail_sender',  # Include Gmail credentials
    '--add-data=src/mail_sender/token.pickle:src/mail_sender',  # Include Gmail token if it exists
    '--paths=src',  # Add the src directory to Python path
    # Hidden imports for all your modules
    '--hidden-import=address',
    '--hidden-import=address.matcher',
    '--hidden-import=address.utils',
    '--hidden-import=utils.console',
    '--hidden-import=utils.logging_config',
    '--hidden-import=mail_sender',
    '--hidden-import=mail_sender.init_credentials',
    '--hidden-import=mail_sender.sender',
    '--hidden-import=yad2',
    '--hidden-import=yad2.auth',
    '--hidden-import=yad2.browser',
    '--hidden-import=yad2.client',
    '--hidden-import=yad2.feed_parser',
    '--hidden-import=yad2.item_enricher',
    '--hidden-import=yad2.models',
    '--hidden-import=yad2.selectors',
    # Additional dependencies
    '--hidden-import=selenium',
    '--hidden-import=fuzzywuzzy',
    '--hidden-import=dotenv',
    '--hidden-import=google.auth',
    '--hidden-import=google_auth_oauthlib',
    '--hidden-import=googleapiclient',
    '--console',  # Show console for debugging
]) 