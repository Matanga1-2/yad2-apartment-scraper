import os

import PyInstaller.__main__


def create_error_handler():
    """Create a wrapper script that handles errors and keeps the window open"""
    wrapper_script = '''
import sys
import traceback
import os
from dotenv import load_dotenv

def main():
    try:
        # Set up paths
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(os.path.dirname(__file__))

        # Create Yad2Scraper directory in user's home if it doesn't exist
        home_dir = os.path.expanduser('~')
        app_dir = os.path.join(home_dir, '.Yad2Scraper')
        credentials_dir = os.path.join(app_dir, 'credentials')
        
        # Ensure directories exist
        os.makedirs(app_dir, exist_ok=True)
        os.makedirs(credentials_dir, exist_ok=True)
        
        # Set up environment variables before anything else
        env_paths = [
            os.path.join(base_path, '.env'),
            os.path.join(os.path.dirname(base_path), '.env'),
            '.env'
        ]
        
        for env_path in env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                break
                
        # Add src to path
        src_path = os.path.join(base_path, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            
        # Handle client_secret.json
        client_secret_src = os.path.join(base_path, 'src', 'mail_sender', 'client_secret.json')
        client_secret_dst = os.path.join(credentials_dir, 'client_secret.json')
        
        if not os.path.exists(client_secret_dst):  # Only copy if destination doesn't exist
            if os.path.exists(client_secret_src):
                import shutil
                shutil.copy2(client_secret_src, client_secret_dst)
            
        # Now import and run the actual main function
        from src.main import main
        sys.exit(main())
    except Exception as e:
        print("\\nAn error occurred:")
        traceback.print_exc()
        print("\\nPress Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # Write the wrapper script
    with open('wrapper.py', 'w') as f:
        f.write(wrapper_script)
    
    return 'wrapper.py'

# Create the error handling wrapper
wrapper_script = create_error_handler()

try:
    PyInstaller.__main__.run([
        wrapper_script,
        '--name=Yad2Scraper',
        '--onefile',
        '--clean',
        
        # Include all data files
        '--add-data=consts/*:consts',
        '--add-data=src/mail_sender/client_secret.json:src/mail_sender',  # Include client_secret.json in the package
        '--add-data=.env:.',
        '--add-data=src:src',
        
        # Include all required modules
        '--collect-all=selenium',
        '--collect-all=webdriver_manager',
        '--collect-all=fuzzywuzzy',
        '--collect-all=google_auth_oauthlib',
        '--collect-all=googleapiclient',
        '--collect-all=python-dotenv',
        
        # Include all your source modules
        '--collect-submodules=src',
        
        # Explicitly import all your packages
        '--hidden-import=address',
        '--hidden-import=address.matcher',
        '--hidden-import=address.utils',
        '--hidden-import=mail_sender',
        '--hidden-import=mail_sender.sender',
        '--hidden-import=mail_sender.init_credentials',
        '--hidden-import=utils',
        '--hidden-import=utils.console',
        '--hidden-import=utils.logging_config',
        '--hidden-import=yad2',
        '--hidden-import=yad2.auth',
        '--hidden-import=yad2.browser',
        '--hidden-import=yad2.client',
        '--hidden-import=yad2.feed_parser',
        '--hidden-import=yad2.item_enricher',
        '--hidden-import=yad2.models',
        '--hidden-import=yad2.selectors',
        
        # Keep console for debugging
        '--console',
    ])
finally:
    # Clean up the temporary wrapper script
    if os.path.exists(wrapper_script):
        os.remove(wrapper_script)