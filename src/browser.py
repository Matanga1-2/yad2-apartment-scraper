import logging

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BrowserSetup:
    @staticmethod
    def _setup_logging():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler('scraper.log')
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.logger = logging.getLogger(__name__)
        BrowserSetup._setup_logging()

    def check_for_captcha(self) -> bool:
        """Check if page contains a Captcha challenge"""
        if self.driver and "g-recaptcha" in self.driver.page_source:
            self.logger.warning("Captcha challenge detected")
            return True
        return False

    def init_driver(self) -> webdriver.Chrome:
        try:
            self.logger.info("Initializing Chrome WebDriver")
            options = webdriver.ChromeOptions()
            if self.headless:
                self.logger.info("Running in headless mode")
                options.add_argument('--headless=new')
            options.add_argument('--start-maximized')
            options.add_argument('--window-size=1920,1080')

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)

            self.logger.info("WebDriver initialized successfully")
            return self.driver

        except WebDriverException as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            raise RuntimeError(f"Failed to initialize browser: {str(e)}") from e

    def quit(self):
        if self.driver:
            self.logger.info("Closing browser")
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()