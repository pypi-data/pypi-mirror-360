# -*- coding: utf-8 -*-
"""Top level package for recursiveseriation"""

import pandas as pd

from cpinow.logger import configure_logging
from cpinow.names import Countries, CPIColumns
from cpinow.settings import init_settings

__app_name__ = "cpinow"
__version__ = "2025.7.8"

SETTINGS = init_settings()
logger = configure_logging(__app_name__ + " - v" + __version__, SETTINGS, kidnap_loggers=True)

DF_CPI = {
    Countries.COLOMBIA.value: pd.read_csv(SETTINGS.COLOMBIA_LOCAL_PATH.as_posix()),
}

for key, item in DF_CPI.items():
    if item[CPIColumns.DATE.value].max() <= pd.to_datetime("today").strftime("%Y-%m-%d"):
        logger.warn(f"The data is not up to date in the {key} country. Please run the update script.")


def update(countries: list = None):
    from cpinow.retrievers import __retrievers__

    if countries is None:
        countries = DF_CPI.keys()
    for retriever in __retrievers__:
        if retriever.country in countries:
            logger.info(f"Updating {retriever.country} data...")
            retriever.launch()
            # replace the dataframe in the DF_CPI dictionary
            DF_CPI[retriever.country] = retriever.data
