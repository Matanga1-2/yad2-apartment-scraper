import logging
import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow

from src.utils.console import prompt_yes_no


def get_credentials_dir():
    """Get the directory where credentials should be stored"""
    home = os.path.expanduser('~')
    credentials_dir = os.path.join(home, '.Yad2Scraper', 'credentials')
    os.makedirs(credentials_dir, exist_ok=True)
    return credentials_dir

def init_gmail_credentials(force_new=False):
    """
    Initialize Gmail API credentials. This script should be run once before using the main application.
    It will:
    1. Check for existing token.pickle and client_secret.json
    2. Start the OAuth2 flow if needed
    3. Save the credentials to token.pickle

    Args:
        force_new (bool): If True, force creation of new credentials regardless of existing ones
    """
    logger = logging.getLogger(__name__)
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    # Get the credentials directory in user's home
    credentials_dir = get_credentials_dir()
    
    # For client_secret.json, first check in the credentials dir, then fall back to package dir
    client_secret_name = 'client_secret.json'
    token_path = os.path.join(credentials_dir, 'token.pickle')
    client_secret_path = os.path.join(credentials_dir, client_secret_name)
    
    if not os.path.exists(client_secret_path):
        # Fall back to checking in the package directory
        package_dir = os.path.dirname(os.path.abspath(__file__))
        package_client_secret = os.path.join(package_dir, client_secret_name)
        if os.path.exists(package_client_secret):
            # Copy to user directory
            import shutil
            shutil.copy2(package_client_secret, client_secret_path)
    
    # Check if token.pickle already exists
    if os.path.exists(token_path) and not force_new:
        logger.info(f"Existing credentials found at {token_path}")
        if not prompt_yes_no("Credentials already exist. Do you want to create new ones?"):
            logger.info("Using existing credentials")
            return True
        logger.info("Proceeding to create new credentials...")
    
    # Check if client_secret.json exists
    if not os.path.exists(client_secret_path):
        logger.error("client_secret.json not found! Please download it from Google Cloud Console")
        logger.info("1. Go to https://console.cloud.google.com")
        logger.info("2. Create a project or select existing one")
        logger.info("3. Enable Gmail API")
        logger.info("4. Create OAuth 2.0 credentials")
        logger.info(f"5. Download client configuration and save as '{client_secret_name}' in {credentials_dir}")
        return False

    try:
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            
        logger.info("Successfully initialized Gmail credentials!")
        logger.info(f"token.pickle has been created at {token_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize credentials: {str(e)}")
        return False

if __name__ == "__main__":
    # Setup basic logging for when script is run directly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    init_gmail_credentials() 