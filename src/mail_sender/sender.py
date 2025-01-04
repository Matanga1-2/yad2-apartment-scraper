import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from src.mail_sender.init_credentials import init_gmail_credentials

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
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(current_dir, 'token.pickle')

        # Initialize credentials using the init_credentials function
        if not os.path.exists(token_path):
            logging.warning("No existing credentials found. Will attempt to initialize new credentials...")
            if not init_gmail_credentials():
                logging.error("Failed to initialize Gmail credentials")
                raise RuntimeError("Failed to initialize Gmail credentials.")
        
        # Load the credentials from token.pickle
        with open(token_path, 'rb') as token:
            self.creds = pickle.load(token)

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