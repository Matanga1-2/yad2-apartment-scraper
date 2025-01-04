import os
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import logging
from src.utils.console import prompt_yes_no

def _setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(current_dir, 'gmail_auth.log')
        
        handlers = [
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        for handler in handlers:
            handler.setFormatter(formatter)
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)

    return logger

logger = _setup_logging()

def init_gmail_credentials():
    """
    Initialize Gmail API credentials. This script should be run once before using the main application.
    It will:
    1. Check for existing token.pickle and client_secret.json
    2. Start the OAuth2 flow if needed
    3. Save the credentials to token.pickle
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    client_secret_path = os.path.join(current_dir, 'client_secret.json')
    token_path = os.path.join(current_dir, 'token.pickle')
    
    # Check if token.pickle already exists
    if os.path.exists(token_path):
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
        logger.info("5. Download client configuration and save as 'client_secret.json'")
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
    init_gmail_credentials() 