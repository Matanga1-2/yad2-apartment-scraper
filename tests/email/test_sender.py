import pytest

from src.mail_sender.sender import EmailSender


@pytest.fixture
def setup_env_vars(monkeypatch):
    """Fixture to set up environment variables for testing."""
    monkeypatch.setenv("EMAIL_RECIPIENTS", "test@example.com")
    monkeypatch.setenv("EMAIL_CC_RECIPIENTS", "test2@example.com")

def test_send_email(setup_env_vars):
    """
    Test sending an email using the EmailSender class.
    
    This test sends a test email to the recipients specified in the
    EMAIL_CC_RECIPIENTS environment variable. Ensure that the Gmail API
    credentials are correctly set up and that the recipient email addresses
    are valid to receive the test email.
    """
    sender = EmailSender()
    subject = "Unit Test Email"
    body = "This is a test email sent from the EmailSender unit test."
    
    try:
        sender.send_email(subject, body)
        print("Test email sent successfully.")
    except Exception as e:
        pytest.fail(f"Sending test email failed: {e}") 