import time
from abc import ABC
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from cpinow import logger


class SeleniumDownloaderMixin(ABC):
    """Provides Selenium-based downloading functionality."""

    def configure_driver(self, download_dir: Path, headless: bool = True) -> webdriver.Firefox:
        """Configures and returns a Firefox WebDriver with download settings."""
        profile = FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", str(download_dir))
        profile.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        profile.set_preference("pdfjs.disabled", True)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.useDownloadDir", True)

        options = Options()
        if headless:
            options.add_argument("--headless")
        options.profile = profile

        return webdriver.Firefox(options=options)

    def switch_to_iframe(self, driver, xpath, timeout=20):
        WebDriverWait(driver, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath)))
        logger.info(f"IFrame {xpath} available.")

    def click_button_ui(self, driver, xpath, timeout=20, description=""):
        button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button.click()
        logger.info(f"Button {description} clicked in the UI.")

    def click_button_js(self, driver, xpath, timeout=20, description=""):
        button = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].click();", button)
        logger.info(f"Button {description} clicked using JS.")

    def wait_for_download(self, download_dir: Path, wait_time: int = 5) -> Path:
        """Waits for file download and returns the downloaded Excel file path."""
        logger.info("Waiting for file to finish downloading...")
        time.sleep(wait_time)
        downloaded_files = list(download_dir.glob("*"))
        logger.info(f"Downloaded files: {downloaded_files}")

        for file in downloaded_files:
            if file.suffix in [".xls", ".xlsx"]:
                logger.info(f"Downloaded file: {file.name}")
                file.rename(download_dir / "colombia.xlsx")
                return file

        logger.warning("No Excel file was downloaded.")
        return None
