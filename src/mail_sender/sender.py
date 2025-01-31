import base64
import logging
import os
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from src.mail_sender.init_credentials import get_credentials_dir, init_gmail_credentials


class EmailSender:
    def __init__(self):
        self.recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",")
        self.cc_recipients = os.getenv("EMAIL_CC_RECIPIENTS", "").split(",")
        
        if not self.recipients:
            logging.error("No recipients specified in EMAIL_RECIPIENTS environment variable")
            raise ValueError("No recipients specified in EMAIL_RECIPIENTS")

        # If modifying these scopes, delete the token.pickle file
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        self.creds = None
        self.initialize_credentials()

    def initialize_credentials(self):
        """Initialize or load credentials for Gmail API using init_credentials logic."""
        # Get the credentials directory
        credentials_dir = get_credentials_dir()
        token_path = os.path.join(credentials_dir, 'token.pickle')

        # Initialize credentials using the init_credentials function
        if not os.path.exists(token_path):
            logging.warning("No existing credentials found. Will attempt to initialize new credentials...")
            if not init_gmail_credentials():
                logging.error("Failed to initialize Gmail credentials")
                raise RuntimeError("Failed to initialize Gmail credentials.")
        
        # Load the credentials from token.pickle
        try:
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)
        except Exception as err:
            logging.error(f"Failed to load credentials from {token_path}: {str(err)}")
            raise RuntimeError(f"Failed to load Gmail credentials: {str(err)}") from err

    def create_message(self, subject: str, body: str) -> dict:
        """Create a message for an email."""
        message = MIMEMultipart()
        message['to'] = ', '.join(self.recipients)
        if self.cc_recipients:
            message['cc'] = ', '.join(self.cc_recipients)
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send_email(self, subject: str, body: str) -> None:
        """
        Sends an email using Gmail API.
        
        Args:
            subject: Email subject
            body: Email body text
            
        Raises:
            Exception: If email sending fails
        """
        try:
            print("sending email...")
            service = build('gmail', 'v1', credentials=self.creds)
            message = self.create_message(subject, body)
            
            # Send the email
            sent_message = service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            logging.info(f"Email sent successfully: {subject} (Message ID: {sent_message['id']})")
            print("email sent successfully!")

        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}", exc_info=True)
            raise 