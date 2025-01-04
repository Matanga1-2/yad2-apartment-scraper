import logging
import os

from selenium.webdriver.common.by import By

from .browser import Browser


class Yad2Auth:
    LOGIN_URL = "https://www.yad2.co.il/auth/login"

    def __init__(self, browser: Browser):
        self.browser = browser
        self.logger = logging.getLogger(__name__)

    def login(self) -> bool:
        try:

            if not os.getenv('YAD2_EMAIL') or not os.getenv('YAD2_PASSWORD'):
                self.logger.error("Missing YAD2_EMAIL or YAD2_PASSWORD environment variables")
                return False 
            
            self.logger.info("Attempting to login to Yad2")  
            print("login to Yad2...")      
            if not self.browser.driver:
                self.logger.error("Browser driver not initialized")
                return False
            self.browser.driver.get(self.LOGIN_URL)
            
            # Wait and fill email
            email_input = self.browser.wait_for_element(By.ID, "email")
            self.browser.random_delay(1.0, 2.0)
            email_input.send_keys(os.getenv('YAD2_EMAIL'))
            
            # Wait and fill password
            password_input = self.browser.wait_for_element(By.ID, "password")
            self.browser.random_delay(1.0, 2.0)
            password_input.send_keys(os.getenv('YAD2_PASSWORD'))
            
            # Click submit button
            submit_button = self.browser.wait_for_clickable(By.CSS_SELECTOR, "[data-testid='submit']")
            self.browser.random_delay(1.0, 2.0)
            self.browser.safe_click(submit_button)
            
            # Add a small delay to allow for redirect
            self.browser.random_delay(8.0, 12.0)
            
            # Check if we're still on the login page (indicating failure)
            if "/auth/login" in self.browser.driver.current_url:
                self.logger.error("Login failed - still on login page")
                return False
                
            self.logger.info("Successfully logged in to Yad2")
            print("Login successful!")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            print("Login failed!!")
            return False 