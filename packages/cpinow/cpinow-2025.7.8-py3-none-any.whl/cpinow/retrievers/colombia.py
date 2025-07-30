import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from cpinow import SETTINGS, logger
from cpinow.names import Countries, CPIColumns
from cpinow.retrievers.base import SeleniumDownloaderMixin


class ColombiaCPIRetriever(SeleniumDownloaderMixin):
    """CPI Retriever for Colombia using Selenium automation."""

    def __init__(self):
        self.site = "https://uba.banrep.gov.co/htmlcommons/SeriesHistoricas/precios-inflacion.html"
        self.local_file_path = SETTINGS.COLOMBIA_LOCAL_PATH.parent
        self.attempts = 1
        self.country = Countries.COLOMBIA.value
        self.data = pd.read_csv(SETTINGS.COLOMBIA_LOCAL_PATH.as_posix())

    def launch(self):
        """Launches the retriever."""
        logger.info("Launching Colombia CPI Retriever.")
        error = True

        while error is True and self.attempts > 0:
            path, error = self.download()
            self.attempts -= 1

        if error:
            logger.error("Failed to download CPI file after multiple attempts.")
            logger.info("Using the last downloaded file.")
            return None
        logger.info("CPI file downloaded successfully.")

        self.save(self.parse(f"{path}/colombia.xlsx"), f"{path}/colombia.csv")
        self.data = pd.read_csv(f"{path}/colombia.csv")

    def download(self):
        download_dir = self.local_file_path
        driver = self.configure_driver(download_dir)
        error = False

        try:
            site = self.site
            driver.get(site)

            self.switch_to_iframe(driver, "/html/body/iframe[1]")
            self.click_button_ui(
                driver,
                "//li[@title='Desc_SubCarpetaSerie: IPC total' and .//span[text()='IPC total']]",
                description="selección 'IPC total'",
            )
            self.switch_to_iframe(driver, '//*[@id="__iframe0"]')
            self.click_button_js(
                driver, "//a[@onclick='executeCallJob()' and .//img[@alt='Exportar']]", description="exportación"
            )

            try:
                self.click_button_js(driver, '//*[@id="BotonDescargar"]', description="descarga")
                downloaded_file = self.wait_for_download(download_dir)
            except Exception:
                logger.info("Error message, waiting for additional iframe.")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/form/div/div/div[2]"))
                )
                self.switch_to_iframe(driver, "/html/body/form/div/iframe")
                self.click_button_js(driver, '//*[@id="BotonDescargar"]', description="descarga (tras error)")
                error = True

            if not error:
                logger.info(f"Downloaded CPI file saved at {downloaded_file}")
            else:
                logger.warning("Corrupted file, didn't download the file")

        finally:
            driver.quit()

        return download_dir, error

    def parse(self, file_path):
        """Parses the retrieved CPI file."""

        data = pd.read_excel(file_path, sheet_name="Series de datos", header=None)

        # Search as header the row in which the value is "Fecha"
        header_row = data[data.iloc[:, 0] == "Fecha"]

        # Erase all the values before the header row including the header row itself
        if not header_row.empty:
            header_row_index = header_row.index[0]
            data = data.iloc[(header_row_index + 1) :].reset_index(drop=True)
        else:
            raise ValueError("Header row with 'Fecha' not found in the data.")

        # Rename the first column of data to "date" and the second to "cpi"
        data.columns = [CPIColumns.DATE.value, CPIColumns.CPI.value]

        # Erase the last row
        data = data.iloc[:-1].reset_index(drop=True)

        # Obtain the reference date
        data[CPIColumns.REFERENCE_DATE.value] = (
            data[CPIColumns.DATE.value].where(data[CPIColumns.CPI.value] == 100.0).ffill().bfill()
        )

        # Change the date column and reference date column to be the first day of the respectives months
        data[CPIColumns.DATE.value] = pd.to_datetime(data[CPIColumns.DATE.value], format="%Y-%m")
        data[CPIColumns.DATE.value] = data[CPIColumns.DATE.value].apply(lambda x: x.replace(day=1))
        data[CPIColumns.REFERENCE_DATE.value] = pd.to_datetime(
            data[CPIColumns.REFERENCE_DATE.value], format="%Y-%m"
        )
        data[CPIColumns.REFERENCE_DATE.value] = data[CPIColumns.REFERENCE_DATE.value].apply(
            lambda x: x.replace(day=1)
        )

        return data

    def save(self, data, file_path):
        """Saves parsed data to CSV."""
        data.to_csv(file_path, index=False)
        logger.info(f"Data saved to {file_path}")
        return file_path


if __name__ == "__main__":
    retriever = ColombiaCPIRetriever()
    # retriever.launch()
    path = SETTINGS.COLOMBIA_LOCAL_PATH.parent.as_posix()
    retriever.save(retriever.parse(f"{path}/colombia.xlsx"), f"{path}/colombia.csv")
