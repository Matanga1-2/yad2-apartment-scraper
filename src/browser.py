import logging

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _setup_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            file_handler = logging.FileHandler('scraper.log')
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            for handler in [file_handler, console_handler]:
                handler.setFormatter(formatter)
                handler.setLevel(logging.INFO)
                logger.addHandler(handler)

    def init_driver(self) -> webdriver.Chrome:
        try:
            self.logger.info("Initializing Chrome WebDriver")
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless=new')
            options.add_argument('--start-maximized')
            options.add_argument('--window-size=1920,1080')

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            return self.driver

        except WebDriverException as e:
            self.logger.error(f"Browser initialization failed: {str(e)}")
            raise RuntimeError(f"Browser initialization failed: {str(e)}") from e

    def quit(self):
        if self.driver:
            self.logger.info("Closing browser")
            self.driver.quit()
            self.driver = None

    def has_captcha(self) -> bool:
        if self.driver and "g-recaptcha" in self.driver.page_source:
            self.logger.warning("Captcha detected")
            return True
        return False

    def __enter__(self):
        self.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()